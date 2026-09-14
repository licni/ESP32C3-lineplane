# 版本流水號: r1 (2026-09-13) 全功能測試 段 2:飛行油門時間軸,補償曲線,上下限,GPIO5 實測脈寬
# ============================================================================
# A. 三種換段方式的時間軸(水平,補償 0):緩啟動不夾下限,第一段,換段,第二段;電變脈寬與 GPIO5 實測脈寬
# B. 補償曲線:起飛後不補償,朝上/朝下各角度的補償值 = 曲線內插,死區,夾上下限,第二段共用曲線,降落中不補償
# 會改設定:開頭確認待機並備份,結尾還原並比對.
# ============================================================================
import sys
import time

import lp_test as T

T.init("t2_flight_throttle")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")
T.cmd("pwmcap on", expect="OK")


def level():
    T.sim("gyro 0 0 0")
    T.sim("vib 0")
    T.sim("att 0 0 1.0")


def launch():
    T.gesture_push(2.5)
    T.wait_state("wait_still", 2)
    T.wait_state("countdown", 3)
    return T.wait_state("takeoff", 7, poll=0.02)


def expected_base(t, p):
    p1, p2, t1, ramp = p["phase1Pct"], p["phase2Pct"], p["phase1Sec"], p["phaseRamp"]
    m = p["phaseMode"]
    if m == 0:
        return p1 if t < t1 else p2
    if m == 2:
        return p1 + (p2 - p1) * t / t1 if t < t1 else p2
    if t < t1:
        return p1
    return p1 + (p2 - p1) * min(1.0, (t - t1) / ramp)


def sample(st):
    f = st["f"]
    return {"s": T.STATE[f["s"]], "t": f["t"], "out": f["out"], "base": f["base"], "comp": f["comp"],
            "esc": st["esc"], "cap": st["cap"][2], "p": st["p"], "er": f["er"], "lc": f["lc"], "ph": f["ph"]}


esc_min = T.get("/api/settings?p=0")["shared"]["escMinUs"]
esc_max = T.get("/api/settings?p=0")["shared"]["escMaxUs"]
span = esc_max - esc_min
T.log(f"  電變脈寬 0%={esc_min}µs 100%={esc_max}µs,PWM {T.status()['hz']}Hz")

# ============ A. 時間軸 ============
for mode, name, full in ((1, "直接跳(有過渡)", True), (0, "直接跳", False), (2, "平均分攤", False)):
    s, p = T.configure(shared={"disturbMode": 2}, profile={"phaseMode": mode})
    level()
    time.sleep(0.5)
    T.log(f"\n== A{mode}. 換段方式「{name}」:第一段 60% 10 秒,第二段 80%,換段加力 3 秒,緩啟動 2 秒,總 30 秒 ==")
    st = launch()
    T.check("馬達啟動(緩啟動)", T.fstate(st) == "takeoff", T.fstate(st))
    rows = []
    t_end = time.time() + (40 if full else 14)
    while time.time() < t_end:
        st = T.status()
        rows.append(sample(st))
        if rows[-1]["s"] == "done":
            break
        time.sleep(0.1)
    if not full:
        T.post("/api/estop")
    # 時間軸
    bad = []
    for r in rows:
        if r["s"] not in ("takeoff", "flying"):
            continue
        exp = expected_base(r["t"], p)
        exp = exp * r["t"] / p["takeoffRamp"] if r["t"] < p["takeoffRamp"] else max(p["minPct"], min(p["maxPct"], exp))
        if abs(r["out"] - exp) > 2.5 and abs(r["t"] - p["phase1Sec"]) > 0.15:
            bad.append((r["s"], r["t"], r["out"], round(exp, 1)))
    T.check(f"油門符合時間軸(誤差 <2.5%,{len(rows)} 筆)", not bad, bad[:6])
    first = [r for r in rows if r["s"] == "takeoff"]
    T.check(f"緩啟動從低油門開始,不先跳到下限 30%(第一筆 t={first[0]['t']} out={first[0]['out']})" if first else "緩啟動有取樣",
            first and first[0]["out"] < 25, first[:2])
    # 電變脈寬(程式值)與 GPIO5 實測
    bad_esc = [(r["t"], r["out"], r["esc"]) for r in rows if r["s"] in ("takeoff", "flying", "landing")
               and abs(r["esc"] - (esc_min + span * r["out"] / 100)) > 1.6]
    T.check("電變脈寬 = 0% 脈寬 + 油門 × 行程(±1.5µs)", not bad_esc, bad_esc[:5])
    bad_cap = []
    for i in range(1, len(rows) - 1):
        r = rows[i]
        if r["s"] not in ("takeoff", "flying", "landing"):
            continue
        slope = abs(rows[i + 1]["esc"] - rows[i - 1]["esc"]) / 0.2   # µs/秒
        tol = 12 + 0.25 * slope
        if abs(r["cap"] - r["esc"]) > tol:
            bad_cap.append((r["t"], r["esc"], r["cap"], round(tol)))
    T.check(f"GPIO5 實測脈寬跟著輸出(穩定時 ±12µs,變化中放寬)", len(bad_cap) <= 1, bad_cap[:6])
    steady = [r for r in rows if r["s"] == "flying" and 4 < r["t"] < 9.5]
    if steady:
        caps = [r["cap"] for r in steady]
        T.log(f"  第一段 60% 穩定期實測脈寬 {min(caps)}~{max(caps)}µs(設定 {esc_min + span * 0.6:.0f})")
    if mode == 1:
        p2 = [r for r in rows if r["s"] == "flying" and 13.5 < r["t"] < 29.5]
        T.check("第二段 80%", p2 and all(abs(r["out"] - 80) < 0.6 for r in p2), p2[:2])
        ph = [r for r in rows if r["s"] == "flying"]
        T.check("段別:10 秒前 ph=1,之後 ph=2", all((r["ph"] == 1) == (r["t"] < 9.95) for r in ph if abs(r["t"] - 10) > 0.1),
                [(r["t"], r["ph"]) for r in ph if (r["ph"] == 1) != (r["t"] < 10)][:4])
        land = [r for r in rows if r["s"] == "landing"]
        T.check(f"30 秒開始降落(lc=1),3 秒從 80% 減到 30%",
                land and land[0]["lc"] == 1 and 29.8 <= land[0]["t"] <= 30.5 and land[0]["out"] > 70 and any(abs(r["out"] - 30) < 1 for r in land),
                [(r["t"], r["out"]) for r in land[:3] + land[-2:]])
        bad_l = [(r["t"], r["out"]) for r in land if r["t"] < 33 and abs(r["out"] - (80 - 50 * (r["t"] - 30) / 3)) > 3]
        T.check("降落減力線性", not bad_l, bad_l[:4])
        last = rows[-1]
        T.check(f"降落後(桌上靜止)結束,電變回 {esc_min}µs,GPIO5 實測 {T.status()['cap'][2]}µs",
                last["s"] == "done" and T.status()["esc"] == esc_min and abs(T.status()["cap"][2] - esc_min) <= 12, last)
    time.sleep(0.5)
    T.check("停止後 GPIO5 實測回到 0% 脈寬", abs(T.status()["cap"][2] - esc_min) <= 12, T.status()["cap"])

# ============ B. 補償曲線 ============
T.log("\n== B. 補償曲線:第一段 60%(20 秒),第二段 90%,下限 40,上限 95,起飛後 3 秒不補償 ==")
s, p = T.configure(shared={"disturbMode": 2},
                   profile={"phaseMode": 0, "phase1Sec": 20, "phase2Pct": 90, "minPct": 40, "maxPct": 95})
level()
time.sleep(0.5)
st = launch()
T.wait_state("flying", 3, poll=0.02)
T.sim("att 60 0 1.0")
time.sleep(0.3)
st = T.status()
r = sample(st)
T.check(f"起飛後 3 秒內(t={r['t']})機頭 60°:不補償(comp=0,out=60)", r["t"] < 3 and r["comp"] == 0 and abs(r["out"] - 60) < 0.2, r)
while T.status()["f"]["t"] < 3.3:
    time.sleep(0.05)
pitches = [60, 0, 10, 20, 25, 30, 45, 57.5, 70, 80, 85, -2, -3, -10, -30, -45, -60, -75, -85]
bad = []
for ang in pitches:
    T.sim(f"att {ang} 0 1.0")
    time.sleep(0.35)
    r = sample(T.status())
    exp_c = T.curve_comp(p, r["p"])
    exp_o = max(p["minPct"], min(p["maxPct"], 60 + exp_c))
    ok = abs(r["comp"] - exp_c) <= 0.15 and abs(r["out"] - exp_o) <= 0.15 and abs(r["cap"] - (esc_min + span * exp_o / 100)) <= 12
    T.log(f"  機頭 {r['p']:+6.1f}°  補償 {r['comp']:+6.1f}(預期 {exp_c:+6.2f})  輸出 {r['out']:5.1f}%(預期 {exp_o:5.1f})"
          f"  電變 {r['esc']}µs  GPIO5 {r['cap']}µs  t={r['t']}  {'OK' if ok else 'FAIL'}")
    if not ok or r["s"] != "flying" or r["t"] >= 20:
        bad.append((ang, r))
T.check("第一段:朝上/朝下各角度補償 = 曲線內插,死區內 0,−85° 被下限 40% 夾住,GPIO5 實測脈寬相符", not bad, bad[:3])
while T.status()["f"]["t"] < 20.3:
    time.sleep(0.1)
bad = []
for ang in (0, 20, 30, 45, 85, -30, -85):
    T.sim(f"att {ang} 0 1.0")
    time.sleep(0.35)
    r = sample(T.status())
    exp_c = T.curve_comp(p, r["p"])
    exp_o = max(p["minPct"], min(p["maxPct"], 90 + exp_c))
    ok = abs(r["comp"] - exp_c) <= 0.15 and abs(r["out"] - exp_o) <= 0.15 and abs(r["cap"] - (esc_min + span * exp_o / 100)) <= 12
    T.log(f"  [第二段] 機頭 {r['p']:+6.1f}°  補償 {r['comp']:+6.1f}  輸出 {r['out']:5.1f}%(預期 {exp_o:5.1f})  GPIO5 {r['cap']}µs  ph={r['ph']}  {'OK' if ok else 'FAIL'}")
    if not ok or r["ph"] != 2:
        bad.append((ang, r))
T.check("第二段共用同一條曲線,+30° 以上被上限 95% 夾住", not bad, bad[:3])
T.sim("att 45 0 1.0")
st = T.wait_state("landing", 12, poll=0.05)
time.sleep(0.5)
r = sample(T.status())
T.check(f"降落中不補償(機頭 45°,comp={r['comp']},out={r['out']})", r["s"] == "landing" and r["comp"] == 0 and r["out"] < 90, r)
level()
st = T.wait_state("done", 10)
T.check("降落結束", T.fstate(st) == "done", st["f"])

T.log("\n== 收尾 ==")
T.cmd("pwmcap off", expect="OK")
T.restore_and_verify()
sys.exit(T.finish())
