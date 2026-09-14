# 版本流水號: r1 (2026-09-13) GG 指示:板上收輪舵機行程改 1400~1600µs 並儲存(先確認待機且無未儲存變更,備份,改完比對只差這兩項)
import sys

import board_backup
import lp_test as T

board_backup.require_idle(T.HOST)
before = board_backup.backup(T.HOST)
T.setmany("s", {"gearMinUs": 1400, "gearMaxUs": 1600})
T.save()
after = board_backup.backup(T.HOST)
d = board_backup.diff(before, after)
print("變更:", d)
ok = sorted(x[0] for x in d) == ["shared.gearMaxUs", "shared.gearMinUs"] and after["shared"]["gearMinUs"] == 1400 \
    and after["shared"]["gearMaxUs"] == 1600 and T.status()["dirty"] == 0
print("OK 只改了行程兩項並已儲存" if ok else "FAIL")
sys.exit(0 if ok else 1)
