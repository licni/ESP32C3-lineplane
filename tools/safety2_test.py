# 版本流水號: r2 (2026-09-14) 校正旗標時效改用正式 10 秒(不用 calexp)
# 舊: r1 (2026-09-14) 安全審查第二批實測:撞擊後不接受推力手勢,校正旗標時效,油門下限最低 10%,飛行中鎖住 WiFi 寫入
# ============================================================================
# A. 撞擊斷電後:推飛機被拒(原因 9),網頁開始可以;開始/取消之後推飛機恢復有效
# B. 校正旗標:設定旗標 → 5 秒時還在,10 秒後自動取消(事件 26/1);再設定 → 網頁重開機 → 開機取消(事件 26/2)
# C. 下限:設 5% 被拒(range);飛行中補償 -50% 輸出不低於 10%
# D. 起飛程序中:儲存 WiFi,發射功率,保持,檢查更新,校正設定都被拒(locked);
#    發射功率試用中開始倒數 → 計時暫停,不退回(事件 27/1),取消後才照剩餘時間退回;
#    儲存相同的 WiFi 設定並重開 → 設定試用中開始倒數 → 剩餘秒數不減(事件 27/2),取消後按保持
# 需要:手勢開啟;設定先備份,結束還原比對;WiFi 設定只存「和目前完全相同」的值,最後確認沒有試用中.
# ============================================================================
import os
import sys
import time

os.environ.setdefault("LP_HOST", "lineplane.local")
import lp_test as T  # noqa: E402

T.init("safety2_test")
T.protect()   # 送 armsw 1


def fly_setup():
    T.configure(shared={"gestureEnable": 1, "disturbMode": 2, "countdownSec": 5, "crashEnable": 1, "crashG": 14.0},
                profile={"takeoffRamp": 1.0, "noCompSec": 0, "flightSec": 60, "phase1Sec": 30, "phase1Pct": 30,
                         "minPct": 10, "maxPct": 100})
    T.sim("att 0 0")
    time.sleep(2.5)


# ======== A ========
T.log("\n== A. 撞擊斷電後不接受推力手勢 ==")
fly_setup()
T.gesture_push()
st = T.wait_state("flying", 12)
T.check(f"起飛進入飛行({T.fstate(st)})", T.fstate(st) == "flying", st["f"])
T.sim("pulse z 20 15")
st = T.wait_state("done", 2)
T.check(f"撞擊斷電(er=5)", T.fstate(st) == "done" and st["f"]["er"] == 5, st["f"])
time.sleep(1.0)
n0 = T.ev_total()
T.gesture_push()
time.sleep(1.0)
st = T.status()
T.check(f"撞擊後推飛機:停在已結束,拒絕原因 9(rj={st['f']['rj']})", T.fstate(st) == "done" and st["f"]["rj"] == 9, st["f"])
T.check("事件:拒絕原因 9,沒有手勢成立事件", any(e[2] == 4 and e[3] == 9 for e in T.events_after(n0)) and not any(e[2] == 3 for e in T.events_after(n0)),
        T.events_after(n0))
time.sleep(1.8)
r = T.post("/api/start")
st = T.wait_state(("wait_still", "countdown"), 3)
T.check(f"網頁開始起飛程序可以({r['code']},{T.fstate(st)})", r["ok"] and T.fstate(st) in ("wait_still", "countdown"), st["f"])
T.post("/api/cancel")
time.sleep(0.8)
T.gesture_push()
st = T.wait_state(("wait_still", "countdown"), 3)
T.check(f"開始/取消之後推飛機恢復有效({T.fstate(st)})", T.fstate(st) in ("wait_still", "countdown"), st["f"])
T.post("/api/cancel")
time.sleep(0.8)

# ======== B ========
T.log("\n== B. 校正旗標時效 ==")
st0 = T.status()
if st0["proto"] != 0:
    T.log("  協定不是 PWM,略過校正測試")
else:
    # 正式時效 10 秒(GG 2026-09-14,原本 10 分鐘),不用 calexp 縮短
    r = T.post("/api/calib", on=1)
    st = T.status()
    T.check(f"設定校正旗標:{r},剩 {st['cal'][4]} 秒(正式時效 10 秒)", r["ok"] and st["cal"][2] == 1 and 7 <= st["cal"][4] <= 10, st["cal"])
    n0 = T.ev_total()
    time.sleep(5)
    st = T.status()
    T.check(f"5 秒時旗標還在(剩 {st['cal'][4]} 秒)", st["cal"][2] == 1 and 3 <= st["cal"][4] <= 6, st["cal"])
    time.sleep(6.5)
    st = T.status()
    T.check(f"10 秒沒拔電:旗標自動取消(cal={st['cal']})", st["cal"][2] == 0, st["cal"])
    T.check("事件 26/1", any(e[2] == 26 and e[3] == 1 for e in T.events_after(n0)), T.events_after(n0))
    r = T.post("/api/calib", on=1)
    T.check(f"再設定一次:{r}", r["ok"] and T.status()["cal"][2] == 1)
    T.reboot()
    st = T.status()
    ev = [e for e in T.events(0)["ev"] if e[2] == 26]
    T.check(f"網頁重開機(不是拔電):開機時取消旗標(cal={st['cal']}),事件 26/2 {ev}", st["cal"][2] == 0 and any(e[3] == 2 for e in ev), (st["cal"], ev))
    T.post("/api/calib", on=0)
    fly_setup()

# ======== C ========
T.log("\n== C. 油門下限最低 10% ==")
edit = T.get("/api/settings")["edit"]
r = T.post("/api/set", p=edit, k="minPct", v=5)
T.check(f"下限設 5% 被拒:{r}", not r["ok"] and r["code"] == "range", r)
r = T.post("/api/set", p=edit, k="minPct", v=10)
T.check(f"下限設 10% 可以:{r}", r["ok"], r)
meta = T.get("/api/meta")
T.check(f"參數表下限範圍 {meta['profile']['minPct'][:2]}", meta["profile"]["minPct"][0] == 10, meta["profile"]["minPct"])
T.configure(profile={"minPct": 10, "maxPct": 100, "phase1Pct": 30, "noCompSec": 0, "takeoffRamp": 1.0,
                     "dnDb": -5, "dnN": 1, "dn1a": -30, "dn1p": -50})
T.sim("att 0 0")
time.sleep(2.5)
T.gesture_push()
st = T.wait_state("flying", 12)
T.sim("attq -60 0")
time.sleep(3.0)
st = T.status()
T.check(f"機頭朝下 {st['p']:.0f}°,基本 30% 補償 {st['f']['comp']:.0f}%:輸出 {st['f']['out']:.0f}%(不低於 10%)",
        T.fstate(st) == "flying" and st["f"]["comp"] <= -40 and abs(st["f"]["out"] - 10) < 0.6, st["f"])
T.post("/api/estop")
time.sleep(0.8)
T.sim("att 0 0")
time.sleep(2.0)

# ======== D ========
T.log("\n== D. 起飛程序與飛行中鎖住 WiFi 寫入 ==")
T.configure(shared={"gestureEnable": 1, "disturbMode": 2, "countdownSec": 40})
w0 = T.get("/api/wifi")
form = {k: w0[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp")}
form["apsfx"] = w0.get("apsfx", "")
time.sleep(1.8)
T.gesture_push()
st = T.wait_state("countdown", 4)
T.check(f"進入倒數({T.fstate(st)})", T.fstate(st) == "countdown", st["f"])
res = {name: T.post(path, **data) for name, path, data in (
    ("儲存WiFi", "/api/wifi", form), ("發射功率", "/api/txpower", {"txp": w0["txp"]}), ("保持", "/api/wifi/keep", {}),
    ("檢查更新", "/api/fw/check", {}), ("取消校正", "/api/calib", {"on": 0}))}
T.check(f"倒數中全部被拒(locked):{ {k: v['code'] for k, v in res.items()} }", all(not v["ok"] and v["code"] == "locked" for v in res.values()), res)
T.post("/api/cancel")
time.sleep(1.0)

T.log("  發射功率試用中開始倒數:計時暫停")
txp0 = w0["txp"]
txp1 = txp0 + 1 if txp0 < 20 else txp0 - 1
r = T.post("/api/txpower", txp=txp1)
st = T.status()
T.check(f"待機時試用發射功率 {txp1} dBm:{r},剩 {st['wt'][0]} 秒", r["ok"] and st["wt"][3] == txp1 and st["wt"][0] > 12, st["wt"])
time.sleep(1.8)
n0 = T.ev_total()
T.gesture_push()
T.wait_state("countdown", 4)
rem_a = T.status()["wt"][0]
time.sleep(20)
st = T.status()
T.check(f"倒數 20 秒:功率試用剩餘 {rem_a:.0f} → {st['wt'][0]:.0f} 秒(暫停),仍是 {st['wt'][3]} dBm", T.fstate(st) == "countdown" and abs(st["wt"][0] - rem_a) <= 1.5 and st["wt"][3] == txp1, st["wt"])
T.check("事件 27/1", any(e[2] == 27 and e[3] == 1 for e in T.events_after(n0)), T.events_after(n0))
T.post("/api/cancel")
t0 = time.time()
reverted = False
while time.time() - t0 < rem_a + 5:
    time.sleep(1)
    s = T.status()
    if s["wt"][0] == 0 and s["wt"][3] == txp0:
        reverted = True
        break
T.check(f"取消後照剩餘時間退回 {txp0} dBm({time.time() - t0:.0f} 秒,剩 {rem_a:.0f})", reverted and time.time() - t0 >= rem_a - 2, (time.time() - t0, T.status()["wt"]))

T.log("  儲存相同的 WiFi 設定並重開:設定試用中開始倒數,剩餘秒數暫停")
r = T.post("/api/wifi", **form)
T.check(f"儲存和目前相同的 WiFi 設定(試用):{r}", r["ok"], r)
T.reboot()
st = T.status()
t0 = time.time()
while st["wt"][1] and st["wt"][2] < 0 and time.time() - t0 < 30:
    time.sleep(1)
    st = T.status()
T.check(f"重開後設定試用中,剩 {st['wt'][2]} 秒", st["wt"][1] == 1 and st["wt"][2] > 100, st["wt"])
T.sim("att 0 0")
time.sleep(2.5)
n0 = T.ev_total()
T.gesture_push()
T.wait_state("countdown", 4)
rem_b = T.status()["wt"][2]
time.sleep(15)
st = T.status()
T.check(f"倒數 15 秒:設定試用剩餘 {rem_b:.0f} → {st['wt'][2]:.0f} 秒(暫停)", T.fstate(st) == "countdown" and abs(st["wt"][2] - rem_b) <= 1.5, st["wt"])
T.check("事件 27/2", any(e[2] == 27 and e[3] == 2 for e in T.events_after(n0)), T.events_after(n0))
T.post("/api/cancel")
time.sleep(2)
st = T.status()
T.check(f"取消後計時繼續({rem_b:.0f} → {st['wt'][2]:.0f})", st["wt"][2] < rem_b - 1, st["wt"])
r = T.post("/api/wifi/keep")
T.check(f"落地(待機)後按保持:{r}", r["ok"], r)
T.reboot()
st = T.status()
w1 = T.get("/api/wifi")
same = all(w1[k] == w0[k] for k in ("ssid", "host", "tmo", "forceap", "txp")) and w1.get("apsfx", "") == w0.get("apsfx", "")
T.check(f"再重開:沒有設定試用,WiFi 設定與測試前相同", st["wt"][1] == 0 and same, (st["wt"], {k: w1[k] for k in ("ssid", "host", "tmo", "txp")}))

T.restore_and_verify()
sys.exit(T.finish())
