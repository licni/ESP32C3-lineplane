# 版本流水號: r1 (2026-09-13) 扭轉機尾取消起飛測試:手勢→倒數→模擬扭轉→回待機,封鎖期內手勢無效,封鎖期後手勢有效
# ============================================================================
# 不改設定(用板上目前的封鎖秒數),板子要在待機,手勢開啟,沒有未儲存變更. 不會啟動馬達(最後取消倒數).
# 實際扭轉角度的累積要拿飛機實測(桌上用序列指令 twist 模擬).
# 用法: %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/twist_cancel_test.py [COM埠] [板子位址]
# ============================================================================
import json
import socket
import sys
import time
import urllib.parse
import urllib.request

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM20"
HOST = "http://" + socket.gethostbyname(sys.argv[2] if len(sys.argv) > 2 else "lineplane.local")
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
block = sh["twistBlock"]

ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = PORT, 115200, 0.2, False, False
ser.open()
n0 = st["evn"]
try:
    time.sleep(1.6)
    ser.write(b"gesture\n")
    st = wait_state((2, 3), 5)
    check("手勢後進入起飛程序(等待放穩/倒數)", st["f"]["s"] in (2, 3), st["f"]["s"])
    st = wait_state((3,), 5)
    check(f"倒數中扭轉角度欄位存在:{st['f'].get('tw')}°", "tw" in st["f"], st["f"])
    ser.write(b"twist\n")
    st = wait_state((1,), 3)
    check(f"扭轉 → 回待機,結束原因 8,封鎖 {st['f']['gb']} 秒", st["f"]["s"] == 1 and st["f"]["er"] == 8 and st["f"]["gb"] > block - 1, st["f"])

    time.sleep(1.6)   # 超過手勢重新接受間隔,但仍在封鎖期內
    ser.write(b"gesture\n")
    time.sleep(0.8)
    st = get("/api/status")
    check(f"封鎖期內手勢無效(仍在待機,剩 {st['f']['gb']} 秒)", st["f"]["s"] == 1 and st["f"]["gb"] > 0, st["f"])

    while get("/api/status")["f"]["gb"] > 0:
        time.sleep(0.3)
    time.sleep(0.3)
    ser.write(b"gesture\n")
    st = wait_state((2, 3), 5)
    check("封鎖期過後手勢恢復有效", st["f"]["s"] in (2, 3), st["f"])
    post("/api/cancel")
    st = wait_state((1,), 3)
    check("取消倒數回待機", st["f"]["s"] == 1, st["f"]["s"])
finally:
    ser.close()

ev = get(f"/api/events?since={n0}")["ev"]
types = [e[2] for e in ev]
print("事件:", [(round(e[1] / 1000, 1), e[2], e[3], e[4], e[5]) for e in ev])
tw = [e for e in ev if e[2] == 20]
check(f"事件紀錄有扭轉取消(封鎖 {block} 秒)", bool(tw) and tw[0][3] == block, tw)
check("封鎖期內的手勢沒有被記成手勢成立(只有 2 次手勢)", types.count(3) == 2, types)
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
