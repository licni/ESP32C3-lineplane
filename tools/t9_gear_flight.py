# 版本流水號: r1 (2026-09-13) 機輪收腳飛行測試:收放時機,緊急停止/撞擊放輪,提早降落開啟不收,關閉不收,反轉,試收輪限制,行程驗證
# GPIO3 自己的電位量脈寬(pwmcap gear). 會改設定:確認待機且無未儲存變更 → 備份 → 測試 → 還原比對.
import os
import sys
import time

if len(sys.argv) > 1:
    os.environ["LP_HOST"] = sys.argv[1]
import lp_test as T  # noqa: E402

T.init("t9_gear_flight")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")
T.cmd("pwmcap gear", expect="OK")

MOTOR = ("takeoff", "flying", "landing")


def of(evs, ty, arg=None):
    return [e for e in evs if e[2] == ty and (arg is None or e[3] == arg)]


def launch():
    T.sim("vib 0")
    T.sim("att 0 0 1.0")
    T.gesture_push(2.5)
    T.wait_state("wait_still", 2)
    T.wait_state("countdown", 3)
    st = T.wait_state("takeoff", 7, poll=0.02)
    T.sim("vib 0.25 3")   # 空中(降落時不會判成靜止)
    return st


def wait_t(tt, timeout=45):
    t0 = time.time()
    st = T.status()
    while time.time() - t0 < timeout and T.fstate(st) in MOTOR and st["f"]["t"] < tt:
        time.sleep(0.03)
        st = T.status()
    return st


def cap():
    time.sleep(0.25)
    return T.pwm()["high"]


G = {"disturbMode": 2, "gearEnable": 1, "gearRetractSec": 4, "gearTravelSec": 1.0, "earlyLand": 0, "gearReverse": 0,
     "gearMinUs": 1400, "gearMaxUs": 1600, "landingTimeout": 8}   # 小行程(GG:避免舵機方向不明時撞壞)

# ---- A. 正常飛行 ----
T.log("\n== A. 起飛 4 秒收輪(舵機 1 秒),30 秒降落開始放輪 ==")
T.configure(shared=G)
n0 = T.ev_total()
launch()
st = wait_t(3.5)
T.check(f"起飛 3.5 秒:輪子放下(位置 {st['gear'][0]}%,GPIO3 {cap()}µs)", st["gear"][0] == 0, st["gear"])
st = wait_t(4.3)
T.check(f"4 秒後開始收(位置 {st['gear'][0]}%)", 0 < st["gear"][0] < 100 or st["gear"][0] == 100, st["gear"])
st = wait_t(5.3)
g = of(T.events_after(n0), 23, 1)
T.check(f"約 5 秒收到位,GPIO3 {cap()}µs,事件「收輪」記飛行 {g[0][4]:.1f} 秒" if g else "收輪事件", st["gear"][0] == 100 and g and 3.9 <= g[0][4] <= 4.2, (st["gear"], g))
st = wait_t(30.05)
T.check("飛行中一直收著", T.fstate(st) == "landing" or st["gear"][0] == 100, st["gear"])
st = wait_t(30.4)
T.check(f"降落開始(減力中)立即放輪:位置 {st['gear'][0]}%", T.fstate(st) == "landing" and st["gear"][0] < 100, (T.fstate(st), st["gear"]))
st = wait_t(31.3)
d = of(T.events_after(n0), 23, 0)
T.check(f"1 秒內放到底,GPIO3 {cap()}µs,事件「放輪」記飛行 {d[0][4]:.1f} 秒" if d else "放輪事件", st["gear"][0] == 0 and d and 29.9 <= d[0][4] <= 30.2, (st["gear"], d))
T.post("/api/estop")
T.wait_state("done", 2)

# ---- B. 緊急停止 / 撞擊 立即放輪 ----
for how in ("estop", "crash"):
    T.log(f"\n== B. 收輪後{'緊急停止' if how == 'estop' else '撞擊斷電'} ==")
    n0 = T.ev_total()
    launch()
    wait_t(5.5)
    if how == "estop":
        T.post("/api/estop")
    else:
        T.sim("pulse z 13.5 30")
    st = T.wait_state("done", 1)
    time.sleep(0.2)
    s1 = T.status()
    T.check(f"{'緊急停止' if how == 'estop' else '撞擊斷電'}後立即放輪(0.2 秒位置 {s1['gear'][0]}%)", T.fstate(st) == "done" and s1["gear"][0] < 100, s1["gear"])
    time.sleep(1.0)
    T.check(f"放到底 GPIO3 {cap()}µs,事件放輪", T.status()["gear"][0] == 0 and of(T.events_after(n0), 23, 0))

# ---- C. 試收輪限制 ----
T.log("\n== C. 試收輪只在待機可用 ==")
T.sim("vib 0")
T.gesture_push(2.5)
T.wait_state("countdown", 4)
r = T.post("/api/geartest", on=1)
T.check("倒數中試收輪被拒", not r["ok"], r)
T.post("/api/cancel")
time.sleep(0.3)
r = T.post("/api/geartest", on=1)
time.sleep(0.3)
T.gesture_push(2.5, rearm=1.8)
st = T.wait_state("wait_still", 2)
time.sleep(0.3)
T.check(f"試收輪中做手勢進入起飛程序 → 立即放輪(位置 {T.status()['gear'][0]}%,試收輪中 {T.status()['gear'][2]})",
        T.fstate(st) == "wait_still" and T.status()["gear"][2] == 0, T.status()["gear"])
T.post("/api/cancel")

# ---- D. 提早降落開啟 → 不收 ----
T.log("\n== D. 觸地提早降落開啟時不收輪;收輪關閉時不收 ==")
for over, name in (({"earlyLand": 1}, "提早降落開啟"), ({"gearEnable": 0}, "收輪關閉")):
    T.configure(shared=dict(G, **over))
    n0 = T.ev_total()
    launch()
    st = wait_t(7)
    T.check(f"{name}:起飛 7 秒輪子仍放下(位置 {st['gear'][0]}%,GPIO3 {cap()}µs),沒有收輪事件",
            st["gear"][0] == 0 and not of(T.events_after(n0), 23, 1), st["gear"])
    T.post("/api/estop")
    T.wait_state("done", 2)

# ---- E. 反轉 ----
T.log("\n== E. 舵機反轉 ==")
T.configure(shared=dict(G, gearReverse=1, gearMinUs=1420, gearMaxUs=1580))
time.sleep(0.5)
T.check(f"反轉:待機放下位置在上限 1580µs(GPIO3 {cap()}µs)", abs(T.pwm()["high"] - 1580) <= 12)
launch()
wait_t(5.5)
T.check(f"反轉:收起位置在下限 1420µs(GPIO3 {cap()}µs)", abs(T.pwm()["high"] - 1420) <= 12)
T.post("/api/estop")
T.wait_state("done", 2)

# ---- F. 行程驗證 ----
r = T.post("/api/set", p="s", k="gearMaxUs", v=1500)
r2 = T.post("/api/set", p="s", k="gearMinUs", v=1450)   # 下限 1450,上限 1500:差不到 100
T.check("行程上限小於下限 +100 被拒(gearrange)", r2["code"] == "gearrange" or r["code"] == "gearrange", (r, r2))
T.post("/api/revert")

T.log("\n== 收尾 ==")
T.cmd("pwmcap off", expect="OK")
T.sim("vib 0")
T.restore_and_verify()
sys.exit(T.finish())
