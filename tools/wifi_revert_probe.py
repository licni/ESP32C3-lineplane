# 版本流水號: r1 (2026-09-14) 查 WiFi 設定試用退回時事件紀錄不見:全程記錄序列埠輸出,退回後看開機時間與事件
import json
import sys
import time
import urllib.parse
import urllib.request

import serial

IP = sys.argv[1] if len(sys.argv) > 1 else "lineplane.local"


def http(path, data=None, timeout=5):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://{IP}{path}", data=body), timeout=timeout).read())


ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout, ser.dtr, ser.rts = "COM20", 115200, 0.2, False, False
ser.open()
w0 = http("/api/wifi")
form = {k: w0[k] for k in ("ssid", "pw", "host", "tmo", "forceap")}
form.update(txp=3, apsfx=w0["apsfx"])
print("save", http("/api/wifi", form))
http("/api/reboot", {})
t0 = time.time()
out = ""
revert_at = None
while time.time() - t0 < 240:
    chunk = ser.read(4096).decode("utf-8", "replace")
    if chunk:
        out += chunk
        for ln in chunk.splitlines():
            if ln.strip():
                print(f"[{time.time()-t0:6.1f}] {ln.strip()}", flush=True)
        if "reverted" in chunk and revert_at is None:
            revert_at = time.time()
    if revert_at and time.time() - revert_at > 20:
        break
time.sleep(5)
for _ in range(20):
    try:
        st = http("/api/status")
        break
    except Exception:  # noqa: BLE001
        time.sleep(1)
ev = http("/api/events?since=0")["ev"]
print("uptime", st["up"], "wt", st["wt"], "txp saved", http("/api/wifi")["txp"])
print("events", [(e[1], e[2], e[3], e[4]) for e in ev])
