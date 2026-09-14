# 版本流水號: r4 (2026-09-14) 確認時限改 1 分鐘後,rollback 預設用韌體真正的時限;--short 才用 fwwin 20
# 舊: r3 (2026-09-14) 重開判斷改看開機秒數變小(r2 用連不上判斷仍漏掉一次重開);允許重裝同版本(--prev 可等於 --expect)
# 舊: r2 (2026-09-14) 下載迴圈已看到斷線時,等重開只等回來(r1 會空等 150 秒,期間新韌體可能已退回,結果誤判)
# 舊: r1 (2026-09-14) 初版:板子自己下載更新的實機測試(公開專案要先發布 --expect 的版本)
# ============================================================================
# 階段 install  :檢查更新讀到 --expect → 版本不符/有未儲存變更被擋 → 安裝 → 下載中拒絕起飛與手動輸出 →
#                重開後待確認:版本正確,拒絕起飛,沒有自己倒數 → 確認 → 可以起飛(開始後立刻取消)
# 階段 rollback :檢查更新讀到 --expect → 安裝 → 重開後故意不確認(序列指令 fwwin 縮短時限)→
#                自動退回 --prev,網頁顯示已退回與被退回的版本,事件 25/2
# 不會開網頁(開網頁會自動確認). 設定先備份,結束還原比對.
# 用法: penv python tools/fw_update_test.py install --expect 2026.09.14.2
#       penv python tools/fw_update_test.py rollback --expect 2026.09.14.3 --prev 2026.09.14.2
# ============================================================================
import argparse
import os
import sys
import time

os.environ.setdefault("LP_HOST", "lineplane.local")
import lp_test as T  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("phase", choices=["install", "rollback"])
ap.add_argument("--expect", required=True)
ap.add_argument("--prev")
ap.add_argument("--short", action="store_true", help="rollback 用序列指令把確認時限縮成 20 秒(預設用韌體真正的時限)")
a = ap.parse_args()

T.init(f"fw_update_test_{a.phase}")
T.protect()


def fw():
    return T.get("/api/fw")


def check_until_expect(timeout=420):
    """raw.githubusercontent.com 有約 5 分鐘快取,剛發布時可能還讀到舊 manifest,重試到讀到為止."""
    t0 = time.time()
    last = None
    while time.time() - t0 < timeout:
        r = T.post("/api/fw/check")
        if not r["ok"]:
            return None, r
        for _ in range(40):
            time.sleep(0.5)
            last = fw()
            if last["check"] != 1:
                break
        if last["check"] == 2 and last["rver"] == a.expect:
            return last, time.time() - t0
        T.log(f"  讀到 check={last['check']} rver={last['rver']} err={last['err']},30 秒後重試(快取)")
        time.sleep(30)
    return last, None


def wait_reboot_back(up_before, timeout=150):
    """等板子重開再回來:用開機秒數變小判斷(r2 用「連不上」判斷,輪詢剛好跳過重開那幾秒就漏掉)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            s = T.get("/api/status")
            if s["up"] < up_before:
                return True
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.5)
    return False


def ev25(n0):
    return [e[3] for e in T.events_after(n0) if e[2] == 25]


f0 = fw()
st0 = T.status()
T.log(f"  板子目前 {f0['ver']},待確認 {f0['pending']},手勢 {st0['f']['ge']}")
T.check("開始時沒有更新中,沒有待確認", f0["busy"] == 0 and f0["pending"] == 0, f0)
if a.phase == "rollback":
    T.check(f"(前提)板子目前是 --prev {a.prev}", f0["ver"] == a.prev, f0["ver"])

# ---- 檢查更新 ----
f1, dt = check_until_expect()
T.check(f"檢查更新讀到 {a.expect}(耗時 {dt if dt is None else round(dt)} 秒),說明「{(f1 or {}).get('notes', '')[:30]}」", dt is not None, f1)
if dt is None:
    T.restore_and_verify()
    sys.exit(T.finish())

if a.phase == "install":
    r = T.post("/api/fw/install", ver="9999.0.0.0")
    T.check(f"版本不符不安裝(fwstale):{r}", not r["ok"] and r["code"] == "fwstale", r)
    # 有未儲存變更:擋下(更新會重開機,設定會不見)
    cd = T.get("/api/settings?p=s")["shared"]["countdownSec"]
    T.setp("s", "countdownSec", cd + 1 if cd < 120 else cd - 1)
    r = T.post("/api/fw/install", ver=a.expect)
    T.check(f"有未儲存變更不安裝(fwdirty):{r}", not r["ok"] and r["code"] == "fwdirty", r)
    T.post("/api/revert")
    time.sleep(0.5)
    r = T.post("/api/fw/check")   # fwstale/fwdirty 不改檢查結果,這裡重檢查確保是 CHECKED
    for _ in range(40):
        time.sleep(0.5)
        if fw()["check"] != 1:
            break

# ---- 安裝 ----
n0 = T.ev_total()
r = T.post("/api/fw/install", ver=a.expect)
T.check(f"開始安裝:{r}", r["ok"], r)
t_start = time.time()
seen_busy = rej5 = man_busy = False
max_prog = 0
up_before = T.status()["up"] + 1
while time.time() - t_start < 120:
    try:
        s = T.get("/api/status")
    except Exception:  # noqa: BLE001
        break   # 重開了
    if s["up"] < up_before - 1:
        break   # 已經重開回來
    up_before = s["up"] + 1
    fwst = s["fw"]
    max_prog = max(max_prog, fwst[4])
    if fwst[0] and fwst[3] == 3 and fwst[4] > 5 and not seen_busy:
        seen_busy = True
        if a.phase == "install":
            if s["f"]["ge"]:
                T.post("/api/start")
                time.sleep(0.4)
                s2 = T.status()
                rej5 = s2["f"]["rj"] == 5 and T.fstate(s2) in ("standby", "done")
            else:
                rej5 = None
            rm = T.post("/api/manual", us=s["esc"])
            man_busy = not rm["ok"] and rm["code"] == "busy"
    if fwst[3] == 5:
        T.log("  下載失敗:", fw())
        break
    time.sleep(0.5)
T.check(f"下載中:更新中旗標,進度到 {max_prog}%", seen_busy and max_prog >= 50, (seen_busy, max_prog))
if a.phase == "install":
    T.check("下載中按開始起飛被拒(拒絕原因 5 韌體更新中)" if rej5 is not None else "(手勢關閉,略過開始起飛)", rej5 is not False, rej5)
    T.check("下載中手動輸出被拒(busy)", man_busy)
back = wait_reboot_back(up_before)
T.check(f"安裝完成後板子重開並回來({time.time() - t_start:.0f} 秒)", back)
time.sleep(1)
f2 = fw()
st = T.status()
T.log(f"  重開後:{f2}")
T.check(f"重開後版本是 {a.expect},待確認中(剩 {f2['remain']} 秒)", f2["ver"] == a.expect and f2["pending"] == 1, f2)
T.check("重開後沒有自己倒數(停在待機)", T.fstate(st) in ("arming", "standby"), T.fstate(st))
T.check("狀態列 fw 陣列顯示待確認", st["fw"][1] == 1, st["fw"])

if a.phase == "install":
    T.wait_state("standby", 8)
    if st["f"]["ge"]:
        T.post("/api/start")
        time.sleep(0.4)
        s3 = T.status()
        T.check(f"待確認時按開始起飛被拒(拒絕原因 6):rj={s3['f']['rj']}", s3["f"]["rj"] == 6 and T.fstate(s3) == "standby", s3["f"])
    n1 = T.ev_total()
    ev = [e for e in T.events(0)["ev"] if e[2] == 25]
    T.check(f"事件:新韌體等待確認(25/1)", any(e[3] == 1 for e in ev), ev)
    r = T.post("/api/fw/confirm")
    f3 = fw()
    T.check(f"確認後不再待確認:{r}", r["ok"] and f3["pending"] == 0 and T.status()["fw"][1] == 0, f3)
    T.check("事件:新韌體已確認(25/0)", 0 in ev25(n1), ev25(n1))
    if st["f"]["ge"]:
        time.sleep(1.8)
        r = T.post("/api/start")
        time.sleep(0.5)
        s4 = T.status()
        ok = r["ok"] and T.fstate(s4) in ("wait_still", "countdown")
        T.post("/api/cancel")
        time.sleep(0.5)
        T.check("確認後可以開始起飛程序(立刻取消)", ok and T.fstate() in ("standby", "done"), (r, T.fstate(s4)))
    # 確認過的韌體重開不會再待確認
    T.reboot()
    f4 = fw()
    T.check("確認過的韌體重開後不是待確認,也沒有已退回", f4["pending"] == 0 and f4["rb"] == 0 and f4["ver"] == a.expect, f4)
else:
    if a.short:
        r = T.cmd("fwwin 20", expect="OK")
        T.check(f"序列指令縮短確認時限 20 秒:{r}", "OK" in r, r)
    t_wait = time.time()
    T.log(f"  故意不確認,等自動退回(時限剩 {f2['remain']} 秒)…")
    T.check("沒確認:時限到板子自己重開", wait_reboot_back(T.status()["up"], 150))
    T.log(f"  從開始等到重開回來 {time.time() - t_wait:.0f} 秒")
    time.sleep(1)
    f5 = fw()
    T.log(f"  退回後:{f5}")
    T.check(f"已退回舊版 {a.prev},不是待確認", f5["ver"] == a.prev and f5["pending"] == 0, f5)
    T.check(f"網頁顯示已退回,被退回的版本 {a.expect}", f5["rb"] == 1 and f5["rbver"] == a.expect, f5)
    ev = [e[3] for e in T.events(0)["ev"] if e[2] == 25]
    T.check(f"事件:上次更新沒確認已退回(25/2):{ev}", 2 in ev, ev)
    st = T.wait_state("standby", 8)
    T.check("退回後停在待機,沒有自己倒數", T.fstate(st) == "standby", T.fstate(st))
    T.reboot()
    f6 = fw()
    T.check("再重開一次:已退回提示只出現一次", f6["rb"] == 0 and f6["ver"] == a.prev, f6)

T.restore_and_verify()
sys.exit(T.finish())
