# 版本流水號: r2 (2026-09-14) 安全開關改成「起飛程序照常開始,按下才倒數」(GG)
# 舊: r1 (2026-09-14) 安全開關 GPIO21 與撞擊斷電連續 2 拍(安全審查後的修正)實機測試
# ============================================================================
# 開發板沒接微動開關:真的腳位是內部上拉 = 沒按. 用序列指令 armsw 0|1|off 覆寫.
#  1. 手勢起飛,開關沒按:照常進入等待放穩(不拒絕),放穩後停住等開關(al=0,事件 28/0),不倒數;
#     按下 → 事件 28/2,馬上開始倒數;倒數中放開不影響;取消
#  2. 開始當下開關已按著(飛場應急短路):放穩後直接倒數,沒有「等開關」事件;取消
#  3. 放穩前短按一下就放開:記住,放穩後開始倒數(倒數開始時開關是放開的);取消
#  4. 網頁「開始起飛程序」開關沒按:送出成功,等待放穩並等開關;按下後倒數;取消
#  5. 倒數中外力介入 → 退回等待放穩 → 重新放穩後繼續倒數,不必再按開關;取消
#  6. 上電後直接倒數 + 開關沒按:解鎖後待機等(aw=1,al=0,事件 28/1),燈慢閃,不倒數;按下 → 開始倒數;取消
#  7. 上電後直接倒數 + 開關按著重開:解鎖後直接倒數,沒有「等開關」事件;取消
#  8. 撞擊斷電:飛行中一拍 20g 不關馬達;連續 15ms 20g 關馬達(原因 5)
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


def ev_types(n0, ty):
    return [e[3] for e in T.events_after(n0) if e[2] == ty]


def cancel():
    T.post("/api/cancel")
    time.sleep(0.6)
    return T.fstate()


def inner(runs):
    return runs[1:-1] if len(runs) > 2 else []


T.log("\n== 1. 手勢起飛,開關沒按:照常開始,放穩後等開關 ==")
T.cmd("armsw 0", expect="OK")
time.sleep(0.3)
n0 = T.ev_total()
T.gesture_push()
st = T.wait_state("wait_still", 3)
T.check(f"推飛機照常進入等待放穩(不拒絕,狀態 {T.fstate(st)},rj={st['f']['rj']})", T.fstate(st) == "wait_still" and st["f"]["rj"] != 7, st["f"])
time.sleep(2.5)
st = T.status()
T.check(f"放穩後停在等待放穩等開關(al={st['f']['al']},放穩 {st['f']['set']} 秒)", T.fstate(st) == "wait_still" and st["f"]["al"] == 0 and st["f"]["set"] >= 1, st["f"])
T.check("事件 28/0:已放穩,等安全開關", 0 in ev_types(n0, 28), T.events_after(n0))
time.sleep(3)
T.check("再等 3 秒仍不倒數", T.fstate() == "wait_still")
t0 = time.time()
T.cmd("armsw 1", expect="OK")
st = T.wait_state("countdown", 3)
dt = time.time() - t0
T.check(f"按下開關後開始倒數({dt:.2f} 秒,al={st['f']['al']})", T.fstate(st) == "countdown" and dt < 1.2 and st["f"]["al"] == 1, (T.fstate(st), dt))
T.check("事件 28/2:安全開關按下", 2 in ev_types(n0, 28), T.events_after(n0))
T.cmd("armsw 0", expect="OK")
time.sleep(1.5)
T.check("倒數中放開開關:繼續倒數", T.fstate() == "countdown")
T.check("取消回待機", cancel() == "standby")

T.log("\n== 2. 開始當下開關已按著:放穩後直接倒數 ==")
T.cmd("armsw 1", expect="OK")
time.sleep(0.3)
n0 = T.ev_total()
T.gesture_push()
st = T.wait_state("countdown", 4)
T.check(f"放穩後直接倒數({T.fstate(st)})", T.fstate(st) == "countdown", st["f"])
T.check(f"沒有等開關事件 {ev_types(n0, 28)}", 0 not in ev_types(n0, 28), T.events_after(n0))
T.check("取消回待機", cancel() == "standby")

T.log("\n== 3. 放穩前短按一下就放開:記住 ==")
T.cmd("armsw 0", expect="OK")
time.sleep(0.3)
n0 = T.ev_total()
T.gesture_push()
T.cmd("armsw 1", expect="OK")
time.sleep(0.3)
T.cmd("armsw 0", expect="OK")
st = T.wait_state("countdown", 4)
T.check(f"放開之後放穩,照樣開始倒數({T.fstate(st)},開關 arm={st['f']['arm']})", T.fstate(st) == "countdown" and st["f"]["arm"] == 0, st["f"])
T.check("事件 28/2:安全開關按下", 2 in ev_types(n0, 28), T.events_after(n0))
T.check("取消回待機", cancel() == "standby")

T.log("\n== 4. 網頁開始起飛程序,開關沒按 ==")
time.sleep(1.8)
n0 = T.ev_total()
r = T.post("/api/start")
st = T.wait_state("wait_still", 3)
T.check(f"網頁開始成功,進入等待放穩({r['code']},{T.fstate(st)})", r["ok"] and T.fstate(st) == "wait_still", (r, st["f"]))
time.sleep(2.5)
st = T.status()
T.check(f"放穩後等開關(al={st['f']['al']})", T.fstate(st) == "wait_still" and st["f"]["al"] == 0, st["f"])
T.cmd("armsw 1", expect="OK")
st = T.wait_state("countdown", 3)
T.check(f"按下開關後倒數({T.fstate(st)})", T.fstate(st) == "countdown", st["f"])
T.check("取消回待機", cancel() == "standby")

T.log("\n== 5. 倒數中外力介入:重新放穩後繼續,不必再按開關 ==")
T.configure(shared={"gestureEnable": 1, "disturbMode": 0, "extendSec": 5, "countdownSec": 20})
T.sim("att 0 0")
time.sleep(2.0)
T.cmd("armsw 1", expect="OK")
T.gesture_push()
st = T.wait_state("countdown", 4)
T.check(f"進入倒數({T.fstate(st)})", T.fstate(st) == "countdown", st["f"])
T.cmd("armsw 0", expect="OK")
time.sleep(0.3)
n0 = T.ev_total()
T.cmd("disturb", expect="OK")
st = T.wait_state("wait_still", 2)
T.check(f"外力介入退回等待放穩({T.fstate(st)})", T.fstate(st) == "wait_still", st["f"])
st = T.wait_state("countdown", 4)
T.check(f"開關放開著,重新放穩後繼續倒數({T.fstate(st)},arm={st['f']['arm']})", T.fstate(st) == "countdown" and st["f"]["arm"] == 0, st["f"])
T.check(f"事件:延長後繼續倒數,沒有等開關 {ev_types(n0, 5)} {ev_types(n0, 28)}", 1 in ev_types(n0, 5) and 0 not in ev_types(n0, 28), T.events_after(n0))
T.check("取消回待機", cancel() == "standby")

T.log("\n== 6. 上電後直接倒數,開關沒按:等開關 ==")
T.configure(shared={"gestureEnable": 0, "disturbMode": 2, "countdownSec": 20})
T.cmd("powerontest", expect="OK")
T.cmd("armsw 0", expect="OK")   # 覆寫存在 RTC,軟體重開保留
T.post("/api/reboot")
time.sleep(3)
T.wait_back()
time.sleep(5)   # 解鎖 3 秒後判斷
st = T.status()
T.check(f"解鎖後待機等開關(aw={st['f']['aw']},al={st['f']['al']}),沒有倒數", T.fstate(st) == "standby" and st["f"]["aw"] == 1 and st["f"]["al"] == 0, st["f"])
ev = T.events(0)["ev"]
T.check("事件 28/1:上電自動倒數等安全開關;沒有拒絕原因 8", any(e[2] == 28 and e[3] == 1 for e in ev) and not any(e[2] == 4 and e[3] == 8 for e in ev), ev)
runs = T.led_capture(3200)
T.log("  等開關的燈:", runs)
T.check("等開關:燈慢閃(每段約 500ms)", len(inner(runs)) >= 4 and all(abs(r[1] - 500) <= 25 for r in inner(runs)), runs)
T.check("仍在待機,沒有倒數", T.fstate() == "standby")
t0 = time.time()
T.cmd("armsw 1", expect="OK")
st = T.wait_state("countdown", 3)
dt = time.time() - t0
T.check(f"按下開關後開始倒數({dt:.2f} 秒)", T.fstate(st) == "countdown" and dt < 1.5, (T.fstate(st), dt))
T.check("取消後不再自己倒數(au=1)", cancel() == "standby" and T.status()["f"]["au"] == 1)

T.log("\n== 7. 上電後直接倒數,開關按著重開:直接倒數 ==")
T.cmd("powerontest", expect="OK")
T.cmd("armsw 1", expect="OK")
T.post("/api/reboot")
time.sleep(3)
T.wait_back()
st = T.wait_state("countdown", 8)
T.check(f"解鎖後直接倒數({T.fstate(st)})", T.fstate(st) == "countdown", st["f"])
T.check("沒有等開關事件", not any(e[2] == 28 and e[3] == 1 for e in T.events(0)["ev"]))
T.check("取消回待機", cancel() == "standby")

T.log("\n== 8. 撞擊斷電連續 2 拍 ==")
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
