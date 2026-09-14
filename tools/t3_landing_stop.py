# 版本流水號: r3 (2026-09-14) 起飛前重新定姿(前段抖動超過 1g 把姿態拉向倒飛,F4 偶發拒絕原因 3);撞擊斷電後改用網頁開始起飛;狀態摘要加 rj/arm
# 舊: r2 (2026-09-14) 撞擊斷電後改用網頁開始起飛(推飛機不算手勢);狀態摘要加 rj/arm
# 舊: r1 (2026-09-13) 全功能測試 段 3:降落與停止(感測器模擬走真正的偵測路徑)
# ============================================================================
# 「空中」用 Z 軸 3Hz ±0.25g 晃動模擬(降落靜止判斷看加速度變化 0.1g,晃動就不會判成靜止;
#  不用偏航角速度,因為飛行中向心力補償會把沒有向心力的模擬讀值算歪).
# F1 觸地衝擊:減力中的衝擊不算,低於門檻不算,長時間 G 力不算,短尖峰 ≥ 門檻才停
# F2 完全靜止 1 秒 F3 地面滑行抖動(傾斜時不算,不論提早降落開關) F4 保險時間(提早降落關閉時飛行中抖動不降落)
# F5 觸地提早降落(啟用秒數前不算,傾斜不算,達標開始降落) F6~F9 撞擊斷電(緩啟動/飛行/降落/關閉)與緊急停止
# F10 飛行中感測器故障:補償停止,時間軸照走,觸地判斷失效 → 保險時間停
# ============================================================================
import sys
import time

import lp_test as T

T.init("t3_landing_stop")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")
T.cmd("pwmcap on", expect="OK")

MOTOR = ("takeoff", "flying", "landing")


def of(evs, ty, arg=None):
    return [e for e in evs if e[2] == ty and (arg is None or e[3] == arg)]


def level(air=True):
    T.sim("gyro 0 0 0")
    T.sim("att 0 0 1.0")
    T.sim("vib 0.25 3" if air else "vib 0")


def launch():
    T.sim("vib 0")
    # 重新定姿成水平:前一段 ±1.5g 抖動超過 1g,讀值瞬間是「重力朝上」,姿態濾波被拉向倒飛,
    # 只關抖動不定姿時推飛機會被判角度超過(拒絕原因 3),F4 時好時壞就是這個(2026-09-14 查到)
    T.sim("att 0 0")
    time.sleep(1.0)
    st = T.status()
    if T.fstate(st) == "done" and st["f"]["er"] == 5:
        # 撞擊斷電後推飛機不算手勢(flight r18,安全審查 A3),使用者要按網頁「開始起飛程序」
        time.sleep(1.7)
        T.post("/api/start")
    else:
        T.gesture_push(2.5)
    T.wait_state("wait_still", 2)
    T.wait_state("countdown", 3)
    st = T.wait_state("takeoff", 7, poll=0.02)
    T.sim("vib 0.25 3")   # 起飛後在「空中」
    return st


def wait_t(tt, timeout=45):
    t0 = time.time()
    st = T.status()
    while time.time() - t0 < timeout and T.fstate(st) in MOTOR and st["f"]["t"] < tt:
        time.sleep(0.03)
        st = T.status()
    return st


def wait_done(timeout):
    return T.wait_state("done", timeout, poll=0.05)


def stop_ev(n0):
    s = of(T.events_after(n0), 11)
    return s[0] if s else None


def summary(st, n0):
    e = stop_ev(n0)
    return f"state={T.fstate(st)} er={st['f']['er']} rj={st['f']['rj']} arm={st['f'].get('arm')} t={st['f']['t']} ev={e}"


s, p = T.configure(shared={"disturbMode": 2, "landingTimeout": 20})
level(air=False)
time.sleep(0.5)

# ---- F1 觸地衝擊 ----
T.log("\n== F1 觸地衝擊(門檻 3g,減力 3 秒)==")
n0 = T.ev_total()
launch()
st = wait_t(30.05)
T.check("30 秒開始降落", T.fstate(st) == "landing", summary(st, n0))
wait_t(31.0)
T.sim("pulse z 4 30")
time.sleep(0.4)
st = T.status()
T.check("減力中(降落 1 秒)4g 短衝擊:不算觸地(等減力走完才判斷)", T.fstate(st) == "landing", summary(st, n0))
wait_t(33.5)
T.sim("pulse z 2 30")
time.sleep(0.4)
st = T.status()
T.check(f"減力後 2g 短衝擊(< 門檻 3g):不停,監看頁最近衝擊 {st['imp'][0]:.2f}g/{st['imp'][1]}ms", T.fstate(st) == "landing"
        and 1.7 <= st["imp"][0] <= 2.4, (summary(st, n0), st["imp"]))
T.sim("pulse z 5 200")
time.sleep(0.6)
st = T.status()
T.check("5g 持續 200ms(不是短尖峰,像特技持續 G 力):不停", T.fstate(st) == "landing", summary(st, n0))
# r1 第一次跑:0.6 秒後送 4g 量成 3.59g —— 5g 持續力超過 80ms 後基準恢復追蹤(拉到約 2.6g),
# 0.3 秒時間常數要約 1.5 秒才回到 1g. 這是設計行為(持續力後的基準),測試等 1.5 秒再送.
time.sleep(1.0)
T.sim("pulse z 4 30")
st = wait_done(1.0)
e = stop_ev(n0)
T.check("4g 短衝擊 → 觸地關馬達(er=1),事件記 4.0g / 門檻 3.0g", T.fstate(st) == "done" and st["f"]["er"] == 1 and e and e[3] == 1
        and 3.7 <= e[4] <= 4.4 and e[5] == 3.0, summary(st, n0))
time.sleep(0.3)
st = T.status()
T.check(f"停止後電變 {st['esc']}µs,GPIO5 實測 {st['cap'][2]}µs", st["esc"] == 1000 and abs(st["cap"][2] - 1000) <= 12, st["cap"])

# ---- F2 完全靜止 ----
T.log("\n== F2 完全靜止 1 秒 ==")
n0 = T.ev_total()
launch()
st = wait_t(35.0)
T.check("降落 5 秒(減力已走完)一直晃動:不停", T.fstate(st) == "landing", summary(st, n0))
T.sim("vib 0")
t_still = st["f"]["t"]
st = wait_done(3.0)
e = stop_ev(n0)
T.check(f"停止晃動 → {st['f']['t'] - t_still:.2f} 秒後判定靜止關馬達(er=2),事件記靜止 ≥1.0 秒",
        T.fstate(st) == "done" and st["f"]["er"] == 2 and e and e[3] == 2 and e[4] >= 1.0 and 0.9 <= st["f"]["t"] - t_still <= 1.6,
        summary(st, n0))

# ---- F3 地面滑行抖動(提早降落關閉也有效)----
T.log("\n== F3 降落中地面滑行抖動(門檻 0.8g,持續 1 秒,水平 ±20°;提早降落開關為關)==")
n0 = T.ev_total()
launch()
wait_t(33.5)
T.sim("att 30 0 1.0")
T.sim("vib 1.5 20")
time.sleep(2.0)
st = T.status()
T.check(f"機頭 30°(超過水平容許 20°)+ 抖動 {st['vib']:.2f}g 持續 2 秒:不算滑行", T.fstate(st) == "landing" and st["vib"] >= 0.8
        and st["lvl"] == 0, (summary(st, n0), st["vib"], st["lvl"], st["hold"]))
T.sim("att 0 0 1.0")
t_lvl = time.time()
st = wait_done(3.0)
e = stop_ev(n0)
T.check(f"放平 {time.time()-t_lvl:.2f} 秒後判定地面滑行關馬達(er=3),事件記持續 ≥1.0 秒",
        T.fstate(st) == "done" and st["f"]["er"] == 3 and e and e[3] == 3 and e[4] >= 1.0, summary(st, n0))

# ---- F4 保險時間 + 提早降落關閉時飛行中抖動不降落 ----
T.log("\n== F4 保險時間 8 秒;飛行中(提早降落關閉)水平抖動不降落 ==")
s, p = T.configure(shared={"disturbMode": 2, "landingTimeout": 8})
n0 = T.ev_total()
launch()
wait_t(12)
T.sim("vib 1.5 20")
st = wait_t(18)
T.check(f"提早降落關閉:飛行中水平抖動 {st['vib']:.2f}g 6 秒,持續秒數 {st['hold']:.1f},不降落", T.fstate(st) == "flying" and st["hold"] >= 1.0,
        (summary(st, n0), st["hold"]))
T.sim("vib 0.25 3")
st = wait_t(30.05)
st = wait_done(9.5)
e = stop_ev(n0)
T.check(f"降落 8 秒一直沒觸地 → 保險時間關馬達(er=4),飛行 {st['f']['t']} 秒",
        T.fstate(st) == "done" and st["f"]["er"] == 4 and e and e[3] == 4 and 37.8 <= st["f"]["t"] <= 38.4, summary(st, n0))

# ---- F5 觸地提早降落 ----
T.log("\n== F5 觸地提早降落開啟(起飛後 10 秒啟用,抖動 0.8g 持續 1 秒,水平 ±20°)==")
s, p = T.configure(shared={"disturbMode": 2, "earlyLand": 1, "landingTimeout": 20})
n0 = T.ev_total()
launch()
wait_t(4)
T.sim("vib 1.5 20")
wait_t(7)
T.sim("vib 0.25 3")
st = wait_t(11)
T.check("啟用前(4~7 秒)的抖動:10 秒後也不觸發", T.fstate(st) == "flying", summary(st, n0))
T.sim("att 30 0 1.0")
T.sim("vib 1.5 20")
st = wait_t(14)
T.check(f"啟用後機頭 30° 抖動 3 秒:不觸發(水平 {st['lvl']})", T.fstate(st) == "flying" and st["lvl"] == 0, (summary(st, n0), st["hold"]))
T.sim("att 0 0 1.0")
t_lvl = st["f"]["t"]
time.sleep(0.2)
st2 = T.status()
T.check(f"(前提)放平後姿態水平:機頭 {st2['p']:.1f}° 滾轉 {st2['r']:.1f}°,lvl={st2['lvl']}", st2["lvl"] == 1, (st2["p"], st2["r"]))
st = T.wait_state("landing", 3, poll=0.03)
ls = of(T.events_after(n0), 10)
T.check(f"放平抖動 {st['f']['t'] - t_lvl:.1f} 秒後開始降落(lc=2),事件 10/2 記抖動持續秒數",
        T.fstate(st) == "landing" and st["f"]["lc"] == 2 and ls and ls[0][3] == 2 and ls[0][5] >= 1.0 and st["f"]["t"] - t_lvl <= 2.0,
        (summary(st, n0), ls))
t_land = st["f"]["t"]
st = T.status()
T.check(f"提早降落不是立刻停:減力中(降落 {st['f']['t']-t_land:.1f} 秒)", T.fstate(st) == "landing", summary(st, n0))
st = wait_done(5)
T.check(f"減力 3 秒走完後持續抖動 → 地面滑行關馬達(er=3),降落 {st['f']['t']-t_land:.1f} 秒",
        T.fstate(st) == "done" and st["f"]["er"] == 3 and 2.9 <= st["f"]["t"] - t_land <= 3.5, summary(st, n0))

# ---- F6 撞擊斷電:緩啟動中 ----
T.log("\n== F6 撞擊斷電(門檻 14g):緩啟動中 ==")
s, p = T.configure(shared={"disturbMode": 2}, profile={"takeoffRamp": 4})
level()
n0 = T.ev_total()
launch()
wait_t(0.8)
T.sim("pulse z 11 30")
time.sleep(0.3)
st = T.status()
T.check("緩啟動中 12g 衝擊(< 14g):不停", T.fstate(st) == "takeoff", summary(st, n0))
T.sim("pulse z 13.5 30")
st = wait_done(1)
e = stop_ev(n0)
T.check("緩啟動中 14.5g → 撞擊斷電(er=5),事件記 14.5g / 門檻 14",
        T.fstate(st) == "done" and st["f"]["er"] == 5 and e and e[3] == 5 and 14.3 <= e[4] <= 14.7 and e[5] == 14, summary(st, n0))
time.sleep(0.2)
T.check("撞擊斷電後電變與 GPIO5 回 1000µs", T.status()["esc"] == 1000 and abs(T.status()["cap"][2] - 1000) <= 12)

# ---- F7 撞擊斷電:飛行中與降落中 ----
T.log("\n== F7 撞擊斷電:降落中 ==")
s, p = T.configure(shared={"disturbMode": 2})
n0 = T.ev_total()
launch()
wait_t(31)
T.sim("pulse z 13.5 30")
st = wait_done(1)
T.check("降落中 14.5g → 撞擊斷電(er=5)", T.fstate(st) == "done" and st["f"]["er"] == 5, summary(st, n0))
T.log("\n== F8 撞擊斷電:飛行中 ==")
n0 = T.ev_total()
launch()
wait_t(5)
T.sim("pulse z 13.5 30")
st = wait_done(1)
T.check("飛行中 14.5g → 撞擊斷電(er=5)", T.fstate(st) == "done" and st["f"]["er"] == 5, summary(st, n0))

# ---- F9 撞擊斷電關閉 + 量程飽和事件 + 緊急停止 ----
T.log("\n== F9 撞擊斷電關閉;緊急停止 ==")
s, p = T.configure(shared={"disturbMode": 2, "crashEnable": 0})
n0 = T.ev_total()
launch()
wait_t(4)
T.sim("pulse z 13.5 30")
time.sleep(0.4)
T.sim("pulse z 15.5 30")
time.sleep(0.4)
st = T.status()
sat = of(T.events_after(n0), 19)
T.check("撞擊斷電關閉:14.5g 與 16.5g 都不停", T.fstate(st) == "flying", summary(st, n0))
T.check("16.5g 超出量程:記量程飽和事件(馬達運轉中 arg=1)", sat and sat[0][3] == 1, sat)
t_es = st["f"]["t"]
T.post("/api/estop")
st = wait_done(0.5)
e = stop_ev(n0)
T.check(f"飛行中緊急停止 → 立即結束(er=6),事件記飛行 {e[4]:.1f} 秒" if e else "緊急停止",
        T.fstate(st) == "done" and st["f"]["er"] == 6 and e and abs(e[4] - t_es) < 1.0, summary(st, n0))
n0 = T.ev_total()
launch()
wait_t(0.5)
T.post("/api/estop")
st = wait_done(0.5)
T.check("緩啟動中緊急停止(er=6)", T.fstate(st) == "done" and st["f"]["er"] == 6, summary(st, n0))
n0 = T.ev_total()
launch()
wait_t(31)
T.post("/api/estop")
st = wait_done(0.5)
T.check("降落中緊急停止(er=6)", T.fstate(st) == "done" and st["f"]["er"] == 6, summary(st, n0))
r = T.post("/api/estop")
time.sleep(0.3)
st = T.status()
T.check("結束狀態再按緊急停止:沒有作用(不多記停止事件)", T.fstate(st) == "done" and len(of(T.events_after(n0), 11)) == 1, summary(st, n0))

# ---- F10 飛行中感測器故障 ----
T.log("\n== F10 飛行中感測器故障:補償停止,時間軸照走,觸地判斷失效 → 保險時間 ==")
s, p = T.configure(shared={"disturbMode": 2, "landingTimeout": 6})
n0 = T.ev_total()
launch()
wait_t(5)
T.sim("att 45 0 1.0")
time.sleep(0.4)
st = T.status()
T.check(f"故障前機頭 45°:補償 {st['f']['comp']}%", abs(st["f"]["comp"] - 8) < 0.2, st["f"])
T.sim("fail 1")
time.sleep(0.3)
T.sim("fail 0")   # 故障後馬上又有回應:韌體也不再採用(GG 2026-09-13)
time.sleep(0.4)
st = T.status()
f = of(T.events_after(n0), 12)
T.check(f"故障後(又有回應)補償 0,輸出回基本油門 {st['f']['out']}%,馬達照轉,imu=2,事件 12(arg=1)與 13(不採用 arg=1)",
        T.fstate(st) == "flying" and st["f"]["comp"] == 0 and abs(st["f"]["out"] - 60) < 0.2 and st["imu"] == 2 and f and f[0][3] == 1
        and of(T.events_after(n0), 13, 1), (st["f"], f))
st = wait_t(13.5)
T.check(f"故障中照時間軸換段:t={st['f']['t']} 輸出 {st['f']['out']}%(第二段 80%)", T.fstate(st) == "flying" and abs(st["f"]["out"] - 80) < 0.5, st["f"])
st = wait_t(30.05)
T.check("故障中照時間降落", T.fstate(st) == "landing", summary(st, n0))
st = wait_done(8)
T.check(f"故障中(期間感測器一直有回應)觸地判斷仍停用,保險時間 6 秒關馬達(er=4),飛行 {st['f']['t']} 秒",
        T.fstate(st) == "done" and st["f"]["er"] == 4 and 35.8 <= st["f"]["t"] <= 36.4, summary(st, n0))
T.sim("fail 0")
time.sleep(0.5)
T.check("感測器又有回應也維持故障(imu=2),要重新上電", T.status()["imu"] == 2)
st = T.reboot()
T.check("重新開機後 imu=1", st["imu"] == 1, st["imu"])

T.log("\n== 收尾 ==")
level(air=False)
T.cmd("pwmcap off", expect="OK")
T.restore_and_verify()
sys.exit(T.finish())
