# 版本流水號: r1 (2026-09-14) 燒錄後把燒錄前「未儲存」的值放回(不儲存):共用設定,各組風格,名稱,飛行使用組別
# GG 2026-09-14:板上有未儲存變更也直接燒. 燒錄前 board_backup.py save 記下 RAM 值,燒完跑這支.
# 用法: python tools/restore_unsaved.py 燒錄前RAM備份.json [板子位址]
import json
import sys
import time
import urllib.parse
import urllib.request

import board_backup

path = sys.argv[1]
host = sys.argv[2] if len(sys.argv) > 2 else "lineplane.local"
for _ in range(40):
    try:
        urllib.request.urlopen(f"http://{host}/api/status", timeout=3)
        break
    except Exception:  # noqa: BLE001
        time.sleep(1)
with open(path, encoding="utf-8") as f:
    ram = json.load(f)
now = board_backup.backup(host)


def post(p, body=None, data=None, ctype=None):
    b = body if body is not None else urllib.parse.urlencode(data or {}).encode()
    req = urllib.request.Request(f"http://{host}{p}", data=b)
    if ctype:
        req.add_header("Content-Type", ctype)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


changed = []
sh = {k: v for k, v in ram["shared"].items() if now["shared"].get(k) != v}
if sh:
    r = post("/api/setmany?p=s", "\n".join(f"{k}={v}" for k, v in sh.items()).encode(), ctype="text/plain")
    changed.append(("shared", sh, r["code"]))
for i, (pr, pn) in enumerate(zip(ram["profiles"], now["profiles"])):
    d = {k: v for k, v in pr.items() if pn.get(k) != v}
    if d:
        r = post(f"/api/setmany?p={i}", "\n".join(f"{k}={v}" for k, v in d.items()).encode(), ctype="text/plain")
        changed.append((f"p{i}", d, r["code"]))
for i, (a, b) in enumerate(zip(ram["names"], now["names"])):
    if a != b:
        changed.append((f"name{i}", a, post("/api/name", data={"p": i, "name": a})["code"]))
if ram["active"] != now["active"]:
    changed.append(("active", ram["active"], post("/api/select", data={"p": ram["active"]})["code"]))
print("放回的未儲存值:", changed or "沒有")
d = board_backup.diff(ram, board_backup.backup(host))
st = json.loads(urllib.request.urlopen(f"http://{host}/api/status", timeout=8).read())
print("與燒錄前 RAM 狀態比對:", d or "相同", "| dirty =", st["dirty"])
sys.exit(1 if d else 0)
