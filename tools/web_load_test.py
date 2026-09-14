# 版本流水號: r1 (2026-09-13) 網頁負載下的控制迴圈計時測試
# ============================================================================
# 用途:確認「有人開著網頁」時控制迴圈不會被拖慢. 做法:序列埠清除計時紀錄 →
# 用無頭 Edge 實際載入首頁數次(瀏覽器會開多條平行與預連線,比 Python 單連線更貼近手機)
# → 以 5Hz 輪詢狀態 API 一段時間 → 讀回最長執行時間與最長節拍延遲.
# 前提:電腦已連上板子熱點(或同一區網).
# 用法: python tools/web_load_test.py [COM埠] [板子位址] [輪詢秒數]
# ============================================================================
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM20"
HOST = sys.argv[2] if len(sys.argv) > 2 else "192.168.4.1"
POLL_S = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def status():
    return json.loads(urllib.request.urlopen(f"http://{HOST}/api/status", timeout=5).read())


def main():
    s = serial.Serial(PORT, 115200, timeout=0.2)
    s.read(65536)
    s.write(b"timing\n")
    time.sleep(0.5)
    s.read(4096)

    for i in range(3):
        prof = tempfile.mkdtemp(prefix="lp_edge_")   # 全新設定檔:不走快取,每次都整頁重送
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}",
                        "--virtual-time-budget=3000", "--dump-dom", f"http://{HOST}/"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        st = status()
        print(f"edge load {i + 1}: exec={st['ex']}us late={st['late']}ms")

    t_end = time.time() + POLL_S
    worst = 0
    n = 0
    while time.time() < t_end:
        t0 = time.time()
        try:
            st = status()
            worst = max(worst, st["late"])
            n += 1
        except Exception as e:  # noqa: BLE001
            print("poll error", e)
        time.sleep(max(0.0, 0.2 - (time.time() - t0)))
    st = status()
    print(f"after {n} polls: exec={st['ex']}us late={st['late']}ms")
    s.close()


if __name__ == "__main__":
    main()
