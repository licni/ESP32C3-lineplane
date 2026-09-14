# 版本流水號: r1 (2026-09-13) 雙向 DShot 轉速回傳桌上測試:切 DShot300 + 回傳,合成回傳解碼自我測試,送框統計,控制迴圈與網頁負擔,還原
# ============================================================================
# 沒接電變:電變端的回傳時序要接真的雙向 DShot 電變才能驗證. 這裡驗證 C3 端的送框,切換,接收設定與 GCR 解碼.
# 會改協定並儲存,結束用 board_backup 還原並重開機. 板子要在待機且沒有未儲存變更.
# 用法: %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/rpm_telemetry_test.py [COM埠] [板子位址]
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
IP = socket.gethostbyname(sys.argv[2] if len(sys.argv) > 2 else "lineplane.local")
HOST = "http://" + IP
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


def wait_back(proto):
    time.sleep(4)
    for _ in range(40):
        try:
            st = get("/api/status")
            if st["proto"] == proto and st["f"]["s"] in (1, 7):
                return st
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    raise RuntimeError("board not back")


def latency(n=40):
    lat = []
    for _ in range(n):
        t = time.time()
        get("/api/status")
        lat.append(time.time() - t)
        time.sleep(0.05)
    lat.sort()
    return lat[len(lat) // 2] * 1000, lat[-1] * 1000


ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = PORT, 115200, 0.2, False, False


def cmd(c, want, timeout=3.0):
    ser.reset_input_buffer()
    ser.write((c + "\n").encode())
    t0 = time.time()
    buf = ""
    while time.time() - t0 < timeout:
        buf += ser.read(512).decode(errors="replace")
        for line in buf.splitlines():
            if want in line:
                return line.strip()
    return buf.strip()[-200:]


board_backup.require_idle(IP)
SNAP = board_backup.backup(IP)
try:
    med0, max0 = latency()
    st0 = get("/api/status")
    print(f"--- 基準(PWM):網頁回應中位 {med0:.0f} ms 最長 {max0:.0f} ms,控制迴圈最長 {st0['ex']} µs")
    post("/api/timing/reset")

    print("--- 切到 DShot300 + 轉速回傳 ---")
    ok = all(post("/api/set", p="s", k=k, v=v)["ok"] for k, v in (("escProtocol", 2), ("escRpm", 1), ("motorPoles", 14)))
    check("設定 DShot300 + 轉速回傳並儲存,重開機", ok and post("/api/save")["ok"] and post("/api/reboot")["ok"])
    st = wait_back(2)
    ser.open()
    check(f"開機套用:proto={st['proto']},回傳啟用={st['rpm'][0]}", st["proto"] == 2 and st["rpm"][0] == 1, st.get("rpm"))

    time.sleep(2)
    a = get("/api/status")["rpm"]
    time.sleep(2)
    b = get("/api/status")["rpm"]
    fps = (b[1] - a[1]) / 2
    check(f"每秒送出訊框約 2000(實測 {fps:.0f})", 1800 <= fps <= 2100, (a, b))
    check(f"沒接電變:沒有回傳({b[5] - a[5]} 次/2秒),沒有假解碼成功", b[3] == a[3], (a, b))

    for p in (1000, 50, 20000, 65408, 333):
        line = cmd(f"rpmtest {p}", "rpmtest")
        e = 0
        while (p >> e) > 0x1FF and e < 7:
            e += 1
        expect = (p >> e) << e
        check(f"合成回傳解碼 週期 {p}µs(量化 {expect}):{line}", line.startswith("OK") and f"decoded={expect}us" in line, line)

    post("/api/timing/reset")
    time.sleep(0.2)
    med1, max1 = latency()
    st = get("/api/status")
    check(f"網頁回應中位 {med1:.0f} ms 最長 {max1:.0f} ms(基準 {med0:.0f}/{max0:.0f})", max1 < 400, (med1, max1))
    check(f"控制迴圈最長執行 {st['ex']} µs,延遲 {st['late']} ms", st["ex"] < 3000 and st["late"] <= 16, (st["ex"], st["late"]))

    # 手動輸出在雙向模式下:DShot 值跟著變
    post("/api/manual", us=1000)
    for _ in range(4):
        post("/api/manual", us=1500)
        time.sleep(0.2)
    st = get("/api/status")
    check(f"雙向模式手動 50%:DShot 值 {st['dsh']}", st["dsh"] == 1048, st["dsh"])
    post("/api/manual/stop")
finally:
    print("--- 還原 ---")
    errs = board_backup.restore(IP, SNAP)
    check("還原設定寫入成功", not errs, errs)
    post("/api/reboot")
    st = wait_back(SNAP["shared"].get("escProtocol", 0))
    check(f"重開機回原協定 proto={st['proto']},回傳={st['rpm'][0]}", st["proto"] == SNAP["shared"].get("escProtocol", 0), st.get("rpm"))
    d = board_backup.diff(SNAP, board_backup.backup(IP))
    check("設定與測試前完全相同", not d, d[:5])
    if ser.is_open:
        ser.close()
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
