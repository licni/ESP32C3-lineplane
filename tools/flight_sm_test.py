# 版本流水號: r4 (2026-09-14) 安全開關:序列指令 armsw 1 當作按下(開始與自動倒數重開後)
# 舊: r3 (2026-09-14) 自動倒數段落重開前送 powerontest;新增第 7 段:軟體重開(OTA/網頁重開)不自動倒數
# 舊: r2 (2026-09-13) 開頭解析一次 IP(用 .local 名稱在馬達啟動時會卡 2.7 秒,漏掉緩啟動狀態)
# 舊: r1 (2026-09-13) 飛行狀態機桌上測試(不接馬達):手勢,放穩,倒數,時間軸油門,降落,觸地,拒絕,取消,緊急停止,自動倒數
# ============================================================================
# 板子放在桌上不要動(放穩與「降落觸地靜止」都靠它). 會改寫並儲存設定,結束時全部回預設.
# 用法: python tools/flight_sm_test.py [COM埠] [板子位址]
# ============================================================================
import json
import socket
import sys
import time
import urllib.parse
import urllib.request

import serial

import board_backup

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM20"
# 開頭解析一次 IP,之後都用 IP:Windows 每次請求重新解析 .local 名稱時,實測在馬達啟動那一刻會卡 2.7 秒
# (序列遙測與控制迴圈都沒中斷,改用 IP 就不會),輪詢會整段錯過 2 秒的緩啟動狀態.
HOST = "http://" + socket.gethostbyname(sys.argv[2] if len(sys.argv) > 2 else "lineplane.local")
STATE = ["arming", "standby", "wait_still", "countdown", "takeoff", "flying", "landing", "done"]
passed = failed = 0


def get(path):
    return json.loads(urllib.request.urlopen(HOST + path, timeout=8).read())


def post(path, **d):
    req = urllib.request.Request(HOST + path, data=urllib.parse.urlencode(d).encode())
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  OK  ", name)
    else:
        failed += 1
        print("  FAIL", name, detail)


# 注意:Windows 開啟 COM 埠會切換 DTR/RTS,ESP32-C3 原生 USB 會把它當成重置 → 板子重開機.
# 所以整個測試只開一次,而且開之前先把 DTR/RTS 設成不動作. (r1 第一次跑就是被這個害的:每次送指令板子都重開.)
_ser = None


def gesture():
    # 韌體一次手勢後 1.5 秒內不接受下一次(避免一次推力算兩次),測試要等過這段時間
    time.sleep(1.7)
    serial_cmd("gesture")


def serial_cmd(cmd):
    global _ser
    if _ser is None:
        _ser = serial.Serial()
        _ser.port = PORT
        _ser.baudrate = 115200
        _ser.timeout = 0.2
        _ser.dtr = False
        _ser.rts = False
        _ser.open()
        time.sleep(0.5)
    _ser.reset_input_buffer()
    _ser.write((cmd + "\n").encode())
    time.sleep(0.3)
    return _ser.read(4096).decode("utf-8", "replace").strip()


def status():
    return get("/api/status")


def wait_state(target, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = status()
        if STATE[st["f"]["s"]] == target:
            return st
        time.sleep(0.1)
    return status()


def wait_back():
    for _ in range(60):
        time.sleep(1)
        try:
            return status()
        except Exception:  # noqa: BLE001
            pass
    raise RuntimeError("board did not come back")


def setp(scope, k, v):
    r = post("/api/set", p=scope, k=k, v=v)
    if not r["ok"]:
        raise RuntimeError(f"set {k}={v} failed: {r}")


def expected_base(t, mode, p1=60, p2=80, t1=10, ramp=3):
    if mode == 0:
        return p1 if t < t1 else p2
    if mode == 2:
        return p1 + (p2 - p1) * t / t1 if t < t1 else p2
    if t < t1:
        return p1
    return p1 + (p2 - p1) * min(1.0, (t - t1) / ramp)


def configure(gesture=1, mode=1):
    post("/api/defaults", p="s")
    post("/api/defaults", p=0)
    setp("s", "gestureEnable", gesture)
    setp("s", "countdownSec", 5)
    setp(0, "phase1Sec", 10)   # 先縮第一段,總時間才能縮到 30(第一段必須比總時間短)
    setp(0, "flightSec", 30)
    setp(0, "phase1Pct", 60)
    setp(0, "phase2Pct", 80)
    setp(0, "phaseMode", mode)
    setp(0, "phaseRamp", 3)
    setp(0, "takeoffRamp", 2)
    setp(0, "noCompSec", 3)
    setp(0, "landingRamp", 3)
    setp(0, "landingPct", 30)
    post("/api/select", p=0)
    r = post("/api/save")
    if not r["ok"]:
        raise RuntimeError(f"save failed {r}")


def run_flight(mode, label, until_done=True):
    """已在起飛前:追蹤時間軸,回傳 (樣本, 最後狀態)."""
    samples = []
    t_end = time.time() + 45
    last = None
    while time.time() < t_end:
        st = status()
        f = st["f"]
        samples.append((STATE[f["s"]], f["t"], f["out"], f["base"], f["comp"], st["esc"], f["er"], f["lc"]))
        last = st
        if not until_done or STATE[f["s"]] == "done":
            break
        time.sleep(0.25)
    return samples, last


board_backup.require_idle(HOST.replace("http://", ""))
SNAP = board_backup.backup(HOST.replace("http://", ""))   # 結束時原樣還原,不洗掉 GG 調好的值
serial_cmd("fs")   # 先把序列埠開起來(不重置),之後的測試不會再動到它
serial_cmd("armsw 1")   # 開發板沒接 GPIO21 安全開關,當作按下
print("== 準備:時間縮短的測試風格(倒數 5 秒,第一段 60% 10 秒,第二段 80%,總 30 秒,降落 3 秒到 30%) ==")
configure(gesture=1, mode=1)
time.sleep(1)
st = status()
check("待機或上一趟的結束(都可接受手勢)", STATE[st["f"]["s"]] in ("standby", "done"), st["f"])

# ---- 1. 未儲存變更 → 拒絕啟動 ----
setp(0, "phase2Pct", 81)
gesture()
time.sleep(0.5)
st = status()
check("有未儲存變更時手勢被拒絕(rj=1),停在待機", st["f"]["rj"] == 1 and STATE[st["f"]["s"]] == "standby", st["f"])
post("/api/revert")

# ---- 2. 倒數中取消 ----
gesture()
st = wait_state("countdown", 5)
check("手勢 → 放穩 → 倒數", STATE[st["f"]["s"]] == "countdown", st["f"])
r = post("/api/set", p=0, k="phase1Pct", v=61)
check("倒數中設定鎖定(locked)", not r["ok"] and r["code"] == "locked", r)
post("/api/cancel")
time.sleep(0.4)
st = status()
check("取消倒數回待機,電變 1000µs", STATE[st["f"]["s"]] == "standby" and st["esc"] == 1000, (st["f"], st["esc"]))

# ---- 3. 完整飛行(換段有過渡) ----
post("/api/timing/reset")
gesture()
st = wait_state("wait_still", 3)
check("手勢後進入等待放穩", STATE[st["f"]["s"]] in ("wait_still", "countdown"), st["f"])
st = wait_state("countdown", 5)
cd0 = st["f"]["cd"]
st = wait_state("takeoff", 8)
check(f"倒數 {cd0:.1f} 秒後起飛", STATE[st["f"]["s"]] == "takeoff", st["f"])
samples, last = run_flight(1, "ramp")
bad = []
for (s, t, out, base, comp, esc, er, lc) in samples:
    if s in ("takeoff", "flying"):
        exp = expected_base(t, 1)
        if t < 2:
            exp = exp * t / 2
        else:
            exp = max(30, min(100, exp + comp))
        if abs(out - exp) > 2.5:
            bad.append((s, round(t, 2), out, round(exp, 1)))
    if s in ("takeoff", "flying", "landing") and abs(esc - (1000 + 10 * out)) > 3:
        bad.append(("esc", round(t, 2), out, esc))
check("起飛/換段/第二段油門符合時間軸(誤差 <2.5%),電變脈寬 = 1000 + 10×油門", not bad, bad[:6])
ts = {s: [x for x in samples if x[0] == s] for s in ("takeoff", "flying", "landing")}
check("有經過緩啟動,飛行,降落三個狀態", all(ts[k] for k in ts), {k: len(v) for k, v in ts.items()})
fly = ts["flying"]
p2 = [x for x in fly if x[1] > 14]
check("第二段油門 80%", p2 and all(abs(x[2] - 80) < 2 for x in p2), p2[:3])
land = ts["landing"]
check("降落因為時間到(lc=1),起點約 80% 往 30% 減", land and land[0][7] == 1 and land[0][2] > 60 and min(x[2] for x in land) < 45,
      land[:2] + land[-2:])
f = last["f"]
check("降落後桌上靜止判定觸地(er=2),馬達停,電變 1000µs", STATE[f["s"]] == "done" and f["er"] == 2 and last["esc"] == 1000, (f, last["esc"]))
check(f"飛行時間約 34~36 秒(實際 {f['t']:.1f})", 33 <= f["t"] <= 37, f["t"])
check(f"整趟控制迴圈延遲 {last['late']}ms,最長執行 {last['ex']}us", last["late"] <= 5 and last["ex"] < 4000, (last["late"], last["ex"]))

# ---- 4. 結束後再次手勢可起飛,飛行中緊急停止 ----
gesture()
st = wait_state("takeoff", 12)
st = wait_state("flying", 5)
r = post("/api/set", p="s", k="gestureG", v=2.5)
check("飛行中設定鎖定", not r["ok"] and r["code"] == "locked", r)
check("飛行中 OTA 不允許(ota=0)", st["ota"] == 0, st["ota"])
time.sleep(1)
post("/api/estop")
time.sleep(0.3)
st = status()
check("緊急停止:立即結束(er=6),電變 1000µs", STATE[st["f"]["s"]] == "done" and st["f"]["er"] == 6 and st["esc"] == 1000, (st["f"], st["esc"]))

# ---- 5. 換段方式:直接跳 / 平均分攤 ----
for mode, name in ((0, "直接跳"), (2, "平均分攤")):
    configure(gesture=1, mode=mode)
    gesture()
    wait_state("takeoff", 12)
    got = []
    t_end = time.time() + 16
    while time.time() < t_end:
        f = status()["f"]
        if STATE[f["s"]] == "flying":
            got.append((f["t"], f["out"], f["comp"]))
        time.sleep(0.25)
    post("/api/estop")
    bad = [(round(t, 2), o, round(expected_base(t, mode) + c, 1)) for (t, o, c) in got
           if abs(t - 10) > 0.4 and abs(o - max(30, min(100, expected_base(t, mode) + c))) > 2.5]
    check(f"換段方式「{name}」油門符合時間軸", got and not bad, bad[:5])

# ---- 6. 手勢關閉:上電自動倒數,每次上電只一次 ----
configure(gesture=0, mode=1)
# 韌體 flight r15 起只有真的上電才自動倒數;桌上 USB 供電沒辦法斷電,用 powerontest 讓這次軟體重開算上電
r = serial_cmd("powerontest")
check("序列指令 powerontest 接受", "OK" in r, r)
post("/api/reboot")
time.sleep(3)
wait_back()
serial_cmd("armsw 1")   # 重開後覆寫清掉,再按一次安全開關(沒按會在待機等開關)
st = wait_state("countdown", 10)
check("手勢關閉:上電解鎖後直接倒數", STATE[st["f"]["s"]] == "countdown", st["f"])
st = wait_state("takeoff", 10)
if STATE[st["f"]["s"]] != "takeoff":
    st = status()
check("自動倒數後起飛(緩啟動只有 2 秒,輪到時可能已進入飛行)", STATE[st["f"]["s"]] in ("takeoff", "flying"), st["f"])
time.sleep(1)
post("/api/estop")
time.sleep(0.5)
gesture()
time.sleep(4)
st = status()
check("停止後不會再自己倒數(手勢關閉時模擬手勢也無效)", STATE[st["f"]["s"]] == "done" and st["f"]["au"] == 1, st["f"])

# ---- 7. 手勢關閉,軟體重開(模擬 OTA 更新完或網頁重開機,沒有 powerontest):不自動倒數(GG 2026-09-14) ----
post("/api/reboot")
time.sleep(3)
wait_back()
st = wait_state("standby", 10)
n0 = max(0, st["evn"] - 8)
time.sleep(8)   # 解鎖 3 秒 + 倒數秒數,足夠看出有沒有自己倒數
st = status()
ev = [e for e in get(f"/api/events?since={n0}")["ev"] if e[2] == 2]
check("軟體重開後手勢關閉:停在待機,沒有自己倒數", STATE[st["f"]["s"]] == "standby" and st["f"]["au"] == 1, st["f"])
check(f"解鎖事件標明「這次不是拔電再接電」(arg 3):{ev[-1] if ev else None}", bool(ev) and ev[-1][3] == 3, ev)

print("\n== 收尾:還原測試前的板上設定 ==")
post("/api/defaults", p="s")   # 先讓手勢回到開啟,重開機後才不會自動倒數
post("/api/save")
post("/api/reboot")
time.sleep(3)
wait_back()
st = wait_state("standby", 10)
check("收尾:重開後在待機", STATE[st["f"]["s"]] == "standby" and st["dirty"] == 0, st["f"])
errs = board_backup.restore(HOST.replace("http://", ""), SNAP)
check("還原寫入成功", not errs, errs)
d = board_backup.diff(SNAP, board_backup.backup(HOST.replace("http://", "")))
check("還原後與測試前完全相同", not d, d[:5])
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
