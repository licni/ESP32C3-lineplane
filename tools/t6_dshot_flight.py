# 版本流水號: r1 (2026-09-13) 全功能測試 段 6:DShot300 + 轉速回傳下的完整飛行(GPIO5 模擬電變解出線上油門值)
# 會改協定並重開機;結尾還原設定,重開機回原協定,並用 GPIO5 量脈寬確認.
import sys
import time

import lp_test as T

T.init("t6_dshot_flight")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")


def emu():
    r = T.cmd("emu", expect="emu frames")
    for line in r.splitlines():
        if line.startswith("emu frames"):
            return {k: int(v) for k, v in (x.split("=") for x in line.split()[1:])}
    raise RuntimeError(r)


def dshot_of(pct):
    return 0 if pct <= 0 else round(48 + 1999 * min(pct, 100) / 100)


T.configure(shared={"disturbMode": 2, "escProtocol": 2, "escRpm": 1, "motorPoles": 14})
T.post("/api/reboot")
T.wait_back()
time.sleep(3)
st = T.status()
T.check(f"重開機後協定 DShot300(proto={st['proto']}),轉速回傳啟用(rpm[0]={st['rpm'][0]}),待機送停止(dsh={st['dsh']})",
        st["proto"] == 2 and st["rpm"][0] == 1 and st["dsh"] == 0, (st["proto"], st["rpm"], st["dsh"]))
r = T.cmd("escemu 4285", expect="escemu")
T.check("GPIO5 模擬電變啟動(回傳週期 4285µs = 14 極 2000RPM)", "OK escemu on" in r, r)
time.sleep(1.5)
e0 = emu()
st = T.status()
rpm = st["rpm"]
rpm_val = 60e6 / rpm[6] * 2 / 14 if rpm[6] and rpm[6] != 0xFFFF else 0
T.check(f"待機:模擬電變解出油門值 {e0['value']}(停止),控制器解出轉速 {rpm_val:.0f} RPM", e0["value"] == 0 and 1950 <= rpm_val <= 2050, (e0, rpm))

T.sim("att 0 0 1.0")
T.gesture_push(2.5)
T.wait_state("wait_still", 2)
T.wait_state("takeoff", 8, poll=0.02)
rows = []
t_end = time.time() + 13
while time.time() < t_end:
    st = T.status()
    rows.append((T.fstate(st), st["f"]["t"], st["f"]["out"], st["dsh"]))
    time.sleep(0.1)
bad = [r for r in rows if r[0] in ("takeoff", "flying") and abs(r[3] - dshot_of(r[2])) > 2]
T.check(f"飛行中 DShot 值 = 48 + 1999 × 油門%(±2,{len(rows)} 筆)", not bad, bad[:5])
T.check("緩啟動從很小的 DShot 值開始", any(r[0] == "takeoff" and 0 <= r[3] < 300 for r in rows), rows[:3])
e1 = emu()
st = T.status()
T.check(f"第二段 80%:狀態 dsh={st['dsh']},GPIO5 模擬電變從線上解出 {e1['value']}(預期 {dshot_of(80)})",
        st["dsh"] == dshot_of(80) and e1["value"] == dshot_of(80), (st["dsh"], e1))
ok_rate = (e1["crcok"] - e0["crcok"]) / max(1, e1["frames"] - e0["frames"])
T.check(f"飛行中模擬電變收到的訊框 CRC 正確率 {ok_rate*100:.1f}%", ok_rate >= 0.98, (e0, e1))
st2 = T.status()
T.check(f"飛行中轉速回傳持續成功(最近成功 {st2['rpm'][7]}ms 前)", 0 <= st2["rpm"][7] < 200, st2["rpm"])
T.post("/api/estop")
time.sleep(0.4)
e2 = emu()
st = T.status()
T.check(f"緊急停止後送停止指令:dsh={st['dsh']},線上解出 {e2['value']}", st["dsh"] == 0 and e2["value"] == 0, (st["dsh"], e2))
T.check(f"整段控制迴圈最長延遲 {st['late']}ms,最長執行 {st['ex']}µs", st["late"] <= 16 and st["ex"] < 3000, (st["late"], st["ex"]))
T.cmd("escemu off", expect="escemu")

T.log("\n== 收尾:還原設定,重開機回原協定 ==")
T.restore_and_verify()
T.post("/api/reboot")
T.wait_back()
time.sleep(3)
T.cmd("pwmcap on", expect="OK")
time.sleep(1.0)
st = T.status()
hz0 = T.SNAP["shared"]["escPwmHz"]
T.check(f"重開後回到 PWM {st['hz']}Hz,GPIO5 實測 {st['cap'][2]}µs / {st['cap'][3]}µs", st["proto"] == 0 and st["hz"] == hz0
        and abs(st["cap"][2] - 1000) <= 12 and abs(st["cap"][3] - 1e6 / hz0) <= 1e6 / hz0 * 0.01, (st["proto"], st["cap"]))
T.cmd("pwmcap off", expect="OK")
sys.exit(T.finish())
