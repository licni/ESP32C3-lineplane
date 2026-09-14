# 版本流水號: r1 (2026-09-13) 全功能測試共用工具:序列埠(只開一次,不重置),HTTP,檢查項目與結果紀錄
# ============================================================================
# 用法:import lp_test as T;T.init("測試名稱");... T.check(...);T.finish()
# 結果同時印在畫面並寫入 test_logs/<名稱>_<時間>.txt(額度中斷時看得到跑到哪).
# ============================================================================
import json
import os
import socket
import sys
import time
import urllib.parse
import urllib.request

import serial

sys.path.insert(0, os.path.dirname(__file__))
import board_backup  # noqa: E402

STATE = ["arming", "standby", "wait_still", "countdown", "takeoff", "flying", "landing", "done"]
PORT = os.environ.get("LP_PORT", "COM20")
HOST = socket.gethostbyname(os.environ.get("LP_HOST", "lineplane.local"))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0
fails = []
_ser = None
_log = None
_name = ""


def init(name):
    global _log, _name
    _name = name
    os.makedirs(os.path.join(ROOT, "test_logs"), exist_ok=True)
    path = os.path.join(ROOT, "test_logs", time.strftime(f"{name}_%Y%m%d_%H%M%S.txt"))
    _log = open(path, "w", encoding="utf-8")
    log(f"== {name} {time.strftime('%Y-%m-%d %H:%M:%S')} host={HOST} port={PORT}")
    return path


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    if _log:
        _log.write(s + "\n")
        _log.flush()


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        log("  OK  ", name)
    else:
        failed += 1
        fails.append(name)
        log("  FAIL", name, detail)
    return cond


def finish():
    log(f"\n== {_name}:通過 {passed},失敗 {failed}")
    for f in fails:
        log("   失敗:", f)
    if _log:
        _log.close()
    return failed


# --- HTTP ---
def get(path):
    return json.loads(urllib.request.urlopen(f"http://{HOST}{path}", timeout=8).read())


def post(path, **d):
    req = urllib.request.Request(f"http://{HOST}{path}", data=urllib.parse.urlencode(d).encode())
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def status():
    for i in range(3):
        try:
            return get("/api/status")
        except Exception:  # noqa: BLE001
            if i == 2:
                raise
            time.sleep(0.3)


def fstate(st=None):
    st = st or status()
    return STATE[st["f"]["s"]]


def wait_state(target, timeout, poll=0.05):
    targets = (target,) if isinstance(target, str) else target
    t0 = time.time()
    st = status()
    while time.time() - t0 < timeout:
        if STATE[st["f"]["s"]] in targets:
            return st
        time.sleep(poll)
        st = status()
    return st


def wait_back(timeout=60):
    t0 = time.time()
    time.sleep(2)
    while time.time() - t0 < timeout:
        try:
            return status()
        except Exception:  # noqa: BLE001
            time.sleep(1)
    raise RuntimeError("board did not come back")


def reboot():
    """感測器故障鎖定到重新上電(GG 2026-09-13),測過故障後要重開機才能繼續. 模擬狀態也會清掉."""
    st = status()
    if fstate(st) in ("wait_still", "countdown"):
        post("/api/cancel")
    elif fstate(st) in ("takeoff", "flying", "landing"):
        post("/api/estop")
    time.sleep(0.4)
    r = post("/api/reboot")
    if not r["ok"]:
        raise RuntimeError(f"reboot refused {r}")
    time.sleep(3)
    wait_back()
    return wait_state("standby", 8)


def setp(scope, k, v):
    r = post("/api/set", p=scope, k=k, v=v)
    if not r["ok"]:
        raise RuntimeError(f"set {scope}.{k}={v} failed: {r}")


def setmany(scope, values):
    body = "\n".join(f"{k}={v}" for k, v in values.items()).encode()
    req = urllib.request.Request(f"http://{HOST}/api/setmany?p={scope}", data=body)
    req.add_header("Content-Type", "text/plain")
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        r = json.loads(e.read())
    if not r["ok"]:
        raise RuntimeError(f"setmany {scope} {values} failed: {r}")


def save():
    r = post("/api/save")
    if not r["ok"]:
        raise RuntimeError(f"save failed {r}")


def events(since=0):
    return get(f"/api/events?since={since}")


def ev_total():
    return status()["evn"]


def events_after(n):
    return [e for e in events(n)["ev"] if e[0] >= n]


# --- 序列埠 ---
def ser_open():
    """Windows 開 COM 會切 DTR/RTS,C3 原生 USB 當成重置 → 開之前設成不動作,整個測試只開一次."""
    global _ser
    if _ser is None:
        _ser = serial.Serial()
        _ser.port = PORT
        _ser.baudrate = 115200
        _ser.timeout = 0.05
        _ser.dtr = False
        _ser.rts = False
        _ser.open()
        time.sleep(0.3)
    return _ser


def cmd(line, wait=0.15, expect=None):
    s = ser_open()
    s.reset_input_buffer()
    s.write((line + "\n").encode())
    t_end = time.time() + (1.5 if expect else wait)
    buf = ""
    while time.time() < t_end:
        buf += s.read(4096).decode("utf-8", "replace")
        if expect and expect in buf and "\n" in buf[buf.index(expect):]:
            break
    return buf.strip()


def sim(args):
    r = cmd("sim " + args, expect="sim")
    if "ERR" in r:
        raise RuntimeError(f"sim {args}: {r}")
    return r


def pwm():
    """回傳 dict(active,pulses,high,period,min,max,age)"""
    r = cmd("pwm", expect="pwm active")
    for line in r.splitlines():
        if line.startswith("pwm active"):
            return {k: int(v) for k, v in (x.split("=") for x in line.split()[1:])}
    raise RuntimeError(f"pwm parse: {r}")


def led_capture(ms=3000):
    cmd(f"ledcap {ms}", expect="OK")
    time.sleep(ms / 1000 + 0.2)
    r = cmd("led", expect="led")
    for line in r.splitlines():
        if line.startswith("led runs"):
            parts = line.split()[2:]
            return [(p[0] == "+", int(p[1:])) for p in parts]
    raise RuntimeError(f"led parse: {r}")


# --- 測試用設定(安裝方位,電變協定/頻率/脈寬沿用板上的值,不動)---
TEST_SHARED = {
    "pitchTrim": 0, "gestureEnable": 1, "gestureG": 2.0, "startLevel": 35, "countdownSec": 5,
    "disturbG": 0.3, "disturbMode": 0, "extendSec": 3, "touchdownG": 3.0, "touchdownStill": 1.0,
    "landingTimeout": 20, "crashEnable": 1, "crashG": 14, "earlyLand": 0, "earlyLandArm": 10,
    "earlyLandTilt": 20, "earlyLandVib": 0.8, "earlyLandHold": 1.0, "twistCancel": 45, "twistBlock": 5,
    "lineLength": 18, "lapSec": 5.2,
}
TEST_PROFILE = {
    "phase1Sec": 10, "flightSec": 30, "phase1Pct": 60, "phase2Pct": 80, "takeoffRamp": 2, "phaseRamp": 3,
    "noCompSec": 3, "minPct": 30, "maxPct": 100, "landingRamp": 3, "landingPct": 30, "phaseMode": 1,
    "upDb": 20, "upN": 3, "up1a": 45, "up1p": 8, "up2a": 70, "up2p": 15, "up3a": 90, "up3p": 20,
    "dnDb": -3, "dnN": 3, "dn1a": -30, "dn1p": -10, "dn2a": -60, "dn2p": -20, "dn3a": -90, "dn3p": -25,
}
TEST_SLOT = 0


def configure(shared=None, profile=None):
    """測試設定寫進共用與風格 A,選用 A 並儲存. shared/profile 是蓋在 TEST_* 上的覆寫."""
    st = status()
    if fstate(st) not in ("arming", "standby", "done"):
        log(f"  (configure:板子在 {fstate(st)},先停止/取消;表示前一項測試沒有照預期結束)")
        post("/api/estop")
        post("/api/cancel")
        time.sleep(0.4)
    s = dict(TEST_SHARED, **(shared or {}))
    p = dict(TEST_PROFILE, **(profile or {}))
    setmany("s", s)
    setmany(TEST_SLOT, p)
    post("/api/select", p=TEST_SLOT)
    save()
    return s, p


def curve_comp(p, pitch):
    """與 settings.cpp curveCompPct 同一規則:死區內 0,死區邊界 0% 起直線連到各點,最後一點之外持平."""
    if pitch >= 0:
        pts = [(p["upDb"], 0)] + [(p[f"up{i}a"], p[f"up{i}p"]) for i in range(1, p["upN"] + 1)]
        x = pitch
        if x <= pts[0][0]:
            return 0.0
    else:
        pts = [(-p["dnDb"], 0)] + [(-p[f"dn{i}a"], p[f"dn{i}p"]) for i in range(1, p["dnN"] + 1)]
        x = -pitch
        if x <= pts[0][0]:
            return 0.0
    for (a0, c0), (a1, c1) in zip(pts, pts[1:]):
        if x <= a1:
            return c0 + (c1 - c0) * (x - a0) / (a1 - a0)
    return float(pts[-1][1])


# --- 設定保護(GG 的板上設定是他的資料)---
SNAP = None


_restored = False


def _emergency_restore():
    """腳本中途出錯結束時:停馬達,關模擬,還原設定(atexit)."""
    if SNAP is None or _restored:
        return
    log("\n!! 腳本沒有正常收尾,自動緊急停止並還原設定")
    try:
        post("/api/estop")
        time.sleep(0.4)
        post("/api/cancel")
        time.sleep(0.3)
        cmd("sim off", expect="sim")
        cmd("armsw off", expect="OK")
        cmd("pwmcap off", expect="OK")
        log("  還原:", board_backup.restore(HOST, SNAP) or "ok")
        log("  比對:", board_backup.diff(SNAP, board_backup.backup(HOST)) or "相同")
    except Exception as e:  # noqa: BLE001
        log("  自動還原失敗,請用 tools/recover.py 與 %TEMP% 的備份檔:", e)
    if _log:
        _log.flush()


def protect():
    global SNAP
    import atexit
    board_backup.require_idle(HOST)
    SNAP = board_backup.backup(HOST)
    atexit.register(_emergency_restore)
    cmd("armsw 1", expect="OK")   # 開發板沒接 GPIO21 安全開關,測試期間當作按下(flight r17 起沒按不能起飛)
    return SNAP


def restore_and_verify():
    global _restored
    _restored = True
    try:
        cmd("sim off", expect="sim")
        cmd("armsw off", expect="OK")
    except Exception:  # noqa: BLE001
        pass
    errs = board_backup.restore(HOST, SNAP)
    check("還原寫入成功", not errs, errs)
    d = board_backup.diff(SNAP, board_backup.backup(HOST))
    check("還原後設定與測試前完全相同", not d, d[:8])
    st = status()
    check("收尾:沒有未儲存變更", st["dirty"] == 0, st["dirty"])


def gesture_push(g=2.5, ms=120, rearm=1.7):
    """用模擬感測器做真的啟動手勢:機頭方向推一下(走控制工作的推力計算與狀態機判斷)."""
    time.sleep(rearm)   # 韌體一次手勢後 1.5 秒內不接受下一次
    sim(f"pulse x {g} {ms}")
