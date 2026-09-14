# 版本流水號: r1 (2026-09-13) 事件紀錄測試:模擬手勢→倒數→取消,再手勢→起飛→緊急停止,檢查事件內容與順序
# ============================================================================
# 不改任何設定(用板上目前的設定),板子要在待機,手勢開啟,沒有未儲存變更. 會讓電變輸出油門幾秒.
# 用法: %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/event_log_test.py [COM埠] [板子位址]
# ============================================================================
import json
import sys
import time
import urllib.parse
import urllib.request

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM20"
HOST = "http://" + (sys.argv[2] if len(sys.argv) > 2 else "lineplane.local")
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  OK  ", name)
    else:
        failed += 1
        print("  FAIL", name, detail)


def get(path):
    return json.loads(urllib.request.urlopen(HOST + path, timeout=8).read())


def post(path, **d):
    req = urllib.request.Request(HOST + path, data=urllib.parse.urlencode(d).encode())
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def wait_state(targets, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = get("/api/status")
        if st["f"]["s"] in targets:
            return st
        time.sleep(0.1)
    return get("/api/status")


st = get("/api/status")
sh = get("/api/settings?p=0")["shared"]
if st["f"]["s"] not in (1, 7) or st["dirty"] or not sh["gestureEnable"]:
    raise SystemExit("板子要在待機,手勢開啟,沒有未儲存變更,測試中止.")

# 網頁回應時間(輪詢漏狀態時先看這個)
lat = []
for _ in range(20):
    t = time.time()
    get("/api/status")
    lat.append(time.time() - t)
print(f"狀態回應時間 平均 {sum(lat) / len(lat) * 1000:.0f} ms,最長 {max(lat) * 1000:.0f} ms")

ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = PORT, 115200, 0.2, False, False
ser.open()
n0 = get("/api/status")["evn"]

ser.write(b"gesture\n")
st = wait_state((3,), 8)
check("模擬手勢後進入倒數", st["f"]["s"] == 3, st["f"]["s"])
post("/api/cancel")
wait_state((1,), 3)
time.sleep(1.6)   # 手勢重新接受間隔 1.5 秒
ser.write(b"gesture\n")
st = wait_state((4, 5), sh["countdownSec"] + 12)
check("第二次手勢後馬達啟動", st["f"]["s"] in (4, 5), st["f"]["s"])
time.sleep(1.0)
post("/api/estop")
st = wait_state((7,), 3)
check("緊急停止後結束", st["f"]["s"] == 7 and st["f"]["er"] == 6, st["f"])
time.sleep(0.5)
ser.close()

r = get(f"/api/events?since={n0}")
ev = r["ev"]
types = [e[2] for e in ev]
print("事件:", [(round(e[1] / 1000, 1), e[2], e[3], e[4], e[5]) for e in ev])
want = [3, 5, 7, 3, 5, 8, 11]   # 手勢,倒數,取消,手勢,倒數,馬達啟動,馬達停止
it = iter(types)
check("事件順序:手勢 → 倒數 → 取消 → 手勢 → 倒數 → 馬達啟動 → 馬達停止", all(w in it for w in want), types)
stop = [e for e in ev if e[2] == 11]
check("馬達停止原因 = 緊急停止(6)", bool(stop) and stop[-1][3] == 6, stop)
cd = [e for e in ev if e[2] == 5]
check(f"倒數事件記下倒數秒數 {sh['countdownSec']}", bool(cd) and abs(cd[0][4] - sh["countdownSec"]) < 0.01, cd)
ms = [e[1] for e in ev]
check("時間(通電後毫秒)遞增", ms == sorted(ms), ms)
check("事件總數與狀態一致", r["total"] == get("/api/status")["evn"], (r["total"],))
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
