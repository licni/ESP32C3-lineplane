# 版本流水號: r1 (2026-09-13) 雙向 DShot 轉速回傳端到端測試(GPIO5 跳線接 GPIO4 模擬電變)
# ============================================================================
# 需要 GPIO5 ↔ GPIO4 跳線(GG 插的測試線). 板子模擬電變從 GPIO5 回傳指定週期,控制器從 GPIO4 收回來解碼.
# 驗證:送框 → 放開線 → 接收 → 解碼整條路徑,解碼成功率,控制器送出的反相訊框內容(模擬電變解出油門值),負擔.
# 不驗證真電變的回傳時序(30µs)與電氣特性. 會改協定並儲存,結束還原並重開機.
# 用法: %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/rpm_emulator_test.py [COM埠] [板子位址]
# ============================================================================
import json
import re
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


def window(secs):
    a = get("/api/status")["rpm"]
    time.sleep(secs)
    b = get("/api/status")["rpm"]
    d = [b[i] - a[i] for i in range(1, 6)]   # frames, replies, ok, bad, noReply
    return d, b


def emu_stats():
    line = cmd("emu", "emu frames")
    return {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line)}


board_backup.require_idle(IP)
SNAP = board_backup.backup(IP)
try:
    ok = all(post("/api/set", p="s", k=k, v=v)["ok"] for k, v in (("escProtocol", 2), ("escRpm", 1), ("motorPoles", 14)))
    check("設定 DShot300 + 轉速回傳並儲存,重開機", ok and post("/api/save")["ok"] and post("/api/reboot")["ok"])
    st = wait_back(2)
    ser.open()
    check(f"開機套用 DShot300 回傳啟用={st['rpm'][0]}", st["rpm"][0] == 1, st["rpm"])

    d, _ = window(2)
    print(f"  (模擬電變關閉 2 秒:送框 {d[0]},收到 {d[1]},成功 {d[2]},失敗 {d[3]},沒回傳 {d[4]})")
    check("沒有回傳時不會解碼成功", d[2] == 0, d)

    post("/api/timing/reset")
    for period, expect in ((1000, 1000), (333, 333), (20000, 19968), (5000, 4992)):
        r = cmd(f"escemu {period}", "escemu")
        time.sleep(1)
        d, b = window(3)
        rate = d[2] / d[0] * 100 if d[0] else 0
        check(f"模擬電變週期 {period}µs:3 秒送框 {d[0]},解碼成功 {d[2]}({rate:.1f}%),失敗 {d[3]},沒回傳 {d[4]},解出 {b[6]}µs",
              r.startswith("OK") and b[6] == expect and rate >= 90, (r, d, b))

    r = cmd("escemu stop", "escemu")
    time.sleep(1)
    b = get("/api/status")["rpm"]
    check(f"模擬電變回傳「馬達停止」:週期欄位 {b[6]}(0xFFFF = 65535)", b[6] == 0xFFFF, b)

    cmd("escemu 1000", "escemu")
    post("/api/manual", us=1000)
    for _ in range(5):
        post("/api/manual", us=1500)
        time.sleep(0.2)
    e = emu_stats()
    st = get("/api/status")
    check(f"模擬電變解出控制器送的反相訊框:油門值 {e.get('value')}(控制器 {st['dsh']}),CRC 正確 {e.get('crcok')}/{e.get('frames')}",
          e.get("value") == 1048 and st["dsh"] == 1048 and e.get("crcok", 0) >= e.get("frames", 1) * 0.95, (e, st["dsh"]))
    post("/api/manual/stop")

    lat = []
    for _ in range(30):
        t = time.time()
        get("/api/status")
        lat.append(time.time() - t)
        time.sleep(0.05)
    st = get("/api/status")
    check(f"模擬中網頁回應最長 {max(lat) * 1000:.0f} ms,控制迴圈最長 {st['ex']} µs,延遲 {st['late']} ms",
          max(lat) < 0.4 and st["ex"] < 3000 and st["late"] <= 16, (max(lat), st["ex"], st["late"]))
    cmd("escemu off", "escemu")
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
