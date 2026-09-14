# 版本流水號: r1 (2026-09-13) 外力延長上限測試:連續模擬外力,倒數不可超過「倒數秒數 +10 秒」(不改任何設定)
# ============================================================================
# 用法: python tools/extend_cap_test.py [COM埠] [板子位址]
# 需要板上「外力介入時」是延長秒數. 只用序列測試指令 gesture / disturb / cancel,不寫設定.
# ============================================================================
import json
import sys
import time
import urllib.request

import serial

import board_backup

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM20"
HOST = sys.argv[2] if len(sys.argv) > 2 else "lineplane.local"
STATE = board_backup.STATE
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    passed += bool(cond)
    failed += not cond
    print("  OK  " if cond else "  FAIL", name, "" if cond else detail)


def st():
    return json.loads(urllib.request.urlopen(f"http://{HOST}/api/status", timeout=5).read())["f"]


def wait(target, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        f = st()
        if STATE[f["s"]] == target:
            return f
        time.sleep(0.1)
    return st()


board_backup.require_idle(HOST)
sh = board_backup._get(HOST, "/api/settings")["shared"]
cd_set, ext, mode = sh["countdownSec"], sh["extendSec"], sh["disturbMode"]
if mode != 0:
    raise SystemExit("板上「外力介入時」不是延長秒數,這個測試不適用(不改設定,中止).")
if not sh["gestureEnable"]:
    raise SystemExit("板上啟動手勢關閉,無法用模擬手勢開始倒數(不改設定,中止).")
cap = cd_set + 10
print(f"板上設定:倒數 {cd_set} 秒,每次延長 {ext} 秒 → 上限 {cap} 秒")

ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = PORT, 115200, 0.2, False, False   # 不切 DTR/RTS,板子不會重開
ser.open()
time.sleep(1.7)
try:
    ser.write(b"gesture\n")
    f = wait("countdown", 8)
    check("手勢後進入倒數", STATE[f["s"]] == "countdown", f)
    seen = []
    for k in range(6):
        ser.write(b"disturb\n")
        f = wait("wait_still", 3)
        if STATE[f["s"]] != "wait_still":
            continue   # 指令剛好碰上真的外力(當下不在倒數)而被忽略,換下一次
        f = wait("countdown", 5)
        seen.append(round(f["cd"], 1))
        time.sleep(0.3)
    print("  每次放穩後的倒數剩餘秒數:", seen)
    check(f"倒數從未超過上限 {cap} 秒", seen and max(seen) <= cap + 0.05, seen)
    # 外力門檻調得很低時(例如 0.05g),線材或桌面震動也會觸發真的外力,中間讀數可能略低,只驗核心規則
    check(f"多次外力後倒數確實到達上限(最大 ≥ {cap - 0.5} 秒)", seen and max(seen) >= cap - 0.5, seen)
finally:
    urllib.request.urlopen(urllib.request.Request(f"http://{HOST}/api/cancel", data=b""), timeout=5).read()
    time.sleep(0.5)
    ser.close()
f = st()
check("收尾取消倒數,回到待機", STATE[f["s"]] == "standby", f)
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
