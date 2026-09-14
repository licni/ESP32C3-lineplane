# 版本流水號: r2 (2026-09-13) 改為驗證:故障鎖定到重新上電後,恢復回應不再產生錯誤補償
# 舊: r1 (2026-09-13) 觀察:飛行中感測器故障恢復時重新定姿,繞圈向心力下的角度誤差(記錄數據,不是通過/失敗)
# 模擬水平繞圈:偏航 69.2°/秒(單圈 5.2 秒),機身側向讀到向心力 2.68g(線長 18m),韌體扣掉向心力後應該是水平.
# 故障 0.3 秒後恢復 → 韌體用恢復後第一筆加速度(含 2.68g 側向)直接定姿 → 記錄之後 8 秒的機頭/滾轉/補償.
import sys
import time

import lp_test as T

T.init("t8_imu_recover_observe")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")
T.configure(shared={"disturbMode": 2}, profile={"phase1Sec": 25, "flightSec": 30})
T.sim("att 0 0 1.0")
T.gesture_push(2.5)
T.wait_state("flying", 12)
while T.status()["f"]["t"] < 4:
    time.sleep(0.1)
# 繞圈:先給向心力與偏航,讓濾波在正確速度下穩定
T.sim("acc 0 2.68 1.0")
T.sim("gyro 0 0 69.2")
time.sleep(4)
st = T.status()
T.log(f"繞圈穩定後(故障前):機頭 {st['p']:+.1f}° 滾轉 {st['r']:+.1f}° 補償 {st['f']['comp']:+.1f}%")
pre = (st["p"], st["r"])
T.sim("fail 1")
time.sleep(0.3)
T.sim("fail 0")
rows = []
t0 = time.time()
while time.time() - t0 < 8:
    st = T.status()
    rows.append((round(time.time() - t0, 1), st["p"], st["r"], st["f"]["comp"], st["f"]["out"]))
    time.sleep(0.25)
for r in rows:
    T.log(f"  恢復後 {r[0]:4.1f}s  機頭 {r[1]:+6.1f}°  滾轉 {r[2]:+6.1f}°  補償 {r[3]:+5.1f}%  輸出 {r[4]:5.1f}%")
worst = max(rows, key=lambda r: abs(r[1]))
T.log(f"最大機頭讀值 {worst[1]:+.1f}°(恢復後 {worst[0]} 秒),最大補償 {max(abs(r[3]) for r in rows):.1f}%")
T.check("故障前繞圈水平讀值正確(±3°)", abs(pre[0]) < 3 and abs(pre[1]) < 3, pre)
# r2:GG 決定故障後不再採用資料 → 恢復回應也不重新定姿,補償一直是 0,輸出照時間軸
T.check("感測器又有回應後 8 秒:補償一直是 0,輸出一直是第一段 60%,imu=2",
        all(r[3] == 0 and abs(r[4] - 60) < 0.2 for r in rows) and T.status()["imu"] == 2, rows[:3])
T.reboot()
T.restore_and_verify()
sys.exit(T.finish())
