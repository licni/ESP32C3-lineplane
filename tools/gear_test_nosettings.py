# 版本流水號: r1 (2026-09-13) 機輪收腳:不改設定的實測(GPIO3 舵機脈寬,試收輪,速度,10 秒自動放下,電變頻率不受影響)
import os
import sys
import time

os.environ.setdefault("LP_HOST", sys.argv[1] if len(sys.argv) > 1 else "lineplane.local")
import lp_test as T  # noqa: E402

T.init("gear_test_nosettings")
T.ser_open()
st = T.status()
T.check("待機或結束狀態", T.fstate(st) in ("standby", "done"), T.fstate(st))
sh = T.get("/api/settings?p=0")["shared"]
if sh["gearMaxUs"] - sh["gearMinUs"] > 300:
    # r2:GG 要求避免舵機方向不明時撞壞 —— 板上行程比 1400~1600 大就不做試收輪
    raise SystemExit(f"板上收輪行程 {sh['gearMinUs']}~{sh['gearMaxUs']}µs 太大,為避免撞壞收腳機構不做試收輪測試")
down = sh["gearMaxUs"] if sh["gearReverse"] else sh["gearMinUs"]
up = sh["gearMinUs"] if sh["gearReverse"] else sh["gearMaxUs"]
travel = sh["gearTravelSec"]
T.log(f"  設定:放下 {down}µs 收起 {up}µs 速度 {travel} 秒,PWM 電變 {st['hz']}Hz")

T.cmd("pwmcap gear", expect="OK")
time.sleep(1.0)
p = T.pwm()
T.check(f"GPIO3 實測:放下 {p['high']}µs,週期 {p['period']}µs(50Hz)", abs(p["high"] - down) <= 12 and abs(p["period"] - 20000) <= 200, p)
r = T.post("/api/geartest", on=1)
t0 = time.time()
mids = []
while time.time() - t0 < travel + 1.0:
    s = T.status()
    mids.append((round(time.time() - t0, 2), s["gear"][0], s["gear"][1]))
    time.sleep(0.2)
T.log("  收起過程(秒,位置%,µs):", mids)
T.check("試收輪:慢慢移動(中途有 20~80% 的位置)", r["ok"] and any(20 <= m[1] <= 80 for m in mids), mids)
reach = [m[0] for m in mids if m[1] >= 100]
T.check(f"約 {travel} 秒到收起位置(實際 {reach[0] if reach else '?'} 秒)", reach and abs(reach[0] - travel) <= 0.5, reach[:1])
time.sleep(0.5)
p = T.pwm()
T.check(f"GPIO3 實測:收起 {p['high']}µs", abs(p["high"] - up) <= 12, p)
while time.time() - t0 < 10.3:
    time.sleep(0.2)
s = T.status()
T.check(f"10 秒後自動開始放下(試收輪中={s['gear'][2]},位置 {s['gear'][0]}%)", s["gear"][2] == 0 and s["gear"][0] < 100, s["gear"])
time.sleep(travel + 0.5)
p = T.pwm()
T.check(f"放回下方:GPIO3 實測 {p['high']}µs", abs(p["high"] - down) <= 12, p)
T.post("/api/geartest", on=1)
time.sleep(0.5)
T.post("/api/geartest", on=0)
time.sleep(travel + 0.5)
T.check("收到一半按「放下」立即回放下", T.status()["gear"][0] == 0)

T.cmd("pwmcap on", expect="OK")
time.sleep(1.0)
p = T.pwm()
exp = round(1e6 / st["hz"])
T.check(f"電變 GPIO4(經 GPIO5 量)仍是 {st['hz']}Hz:週期 {p['period']}µs,脈寬 {p['high']}µs", abs(p["period"] - exp) <= exp * 0.01 and abs(p["high"] - 1000) <= 12, p)
T.cmd("pwmcap off", expect="OK")
sys.exit(T.finish())
