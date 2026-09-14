# 版本流水號: r3 (2026-09-14) 收尾走「存檔 → 重開 → 保持 → 再重開」確認流程(r2 收尾留下待確認試用,改到 GG 的等待秒數)
# 舊: r2 (2026-09-14) 退回時檢查板子沒重開(r1 抓到 mDNS 當機);加斷線太久改開熱點
# 舊: r1 (2026-09-14) WiFi 設定保護測試:發射功率試用退回/保持,儲存設定重開後沒確認自動退回/保持,
# 連續開關電救援(rescuetest 模擬上電),打斷計數不救援,斷線自動重連. 結尾把 WiFi 設定還原成測試前.
# 需要:USB(COM20),電腦有線網路在家用網段,無線網卡有 HappySuperGG_Plane 設定檔. 約 9 分鐘.
# 測試前 WiFi 設定(含家用密碼)只存在 test_logs/(不進版本庫).
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import serial

PORT = "COM20"
STA_IP = sys.argv[1] if len(sys.argv) > 1 else "lineplane.local"
AP_IP = "192.168.4.1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = open(os.path.join(ROOT, "test_logs", time.strftime("wifi_protect_test_%Y%m%d_%H%M%S.txt")), "w", encoding="utf-8")
passed = failed = 0


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


def check(name, cond, detail=""):
    global passed, failed
    passed += bool(cond)
    failed += not cond
    log("  OK  " if cond else "  FAIL", name, "" if cond else detail)


def http(host, path, data=None, timeout=5):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(f"http://{host}{path}", data=body)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def wait_http(host, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            return http(host, "/api/status", timeout=3)
        except Exception:  # noqa: BLE001
            time.sleep(1)
    return None


ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = PORT, 115200, 0.1, False, False
ser.open()
time.sleep(0.3)


def cmd(line, expect, timeout=3.0):
    t0 = time.time()
    buf = ""
    ser.reset_input_buffer()
    ser.write((line + "\n").encode())
    while time.time() - t0 < timeout:
        buf += ser.read(4096).decode("utf-8", "replace")
        if expect in buf:
            return buf
    return buf


def wait_boot():
    """送 reboot,之後一直問 fs,板子一回應(開機約 1~2 秒)就回傳. 不能等固定秒數:救援時窗只有 5 秒."""
    ser.reset_input_buffer()
    ser.write(b"reboot\n")
    time.sleep(0.8)
    t0 = time.time()
    while time.time() - t0 < 10:
        try:
            if "state=" in cmd("fs", "state=", timeout=0.4):
                return time.time() - t0
        except Exception:  # noqa: BLE001
            time.sleep(0.2)
    return None


def net():
    r = cmd("net", "txp=")
    for ln in r.splitlines():
        if ln.startswith("wifi="):
            return dict(x.split("=", 1) for x in ln.split())
    return {}


def form(w, **over):
    d = {k: w[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp")}
    d["apsfx"] = w.get("apsfx", "")
    d.update(over)
    return d


def events(host):
    return http(host, "/api/events?since=0")["ev"]


w0 = http(STA_IP, "/api/wifi")
with open(os.path.join(ROOT, "test_logs", "wifi_protect_before.json"), "w", encoding="utf-8") as f:
    json.dump(w0, f, ensure_ascii=False)
st = http(STA_IP, "/api/status")
log("測試前:", {k: w0[k] for k in ("ssid", "host", "tmo", "forceap", "txp", "apsfx")}, "目前功率", st["wt"][3])
check("開始時沒有試用中", st["wt"][0] == 0 and st["wt"][1] == 0, st["wt"])
txp0 = st["wt"][3]

try:
    # ---- 1. 發射功率試用 ----
    log("\n== 1. 發射功率試用 15 秒 ==")
    alt = 4 if txp0 != 4 else 3
    r = http(STA_IP, "/api/txpower", {"txp": alt})
    st = http(STA_IP, "/api/status")
    check(f"拉到 {alt} dBm:立即生效,試用剩 {st['wt'][0]} 秒", r["ok"] and st["wt"][3] == alt and 13 <= st["wt"][0] <= 15, st["wt"])
    time.sleep(16)
    st = http(STA_IP, "/api/status")
    ev = [e for e in events(STA_IP) if e[2] == 24 and e[3] == 3]
    check(f"15 秒沒按保持:退回 {st['wt'][3]} dBm,事件 24/3", st["wt"][3] == txp0 and st["wt"][0] == 0 and ev and ev[-1][4] == txp0, (st["wt"], ev[-1:]))
    http(STA_IP, "/api/txpower", {"txp": alt})
    time.sleep(1)
    http(STA_IP, "/api/wifi/keep", {})
    time.sleep(16)
    st = http(STA_IP, "/api/status")
    check(f"按保持:16 秒後仍是 {st['wt'][3]} dBm", st["wt"][3] == alt and st["wt"][0] == 0, st["wt"])
    http(STA_IP, "/api/txpower", {"txp": 6})
    http(STA_IP, "/api/txpower", {"txp": 8})
    time.sleep(16)
    st = http(STA_IP, "/api/status")
    check(f"連續拖兩次沒按保持:退回最後確認的 {alt} dBm(實際 {st['wt'][3]})", st["wt"][3] == alt, st["wt"])
    http(STA_IP, "/api/txpower", {"txp": txp0})
    http(STA_IP, "/api/wifi/keep", {})

    # ---- 2. 儲存設定重開後沒確認 → 退回 ----
    log("\n== 2. 儲存 WiFi 設定(功率改 3),重開後 3 分鐘沒按保持 → 退回 ==")
    new_txp = 3 if w0["txp"] != 3 else 4
    r = http(STA_IP, "/api/wifi", form(w0, txp=new_txp))
    check(f"儲存成功,存檔功率 {http(STA_IP, '/api/wifi')['txp']}", r["ok"] and http(STA_IP, "/api/wifi")["txp"] == new_txp, r)
    http(STA_IP, "/api/reboot", {})
    time.sleep(6)
    st = wait_http(STA_IP, 60)
    check(f"重開後設定試用中,剩 {st['wt'][2] if st else '?'} 秒", st and st["wt"][1] == 1 and 150 <= st["wt"][2] <= 180, st and st["wt"])
    remain = st["wt"][2] if st else 180
    up_before = st["up"] if st else 0
    log(f"  等 {remain + 8:.0f} 秒…")
    time.sleep(remain + 8)
    st = wait_http(STA_IP, 60)
    w = http(STA_IP, "/api/wifi") if st else {}
    ev = [e for e in events(STA_IP) if e[2] == 24 and e[3] == 2] if st else []
    # r2:r1 第一次跑退回時 mDNS 當機板子重開(事件被清掉),這裡一定要確認沒重開
    check(f"沒按保持:存檔功率改回 {w.get('txp')},試用結束,事件 24/2,板子沒有重開(開機秒數 {up_before} → {st and st['up']})",
          st and w.get("txp") == w0["txp"] and st["wt"][1] == 0 and ev and st["up"] > up_before + remain, (st and st["wt"], w.get("txp"), ev))
    n = net()
    check(f"序列埠確認:{n.get('wifi')} ip={n.get('ip')} txp={n.get('txp')}", n.get("wifi") == "sta" and n.get("ip") == STA_IP, n)

    # ---- 3. 儲存設定重開後按保持 ----
    log("\n== 3. 儲存設定重開後按保持 → 保留 ==")
    http(STA_IP, "/api/wifi", form(w0, txp=new_txp))
    http(STA_IP, "/api/reboot", {})
    time.sleep(6)
    st = wait_http(STA_IP, 60)
    check("重開後試用中", st and st["wt"][1] == 1, st and st["wt"])
    http(STA_IP, "/api/wifi/keep", {})
    time.sleep(1)
    st = http(STA_IP, "/api/status")
    check(f"按保持:試用結束,存檔功率 {http(STA_IP, '/api/wifi')['txp']}", st["wt"][1] == 0 and http(STA_IP, "/api/wifi")["txp"] == new_txp, st["wt"])
    http(STA_IP, "/api/reboot", {})
    time.sleep(6)
    st = wait_http(STA_IP, 60)
    check("再重開:沒有試用,功率維持", st and st["wt"][1] == 0 and http(STA_IP, "/api/wifi")["txp"] == new_txp, st and st["wt"])
    r = cmd(f"txp {w0['txp']}", "txp")
    check(f"USB 指令 txp {w0['txp']}:直接存檔不需確認", "saved" in r and http(STA_IP, "/api/wifi")["txp"] == w0["txp"], r)

    # ---- 4. 斷線重連 ----
    log("\n== 4. 家用 WiFi 斷線自動重連 ==")
    cmd("stadrop", "OK")
    time.sleep(1)
    t0 = time.time()
    back = None
    while time.time() - t0 < 30:
        n = net()
        if n.get("ip") == STA_IP:
            back = time.time() - t0
            break
        time.sleep(1)
    check(f"斷線後自動連回({back:.0f} 秒)" if back is not None else "斷線後自動連回", back is not None and wait_http(STA_IP, 10), n)

    def standby_secs():
        r = cmd("fs", "state=")
        for ln in r.splitlines():
            if ln.startswith("state="):
                return float(ln.split()[1].rstrip("s"))
        return -1

    log("\n== 4b. 家用 WiFi 斷線一直連不回來 → 等待秒數後改開熱點(不可重開板子) ==")
    s0 = standby_secs()
    cmd("stadrop hold", "OK")
    time.sleep(w0["tmo"] + 5)
    n = net()
    s1 = standby_secs()
    check(f"斷線 {w0['tmo']} 秒連不回來:改開熱點({n.get('wifi')} {n.get('ip')}),板子沒重開(待機秒數 {s0} → {s1})",
          n.get("wifi") == "ap" and n.get("ip") == AP_IP and s1 > s0 + w0["tmo"], (n, s0, s1))
    subprocess.run(["netsh", "wlan", "connect", "name=HappySuperGG_Plane", "interface=Wi-Fi"], capture_output=True)
    st = wait_http(AP_IP, 30)
    ev = [e for e in events(AP_IP) if e[2] == 24 and e[3] == 4] if st else []
    check("熱點網頁可開,事件 24/4", st and ev, ev)
    subprocess.run(["netsh", "wlan", "disconnect", "interface=Wi-Fi"], capture_output=True)
    wait_boot()
    time.sleep(3)
    check("重開後連回家用 WiFi", wait_http(STA_IP, 40) is not None)
    time.sleep(6)

    # ---- 5. 開關電救援:打斷計數不救援 ----
    def flagged_reboot(wait_after):
        cmd("rescuetest", "OK")
        wait_boot()
        time.sleep(wait_after)

    log("\n== 5. 連續上電計數被打斷(通電超過 5 秒)不救援 ==")
    flagged_reboot(0.3)
    flagged_reboot(6.5)   # 第二次開機後等超過 5 秒 → 計數歸零
    flagged_reboot(0.3)
    time.sleep(3)
    n = net()
    check(f"中間有一次通電超過 5 秒:不救援,仍連家用({n.get('wifi')} {n.get('ssid')})", n.get("wifi") in ("sta", "connecting") and n.get("ssid") == w0["ssid"], n)
    time.sleep(6)

    log("\n== 6. 連續 3 次快速上電 → WiFi 回出廠 ==")
    flagged_reboot(0.3)
    flagged_reboot(0.3)
    flagged_reboot(0.3)
    time.sleep(3)
    n = net()
    check(f"WiFi 回出廠:熱點模式,家用名稱清空,功率 {n.get('txp')}", n.get("wifi") == "ap" and n.get("ssid", "x") == "" and n.get("txp") == "5dBm", n)
    subprocess.run(["netsh", "wlan", "connect", "name=HappySuperGG_Plane", "interface=Wi-Fi"], capture_output=True)
    st = wait_http(AP_IP, 40)
    ev = [e for e in events(AP_IP) if e[2] == 24 and e[3] == 1] if st else []
    wa = http(AP_IP, "/api/wifi") if st else {}
    check("手機(電腦)連出廠熱點 HappySuperGG_Plane 可開網頁,事件 24/1", st and ev and wa.get("apnow") == "HappySuperGG_Plane", (wa.get("apnow"), ev))
    fl = http(AP_IP, "/api/settings?p=0") if st else {}
    check("飛行設定不受影響(沒有未儲存,設定可讀)", st and st["dirty"] == 0 and "shared" in fl)
finally:
    # ---- 還原 ----
    log("\n== 還原測試前的 WiFi 設定 ==")
    n = net()
    if n.get("wifi") == "ap" or n.get("ssid") != w0["ssid"]:
        r = cmd(f"wifi {w0['ssid']} {w0['pw']}", "OK saved")
        wait_boot()
        time.sleep(3)
    st = wait_http(STA_IP, 90)
    if st:
        # r3:網頁存檔是試用,沒重開就按保持清不掉 → r2 以前收尾留下待確認的試用,之後重開沒確認就退回(把 GG 的等待秒數 10 退成 30).
        # 正確做法:存檔 → 重開 → 按保持 → 再重開確認
        http(STA_IP, "/api/wifi", form(w0))
        wait_boot()
        st = wait_http(STA_IP, 60)
        if st and st["wt"][1]:
            http(STA_IP, "/api/wifi/keep", {})
        wait_boot()
        st = wait_http(STA_IP, 60)
    w1 = http(STA_IP, "/api/wifi") if st else {}
    same = st and all(w1.get(k) == w0[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp", "apsfx"))
    check("WiFi 設定與測試前相同,再重開後沒有待確認的試用", same and st["wt"][1] == 0, (w1, st and st["wt"]))
    subprocess.run(["netsh", "wlan", "disconnect", "interface=Wi-Fi"], capture_output=True)
    log(f"\n通過 {passed},失敗 {failed}")
    LOG.close()
sys.exit(1 if failed else 0)
