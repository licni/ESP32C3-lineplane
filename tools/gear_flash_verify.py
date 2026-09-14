# 版本流水號: r1 (2026-09-13) 機輪收腳燒錄後:設定轉移比對,把燒錄前未儲存的值放回(不儲存),新參數預設值
# 用法: python tools/gear_flash_verify.py 燒錄前已儲存狀態.json 燒錄前RAM狀態.json 板子位址
import json
import sys
import time
import urllib.request

import board_backup

saved_path, ram_path, host = sys.argv[1], sys.argv[2], sys.argv[3]
for _ in range(40):
    try:
        st = json.loads(urllib.request.urlopen(f"http://{host}/api/status", timeout=3).read())
        break
    except Exception:  # noqa: BLE001
        time.sleep(1)
with open(saved_path, encoding="utf-8") as f:
    saved = json.load(f)
with open(ram_path, encoding="utf-8") as f:
    ram = json.load(f)
now = board_backup.backup(host)
d = board_backup.diff(saved, now)
print("燒錄後(載入存檔)與燒錄前已儲存值比對:", d or "相同", "| dirty =", st["dirty"])
g = {k: v for k, v in now["shared"].items() if k.startswith("gear")}
print("新參數:", g)
# 放回燒錄前未儲存的值(不儲存)
un = {k: v for k, v in ram["shared"].items() if now["shared"].get(k) != v}
if un:
    body = "\n".join(f"{k}={v}" for k, v in un.items()).encode()
    req = urllib.request.Request(f"http://{host}/api/setmany?p=s", data=body, headers={"Content-Type": "text/plain"})
    print("放回未儲存:", un, json.loads(urllib.request.urlopen(req, timeout=8).read()))
time.sleep(0.5)
st = json.loads(urllib.request.urlopen(f"http://{host}/api/status", timeout=8).read())
d2 = board_backup.diff(ram, board_backup.backup(host))
print("與燒錄前 RAM 狀態比對:", d2 or "相同", "| dirty =", st["dirty"], "| gear =", st.get("gear"))
