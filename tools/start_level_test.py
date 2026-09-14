# 版本流水號: r4 (2026-09-14) 安全開關:序列指令 armsw 1 當作按下
# 舊: r3 (2026-09-14) 上電自動倒數段落重開前送 powerontest(韌體改成只有上電才自動倒數)
# 舊: r2 (2026-09-13) 加起飛程序中角度超過取消(序列指令 tilt 模擬)
# 舊: r1 (2026-09-13) 起飛前水平限制測試:角度超過時手勢被拒,上電自動倒數暫停等放平,原因寫進事件紀錄
# ============================================================================
# 板子平放在桌上,用「角度修正 +30°」讓控制器以為機頭抬起約 30°,再把水平限制設 20° 製造「角度超過」.
# 會改設定並儲存,結束用 board_backup 還原並重開機比對. 板子要在待機且沒有未儲存變更. 不會啟動馬達(倒數後取消).
# 用法: %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/start_level_test.py [COM埠] [板子位址]
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


def setsave(**kv):
    ok = all(post("/api/set", p="s", k=k, v=v)["ok"] for k, v in kv.items())
    return ok and post("/api/save")["ok"]


def wait_state(targets, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = get("/api/status")
        if st["f"]["s"] in targets:
            return st
        time.sleep(0.1)
    return get("/api/status")


def wait_back():
    time.sleep(4)
    for _ in range(40):
        try:
            return get("/api/status")
        except Exception:  # noqa: BLE001
            time.sleep(1)
    raise RuntimeError("board not back")


def events_since(n):
    return get(f"/api/events?since={n}")["ev"]


ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = PORT, 115200, 0.2, False, False

board_backup.require_idle(IP)
SNAP = board_backup.backup(IP)
try:
    print("--- 手勢啟動模式 ---")
    check("設定:手勢開啟,角度修正 +30°,水平限制 20°", setsave(gestureEnable=1, pitchTrim=30, startLevel=20, disturbMode=2))
    time.sleep(2)
    st = get("/api/status")
    check(f"控制角度約 +30°(實際 {st['p']:.1f}°)", st["p"] > 22, st["p"])
    ser.open()
    ser.write(b"armsw 1\n")   # 開發板沒接 GPIO21 安全開關,當作按下
    n0 = st["evn"]
    time.sleep(1.6)
    ser.write(b"gesture\n")
    time.sleep(1.0)
    st = get("/api/status")
    check(f"角度超過:手勢被拒,仍在待機(狀態 {st['f']['s']},拒絕原因 {st['f']['rj']})", st["f"]["s"] == 1 and st["f"]["rj"] == 3, st["f"])
    ev = [e for e in events_since(n0) if e[2] == 4]
    check(f"事件紀錄:拒絕原因 3 並記下角度 {ev[-1][4] if ev else None}°", bool(ev) and ev[-1][3] == 3 and ev[-1][4] > 22, ev)

    check("水平限制放寬到 40°", setsave(startLevel=40))
    time.sleep(1.6)
    ser.write(b"gesture\n")
    st = wait_state((2, 3), 4)
    check("角度在限制內:手勢成立進入起飛程序", st["f"]["s"] in (2, 3), st["f"])
    n1 = get("/api/status")["evn"]
    ser.write(b"tilt\n")   # 倒數中設定鎖定改不了角度,用序列指令模擬傾斜
    st = wait_state((1,), 3)
    check(f"起飛程序中角度超過:直接取消回待機(結束原因 {st['f']['er']})", st["f"]["s"] == 1 and st["f"]["er"] == 9, st["f"])
    ev = [e for e in events_since(n1) if e[2] == 21]
    check(f"事件紀錄:角度超過取消(限制 {ev[0][3] if ev else None}°,機頭 {ev[0][4] if ev else None}°)", bool(ev) and ev[0][3] == 40, ev)

    print("--- 上電自動倒數模式 ---")
    # 韌體 flight r15 起只有真的上電才自動倒數;桌上 USB 供電沒辦法斷電,用 powerontest 讓這次軟體重開算上電
    ser.write(b"powerontest\n")
    time.sleep(0.4)
    check("設定:手勢關閉,水平限制 20°(角度修正仍 +30°),重開機(算上電)", setsave(gestureEnable=0, startLevel=20) and post("/api/reboot")["ok"])
    ser.close()
    st = wait_back()
    time.sleep(1)
    ser.open()
    ser.write(b"armsw 1\n")   # 重開後覆寫清掉,再按一次
    st = wait_state((1, 3), 8)
    time.sleep(4)   # 解鎖 3 秒後會判斷
    st = get("/api/status")
    check(f"角度超過:不倒數,待機等放平(狀態 {st['f']['s']},等待 {st['f']['aw']})", st["f"]["s"] == 1 and st["f"]["aw"] == 1, st["f"])
    time.sleep(3)
    st = get("/api/status")
    check("持續超過就一直不倒數", st["f"]["s"] == 1 and st["f"]["aw"] == 1, st["f"])
    ev = events_since(0)
    rej = [e for e in ev if e[2] == 4 and e[3] == 4]
    check(f"事件紀錄:上電自動倒數暫停(原因 4,機頭 {rej[0][4] if rej else None}°)", bool(rej), [e[2:] for e in ev])

    check("角度修正改回 0(模擬把飛機放平)並儲存", setsave(pitchTrim=0))
    st = wait_state((3,), 5)
    check(f"放平維持 1 秒後開始倒數(狀態 {st['f']['s']},倒數 {st['f']['cd']})", st["f"]["s"] == 3 and st["f"]["aw"] == 0, st["f"])
    ev = events_since(0)
    check("事件紀錄有開始倒數", any(e[2] == 5 for e in ev), [e[2:] for e in ev])
    ser.write(b"tilt\n")
    st = wait_state((1,), 3)
    check(f"自動倒數中角度超過:取消(結束原因 {st['f']['er']}),不會再自己倒數", st["f"]["s"] == 1 and st["f"]["er"] == 9 and st["f"]["au"] == 1, st["f"])
    time.sleep(3)
    check("取消後維持待機", get("/api/status")["f"]["s"] == 1)
finally:
    print("--- 還原 ---")
    errs = board_backup.restore(IP, SNAP)
    check("還原設定寫入成功", not errs, errs)
    post("/api/reboot")
    if ser.is_open:
        ser.close()
    wait_back()
    d = board_backup.diff(SNAP, board_backup.backup(IP))
    check("設定與測試前完全相同", not d, d[:5])
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
