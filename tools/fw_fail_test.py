# 版本流水號: r3 (2026-09-14) 註記:韌體 fw_update r5 起板子只裝「比目前新」的版本(逐段比數字). 測試分支 manifest 的 version
#   若是 test-sha 這種非數字,會被判定比較舊,安裝回 fwnotnewer 而測不到下載失敗;重跑前把測試分支的 version 改成比板子大的數字
#   (例如 9999.01.01.1),下面比對 rver 的地方一起改. 公開韌體專案 2026-09-14 重建後 fwtest 分支已不存在,要重建才能跑 A 段.
# 舊: r2 (2026-09-14) 「沒進入起飛程序」改看開始倒數事件(推力事件本來就先記);無線燒錄推力提早到 3.5 秒,燒錄先自己失敗的那次不算數重測
# 舊: r1 (2026-09-14) 初版:韌體更新失敗情況與寫入途中擋起飛的實機測試(GG:沒實測的兩項都要測)
# ============================================================================
# A. 板子下載失敗(用序列指令 fwurl 暫時改讀公開專案的臨時分支 fwtest,正式來源 main 不受影響):
#    sha    檢查碼故意錯   → 整個下載完才發現,放棄,開機分區不變
#    size   大小故意錯     → 下載前比對檔頭大小就放棄
#    nofile 檔案不存在     → 404
#    cut    正常檔案,下載到一半讓家用 WiFi 真的斷線(stadrop hold)→ 下載中斷
#    每種都驗證:錯誤代碼,不在更新中,版本不變,可以開始起飛;最後重開確認不是待確認,沒有已退回.
# B. 寫入途中推飛機(寫入時 loop 被佔住,序列指令收不到,事先用 sim pulse 延遲參數排好):
#    對照組:沒有寫入時,延遲推力會觸發起飛程序(證明推力有效)
#    網頁上傳截斷的韌體檔:寫入途中推 → 拒絕原因 5;檔案不完整寫入失敗,不重開,事件紀錄留著可以查
#    無線燒錄中途切斷:同上
# 需要:手勢開啟,板子待機且沒有未儲存變更,GPIO 不用接. 設定先備份,結束還原比對.
# ============================================================================
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import uuid

os.environ.setdefault("LP_HOST", "lineplane.local")
import lp_test as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://raw.githubusercontent.com/licni/ESP32lineplane-firmware/fwtest/"
BIN = os.path.join(ROOT, ".pio", "build", "esp32c3_supermini", "firmware.bin")
PY = os.path.join(os.environ["USERPROFILE"], ".platformio", "penv", "Scripts", "python.exe")
ESPOTA = os.path.join(os.environ["USERPROFILE"], ".platformio", "packages", "framework-arduinoespressif32", "tools", "espota.py")

T.init("fw_fail_test")
T.protect()


def fw():
    return T.get("/api/fw")


def wait_check(timeout=20):
    f = fw()
    t0 = time.time()
    while f["check"] == 1 and time.time() - t0 < timeout:
        time.sleep(0.5)
        f = fw()
    return f


def can_start(label):
    """開始起飛程序後立刻取消:驗證失敗後沒有卡在「更新中」."""
    time.sleep(1.8)
    r = T.post("/api/start")
    time.sleep(0.5)
    st = T.status()
    ok = r["ok"] and T.fstate(st) in ("wait_still", "countdown")
    T.post("/api/cancel")
    time.sleep(0.6)
    T.check(f"{label}:之後可以開始起飛程序(立刻取消)", ok and T.fstate() in ("standby", "done"), (r, T.fstate(st)))


def ev_types(n0, types):
    return [(e[2], e[3], round(e[4])) for e in T.events_after(n0) if e[2] in types]


st0 = T.status()
ver0 = fw()["ver"]
T.log(f"  板子 {ver0},手勢 {st0['f']['ge']}")
if not st0["f"]["ge"]:
    sys.exit("手勢要開啟才能測(開始起飛與推飛機)")
T.sim("att 0 0")
time.sleep(2.5)

# ======== A. 下載失敗 ========
for case, want in (("sha", "sha"), ("size", "size"), ("nofile", "nofile")):
    T.log(f"\n== 下載失敗:{case} ==")
    r = T.cmd(f"fwurl {BASE}{case}/", expect="OK")
    T.check(f"序列指令改讀測試分支 {case}:{r}", "OK fw source" in r, r)
    T.post("/api/fw/check")
    f = wait_check()
    T.check(f"檢查更新讀到測試版本 test-{case}", f["check"] == 2 and f["rver"] == f"test-{case}", f)
    n0 = T.ev_total()
    r = T.post("/api/fw/install", ver=f"test-{case}")
    T.check(f"開始安裝:{r}", r["ok"], r)
    t0 = time.time()
    f = fw()
    max_prog = 0
    while f["check"] in (3, 4) and time.time() - t0 < 120:
        max_prog = max(max_prog, f["prog"])
        time.sleep(0.5)
        f = fw()
    T.check(f"安裝失敗,錯誤 {f['err']}(預期 {want}),下載進度最多 {max_prog}%,耗時 {time.time() - t0:.0f} 秒",
            f["check"] == 5 and f["err"] == want, f)
    st = T.status()
    T.check("失敗後不在更新中,版本不變,沒有待確認", st["fw"][0] == 0 and st["fw"][1] == 0 and fw()["ver"] == ver0, st["fw"])
    evs = ev_types(n0, (25,))
    if case == "sha":
        T.check(f"檢查碼錯是整個下載完才發現(進度 {max_prog}%);事件:開始 → 失敗 {evs}", max_prog >= 90 and (25, 3, 2) in evs and (25, 5, 0) in evs, evs)
    else:
        T.check(f"下載前就放棄,沒有開始寫入(沒有開始/失敗事件):{evs}", not evs, evs)
    can_start(case)

T.log("\n== 下載中斷:下載到一半讓家用 WiFi 斷線 ==")
r = T.cmd(f"fwurl {BASE}cut/", expect="OK")
T.post("/api/fw/check")
f = wait_check()
T.check("檢查更新讀到 test-cut", f["check"] == 2 and f["rver"] == "test-cut", f)
T.post("/api/fw/install", ver="test-cut")
t0 = time.time()
prog = 0
while time.time() - t0 < 30:
    f = fw()
    prog = f["prog"]
    if prog >= 15:
        break
    time.sleep(0.3)
r = T.cmd("stadrop hold", expect="OK")
T.check(f"下載到 {prog}% 時讓家用 WiFi 斷線:{r}", "OK" in r and 0 < prog < 90, (prog, r))
line = ""
t0 = time.time()
while time.time() - t0 < 90:
    time.sleep(2)
    line = T.cmd("fw", expect="version=")
    if "check=5" in line or "check=4" in line:
        break
m = re.search(r"busy=(\d) pending=(\d).*check=(\d) err=(\S*)", line)
T.log("  序列埠 fw:", line.splitlines()[-1] if line else "")
T.check(f"斷線後下載失敗(序列埠:check={m and m.group(3)} err={m and m.group(4)}),不在更新中,耗時 {time.time() - t0:.0f} 秒",
        bool(m) and m.group(3) == "5" and m.group(4) in ("short", "timeout", "flashwrite") and m.group(1) == "0", line)
T.cmd("reboot")
time.sleep(4)
T.wait_back(90)
st = T.wait_state("standby", 10)
f = fw()
T.check(f"重開後連回家用 WiFi,版本不變 {f['ver']},不是待確認,沒有已退回", f["ver"] == ver0 and f["pending"] == 0 and f["rb"] == 0, f)
T.check("重開後恢復正式更新來源", f["src"].endswith("/main/"), f["src"])
T.sim("att 0 0")
time.sleep(2.5)
can_start("下載中斷重開後")

# ======== B. 寫入途中推飛機 ========
T.log("\n== 對照組:沒有寫入時,延遲 1.5 秒的推力會觸發起飛程序 ==")
time.sleep(1.8)
T.sim("pulse x 2.5 250 1500")
st = T.wait_state(("wait_still", "countdown"), 5)
ok = T.fstate(st) in ("wait_still", "countdown")
T.post("/api/cancel")
time.sleep(0.6)
T.check(f"延遲推力觸發起飛程序({T.fstate(st)}),已取消", ok and T.fstate() in ("standby", "done"), T.fstate(st))
time.sleep(2.0)

with open(BIN, "rb") as fbin:
    full = fbin.read()
cut = full[:900000]

T.log("\n== 網頁上傳截斷的韌體檔,寫入途中推飛機 ==")
n0 = T.ev_total()
T.sim("pulse x 2.5 250 3000")
boundary = uuid.uuid4().hex
body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"firmware\"; filename=\"firmware.bin\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n").encode() + cut + f"\r\n--{boundary}--\r\n".encode()
req = urllib.request.Request(f"http://{T.HOST}/update", data=body)
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
t0 = time.time()
try:
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())
except urllib.error.HTTPError as e:
    r = json.loads(e.read())
dt = time.time() - t0
T.check(f"截斷檔上傳 {len(cut)} 位元組 {dt:.1f} 秒,推力排在 3 秒(寫入途中),結果寫入失敗:{r}", r.get("code") == "updatefail" and dt > 3.5, (r, dt))
time.sleep(1)
evs = ev_types(n0, (25, 4, 3))
T.log("  事件:", evs)
i_start = evs.index((25, 3, 0)) if (25, 3, 0) in evs else -1
i_rej = next((i for i, e in enumerate(evs) if e[0] == 4 and e[1] == 5), -1)
i_fail = evs.index((25, 5, 0)) if (25, 5, 0) in evs else -1
T.check("事件順序:開始更新(網頁上傳)→ 推飛機被拒(原因 5 韌體更新中)→ 更新失敗", 0 <= i_start < i_rej < i_fail, evs)
# 事件 3「偵測到推力」會先記,再判斷能不能起飛;真正進入起飛程序會有事件 5 開始倒數
T.check("寫入途中沒有進入起飛程序(沒有開始倒數事件)", not any(e[0] == 5 for e in ev_types(n0, (5,))), ev_types(n0, (5,)))
st = T.status()
T.check(f"失敗後不重開,停在待機,不在更新中,版本不變", T.fstate(st) in ("standby", "done") and st["fw"][0] == 0 and fw()["ver"] == ver0, (T.fstate(st), st["fw"]))
can_start("上傳失敗後")

T.log("\n== 無線燒錄中途切斷,寫入途中推飛機 ==")
# espota 開始到板子開始寫入約 2.3 秒(序列埠實測);推力排在 3.5 秒,切斷在 9 秒.
# 燒錄如果在推力之前就自己失敗(WiFi 卡住),推力會正常觸發起飛程序:這次不算數,取消倒數後重測(最多 3 次).
valid = False
for attempt in range(1, 4):
    time.sleep(2.0)
    n0 = T.ev_total()
    T.sim("pulse x 2.5 250 3500")
    p = subprocess.Popen([PY, ESPOTA, "-i", T.HOST, "-p", "3232", "-a", "12345678", "-f", BIN, "-r"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(9)
    p.kill()
    out = p.communicate()[0].decode("utf-8", "replace")
    T.log(f"  第 {attempt} 次 espota 最後輸出:", out.strip().splitlines()[-1][-100:] if out.strip() else "(無)")
    t0 = time.time()
    while time.time() - t0 < 60:   # 板子偵測到斷線後才會回到 loop
        try:
            T.get("/api/status")
            break
        except Exception:  # noqa: BLE001
            time.sleep(1)
    time.sleep(1)
    evs = ev_types(n0, (25, 4, 3, 5))
    T.log("  事件:", evs)
    if any(e[0] == 5 for e in evs):
        T.post("/api/cancel")
        time.sleep(0.6)
    i_start = evs.index((25, 3, 1)) if (25, 3, 1) in evs else -1
    i_push = next((i for i, e in enumerate(evs) if e[0] == 3), -1)
    i_fail = evs.index((25, 5, 0)) if (25, 5, 0) in evs else -1
    if 0 <= i_start < i_push < i_fail:
        valid = True
        break
    T.log(f"  第 {attempt} 次不算數:推力不在寫入途中(開始 {i_start},推力 {i_push},失敗 {i_fail}),重測")
T.check("無線燒錄:推力確實發生在寫入途中(開始更新 → 推力 → 更新失敗)", valid, evs)
i_rej = next((i for i, e in enumerate(evs) if e[0] == 4 and e[1] == 5), -1)
T.check("事件順序:開始更新(無線燒錄)→ 推飛機被拒(原因 5)→ 更新失敗", valid and i_start < i_rej < i_fail, evs)
T.check("寫入途中沒有進入起飛程序(沒有開始倒數事件)", valid and not any(e[0] == 5 for e in evs), evs)
st = T.status()
T.check("中斷後不重開,停在待機,不在更新中,版本不變", T.fstate(st) in ("standby", "done") and st["fw"][0] == 0 and fw()["ver"] == ver0 and st["up"] > 30, (T.fstate(st), st["fw"], st["up"]))
can_start("無線燒錄中斷後")

T.restore_and_verify()
sys.exit(T.finish())
