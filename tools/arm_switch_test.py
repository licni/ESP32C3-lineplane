# 版本流水號: r1 (2026-09-14) 安全開關 GPIO21 與撞擊斷電連續 2 拍(安全審查後的修正)實機測試
# ============================================================================
# 開發板沒接微動開關:真的腳位是內部上拉 = 沒按. 用序列指令 armsw 0|1|off 覆寫.
#  1. 真腳位(沒接開關):狀態 arm=0,推飛機被拒原因 7,網頁開始被拒
#  2. armsw 1:推飛機進入起飛程序;起飛程序中放開開關不影響(只在開始那一刻檢查);取消
#  3. 手勢關閉(上電自動倒數)+ armsw 0 重開:解鎖後停在待機等開關(原因 8,aw=1),armsw 1 後約 1 秒開始倒數;取消
#  4. 撞擊斷電:飛行中一拍 20g(5ms)不關馬達;連續 15ms 20g 關馬達(原因 5)
# 設定先備份,結束還原比對. 不接馬達.
# ============================================================================
import os
import sys
import time

os.environ.setdefault("LP_HOST", "lineplane.local")
import lp_test as T  # noqa: E402

T.init("arm_switch_test")
T.protect()   # 裡面會送 armsw 1
T.configure(shared={"gestureEnable": 1, "disturbMode": 2, "countdownSec": 20, "crashEnable": 1, "crashG": 14.0})
T.sim("att 0 0")
time.sleep(2.5)

T.log("\n== 1. 真腳位(沒接開關)==")
T.cmd("armsw off", expect="OK")
time.sleep(0.3)
st = T.status()
T.check("狀態:安全開關沒按下(arm=0)", st["f"]["arm"] == 0, st["f"])
n0 = T.ev_total()
T.gesture_push()
time.sleep(0.8)
st = T.status()
T.check(f"推飛機被拒:拒絕原因 7,仍在待機(rj={st['f']['rj']})", T.fstate(st) == "standby" and st["f"]["rj"] == 7, st["f"])
T.check("事件:拒絕原因 7", any(e[2] == 4 and e[3] == 7 for e in T.events_after(n0)), T.events_after(n0))
r = T.post("/api/start")
time.sleep(0.6)
st = T.status()
T.check(f"網頁開始起飛:送出後被拒原因 7,仍待機({r})", T.fstate(st) == "standby" and st["f"]["rj"] == 7, (r, st["f"]))

T.log("\n== 2. armsw 1:可以起飛,起飛程序中放開不影響 ==")
T.cmd("armsw 1", expect="OK")
time.sleep(0.3)
T.check("狀態:安全開關按下(arm=1)", T.status()["f"]["arm"] == 1)
T.gesture_push()
st = T.wait_state(("wait_still", "countdown"), 4)
T.check(f"推飛機進入起飛程序({T.fstate(st)})", T.fstate(st) in ("wait_still", "countdown"), st["f"])
T.cmd("armsw 0", expect="OK")
time.sleep(1.5)
st = T.status()
T.check(f"起飛程序中放開開關:仍在起飛程序({T.fstate(st)}),只在開始那一刻檢查", T.fstate(st) in ("wait_still", "countdown"), st["f"])
T.post("/api/cancel")
time.sleep(0.6)
T.check("已取消回待機", T.fstate() == "standby")

T.log("\n== 3. 上電自動倒數 + 開關沒按:等開關 ==")
T.configure(shared={"gestureEnable": 0, "disturbMode": 2, "countdownSec": 20})
T.cmd("powerontest", expect="OK")
T.cmd("armsw 0", expect="OK")   # 重開後覆寫會清掉;真腳位本來就是沒按
T.post("/api/reboot")
time.sleep(3)
T.wait_back()
time.sleep(5)   # 解鎖 3 秒後判斷
st = T.status()
T.check(f"解鎖後停在待機等開關(aw=1,rj=8),沒有倒數", T.fstate(st) == "standby" and st["f"]["aw"] == 1 and st["f"]["rj"] == 8, st["f"])
T.check("事件:拒絕原因 8(等安全開關)", any(e[2] == 4 and e[3] == 8 for e in T.events(0)["ev"]))
time.sleep(3)
T.check("3 秒後仍在待機", T.fstate() == "standby")
T.cmd("armsw 1", expect="OK")
t0 = time.time()
st = T.wait_state("countdown", 4)
T.check(f"按下開關後約 1 秒開始倒數({time.time() - t0:.1f} 秒)", T.fstate(st) == "countdown" and 0.8 < time.time() - t0 < 2.5, (T.fstate(st), time.time() - t0))
T.post("/api/cancel")
time.sleep(0.6)
T.check("已取消,不再自己倒數(au=1)", T.fstate() == "standby" and T.status()["f"]["au"] == 1)

T.log("\n== 4. 撞擊斷電連續 2 拍 ==")
T.configure(shared={"gestureEnable": 1, "disturbMode": 2, "countdownSec": 5, "crashEnable": 1, "crashG": 14.0},
            profile={"takeoffRamp": 1.0, "noCompSec": 0, "flightSec": 60, "phase1Sec": 30})
T.sim("att 0 0")
time.sleep(2.5)
T.gesture_push()
st = T.wait_state("flying", 12)
T.check(f"起飛進入飛行({T.fstate(st)})", T.fstate(st) == "flying", st["f"])
n0 = T.ev_total()
T.sim("pulse z 20 5")    # 一拍 20g
time.sleep(0.6)
st = T.status()
T.check("單拍 20g:不關馬達,仍在飛行", T.fstate(st) == "flying", st["f"])
T.sim("pulse z 20 15")   # 連續 3 拍
st = T.wait_state("done", 2)
T.check(f"連續 15ms 20g:撞擊斷電(結束原因 5,{T.fstate(st)})", T.fstate(st) == "done" and st["f"]["er"] == 5, st["f"])
T.check("事件:馬達停止原因 5", any(e[2] == 11 and e[3] == 5 for e in T.events_after(n0)), T.events_after(n0))

T.restore_and_verify()
sys.exit(T.finish())
