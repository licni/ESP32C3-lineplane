# 版本流水號: r1 (2026-09-13) 既有回歸測試批次執行,每支跑完把結果附加到 test_logs/regression_<時間>.txt
# 用法: python tools/run_regression.py A|B   (A:設定/曲線/事件/扭轉/水平/延長/電變服務;B:狀態機/DShot/模擬電變)
import os
import re
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IP = socket.gethostbyname("lineplane.local")
PY = sys.executable
BATCH = {
    "A": [["settings_api_test.py", IP], ["curve_ui_test.py", IP], ["event_log_test.py", "COM20", IP],
          ["twist_cancel_test.py", "COM20", IP], ["start_level_test.py", "COM20", IP], ["extend_cap_test.py", "COM20", IP],
          ["esc_service_test.py", IP]],
    "B": [["flight_sm_test.py", "COM20", IP], ["dshot_test.py", "COM20", IP], ["rpm_emulator_test.py", "COM20", IP]],
}[sys.argv[1]]
out = os.path.join(ROOT, "test_logs", time.strftime(f"regression_{sys.argv[1]}_%Y%m%d_%H%M%S.txt"))
for args in BATCH:
    t0 = time.time()
    p = subprocess.run([PY, "-u", os.path.join(HERE, args[0])] + args[1:], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    text = p.stdout + p.stderr
    fails = [l for l in text.splitlines() if "FAIL" in l or "Traceback" in l]
    m = re.findall(r"通過\s*(\d+)[,,]\s*失敗\s*(\d+)", text)
    summary = f"{args[0]}: exit={p.returncode} {'通過 %s 失敗 %s' % m[-1] if m else ''} ({time.time()-t0:.0f} 秒)"
    print(summary, flush=True)
    with open(out, "a", encoding="utf-8") as f:
        f.write(f"==== {summary}\n{text}\n")
    for l in fails[:10]:
        print("   ", l, flush=True)
print("log:", out)
