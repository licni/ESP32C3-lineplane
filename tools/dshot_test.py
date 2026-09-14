# 版本流水號: r3 (2026-09-13) 協定改 DShot150/300;r2:加 PWM 250Hz 套用與 450Hz 被拒
# 舊: r1 (2026-09-13) DShot 輸出實機測試:切協定重開機,序列埠 dshot 回授解碼(停止/手動 50%),DShot600,還原 PWM
# ============================================================================
# 會改寫並儲存共用設定的輸出協定,結束時用 board_backup 還原並重開機回 PWM.
# 板子要在待機且沒有未儲存變更. GPIO4 上接的舵機會收到 DShot 訊號(舵機不會動,無害).
# 用法: %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/dshot_test.py [COM埠] [板子位址]
# ============================================================================
import json
import sys
import threading
import time
import urllib.parse
import urllib.request

import serial

import board_backup

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM20"
HOST = sys.argv[2] if len(sys.argv) > 2 else "lineplane.local"
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
    return json.loads(urllib.request.urlopen(f"http://{HOST}{path}", timeout=8).read())


def post(path, **data):
    req = urllib.request.Request(f"http://{HOST}{path}", data=urllib.parse.urlencode(data).encode())
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def wait_back(expect_proto):
    time.sleep(4)
    for _ in range(40):
        try:
            st = get("/api/status")
            if st["proto"] == expect_proto and st["f"]["s"] in (1, 7):
                return st
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    raise RuntimeError("board did not come back with protocol %d" % expect_proto)


def set_proto_and_reboot(p):
    r1 = post("/api/set", p="s", k="escProtocol", v=p)
    r2 = post("/api/save")
    r3 = post("/api/reboot")
    return r1["ok"] and r2["ok"] and r3["ok"]


# 序列埠:Windows 開 COM 會切 DTR/RTS,C3 原生 USB 當成重置. 先關掉再開,且整個測試只開一次.
ser = serial.Serial()
ser.port = PORT
ser.baudrate = 115200
ser.timeout = 0.2
ser.dtr = False
ser.rts = False


def serial_cmd(cmd, want, timeout=4.0):
    ser.reset_input_buffer()
    ser.write((cmd + "\n").encode())
    t0 = time.time()
    buf = ""
    while time.time() - t0 < timeout:
        buf += ser.read(512).decode(errors="replace")
        for line in buf.splitlines():
            if want in line:
                return line.strip()
    return buf.strip()[-200:]


board_backup.require_idle(HOST)
SNAP = board_backup.backup(HOST)
beat_stop = threading.Event()
try:
    for proto, name in ((1, "DShot150"), (2, "DShot300")):
        print(f"--- {name} ---")
        check(f"切到 {name} 並儲存,重開機", set_proto_and_reboot(proto))
        if not ser.is_open:
            time.sleep(2)
        st = wait_back(proto)
        if not ser.is_open:
            ser.open()
        check(f"開機套用 {name}:proto={st['proto']},DShot 值 {st['dsh']}", st["proto"] == proto and st["dsh"] == 0, st.get("dsh"))
        line = serial_cmd("dshot", "dshot")
        check(f"回授解碼(停止):{line}", line.startswith("OK") and "value=0 " in line, line)

        mn, mx = SNAP["shared"]["escMinUs"], SNAP["shared"]["escMaxUs"]
        mid = (mn + mx) // 2
        r = post("/api/manual", us=mn)
        beat_stop.clear()

        beat_log = []

        def beat():
            while not beat_stop.is_set():
                t = time.time()
                rr = post("/api/manual", us=mid)
                beat_log.append((round(time.time() - t, 3), rr["code"]))
                time.sleep(0.2)

        th = threading.Thread(target=beat, daemon=True)
        th.start()
        time.sleep(0.6)
        st = get("/api/status")
        expect = round(48 + (2047 - 48) * 50 / 100)
        # 失敗時列出每次心跳的耗時與回應:有別的網頁同時在操作手動輸出,或心跳間隔超過 0.5 秒都看得出來
        check(f"手動輸出 50%:DShot 值 {st['dsh']}(預期 {expect})", r["ok"] and st["man"] == 1 and st["dsh"] == expect,
              (r, st.get("man"), st.get("esc"), beat_log[:6]))
        line = serial_cmd("dshot", "dshot")
        check(f"回授解碼(50%):{line}", line.startswith("OK") and f"value={expect} " in line, line)
        beat_stop.set()
        th.join()
        post("/api/manual/stop")
        time.sleep(0.3)
        st = get("/api/status")
        check(f"上鎖回停止:DShot 值 {st['dsh']},控制迴圈最長 {st['ex']} µs", st["dsh"] == 0 and st["man"] == 0, st.get("dsh"))
        r = post("/api/calib", on=1)
        check("DShot 時拒絕設定校正(calibproto)", not r["ok"] and r["code"] == "calibproto", r)

    print("--- PWM 250Hz ---")
    r0 = post("/api/set", p="s", k="escProtocol", v=0)
    r1 = post("/api/set", p="s", k="escPwmHz", v=250)
    r2 = post("/api/set", p="s", k="escPwmHz", v=450)
    check("PWM 頻率超過 400Hz 被拒(range)", not r2["ok"] and r2["code"] == "range", r2)
    check("設定 PWM 250Hz 並儲存,重開機", r0["ok"] and r1["ok"] and post("/api/save")["ok"] and post("/api/reboot")["ok"])
    st = wait_back(0)
    check(f"開機套用 PWM {st['hz']}Hz,輸出 {st['esc']} µs", st["hz"] == 250 and st["esc"] == 1000, (st["hz"], st["esc"]))
finally:
    beat_stop.set()
    print("--- 還原 ---")
    errs = board_backup.restore(HOST, SNAP)
    check("還原設定寫入成功", not errs, errs)
    post("/api/reboot")
    st = wait_back(SNAP["shared"].get("escProtocol", 0))
    check(f"重開機回 PWM:proto={st['proto']},{st['hz']}Hz,輸出 {st['esc']} µs",
          st["proto"] == 0 and st["esc"] == 1000 and st["hz"] == SNAP["shared"].get("escPwmHz", 50), (st["proto"], st["hz"], st["esc"]))
    d = board_backup.diff(SNAP, board_backup.backup(HOST))
    check("設定與測試前完全相同", not d, d[:5])
    if ser.is_open:
        ser.close()
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
