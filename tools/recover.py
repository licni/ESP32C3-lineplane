# 版本流水號: r1 (2026-09-13) 測試中斷時救援:緊急停止,關閉模擬與量測,用指定備份檔還原並比對
# 用法: python tools/recover.py 備份檔.json
import json
import sys
import time

import board_backup
import lp_test as T

print(T.post("/api/estop"))
time.sleep(0.5)
T.post("/api/cancel")
time.sleep(0.3)
print(T.cmd("sim off", expect="sim"))
print(T.cmd("pwmcap off", expect="OK"))
st = T.status()
print("state", T.fstate(st), "er", st["f"]["er"], "dirty", st["dirty"])
with open(sys.argv[1], encoding="utf-8") as f:
    snap = json.load(f)
print(board_backup.restore(T.HOST, snap) or "restored")
print(board_backup.diff(snap, board_backup.backup(T.HOST)) or "相同")
