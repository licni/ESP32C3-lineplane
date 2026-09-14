# 版本流水號: r1 (2026-09-14) 把 WiFi 設定還原成指定備份,並走完「存檔 → 重開 → 保持」確認流程,確保沒有留下待確認的試用
# (網頁存檔一律試用;沒重開就按保持不會清掉試用,之後重開沒確認會退回. wifi_protect_test r1/r2 的收尾踩到這個)
# 用法: python tools/wifi_restore_confirmed.py 備份.json [板子位址]
import json
import sys
import time
import urllib.parse
import urllib.request

path = sys.argv[1]
ip = sys.argv[2] if len(sys.argv) > 2 else "lineplane.local"


def http(p, data=None, timeout=5):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://{ip}{p}", data=body), timeout=timeout).read())


def wait(timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            return http("/api/status", timeout=3)
        except Exception:  # noqa: BLE001
            time.sleep(1)
    return None


with open(path, encoding="utf-8-sig") as f:
    w0 = json.load(f)
form = {k: w0[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp")}
form["apsfx"] = w0.get("apsfx", "")
print("save", http("/api/wifi", form))
http("/api/reboot", {})
time.sleep(6)
st = wait()
print("after reboot wt", st and st["wt"])
if st and st["wt"][1]:
    print("keep", http("/api/wifi/keep", {}))
time.sleep(1)
http("/api/reboot", {})
time.sleep(6)
st = wait()
w1 = http("/api/wifi")
same = all(w1[k] == w0[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp")) and w1.get("apsfx", "") == w0.get("apsfx", "")
print("再重開後 wt", st["wt"], "設定", {k: w1[k] for k in ("ssid", "host", "tmo", "forceap", "txp", "apsfx")}, "相同" if same else "不同")
sys.exit(0 if same and st["wt"][1] == 0 else 1)
