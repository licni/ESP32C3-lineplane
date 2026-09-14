# 版本流水號: r1 (2026-09-13) 測試掛勾健全性:燒錄後設定不變,sim/pwmcap/ledcap 正常,不改設定
import json
import os
import sys
import time

import lp_test as T
import board_backup

T.init("t0_hooks_sanity")
st = T.status()
T.check("狀態 API 有 sim 與 cap 欄位", "sim" in st and "cap" in st, list(st.keys())[-4:])
with open(os.path.join(T.ROOT, "test_logs", "backup_before_fulltest.json"), encoding="utf-8") as f:
    before = json.load(f)
d = board_backup.diff(before, board_backup.backup(T.HOST))
T.check("燒錄後板上設定與燒錄前相同", not d, d[:5])
T.log("  狀態", T.fstate(st), "esc", st["esc"], "hz", st["hz"], "proto", st["proto"])

T.cmd("pwmcap on", expect="OK")
time.sleep(1.0)
p = T.pwm()
T.log("  pwm", p)
exp_period = round(1e6 / st["hz"])
T.check(f"GPIO5 量到脈寬 ≈ 電變設定 {st['esc']}µs(±15)", abs(p["high"] - st["esc"]) <= 15, p)
T.check(f"GPIO5 量到週期 ≈ {exp_period}µs(±1%)", abs(p["period"] - exp_period) <= exp_period * 0.01, p)
T.check("跳線確實有訊號(age < 100ms)", 0 <= p["age"] < 100, p)

runs = T.led_capture(1500)
T.log("  led", runs)
T.check("待機燈長亮(1.5 秒內只有一段亮)", len(runs) == 1 and runs[0][0], runs)

T.sim("att 30 0 1.0")
time.sleep(0.5)
st = T.status()
T.check(f"sim att 30° → 機頭讀值 {st['p']:.1f}°(含修正 {st['p']-st['rp']:+.1f})", abs(st["rp"] - 30) < 1.5, (st["p"], st["rp"]))
T.check("狀態 sim=1", st["sim"] == 1, st["sim"])
T.sim("att 0 -40 1.0")
time.sleep(0.5)
st = T.status()
T.check(f"sim att 0,-40 → 滾轉 {st['r']:.1f}°", abs(st["r"] + 40) < 1.5, st["r"])
T.sim("off")
time.sleep(1.5)
st = T.status()
T.check(f"sim off → 回到真的感測器(機頭 {st['rp']:.1f}°,滾轉 {st['r']:.1f}°)", abs(st["rp"]) < 5 and abs(st["r"]) < 5 and st["sim"] == 0, st)
ev = T.events(0)["ev"]
sims = [e for e in ev if e[2] == 22]
T.check("事件紀錄有模擬開啟與關閉", len(sims) >= 2 and sims[-2][3] == 1 and sims[-1][3] == 0, sims)
sys.exit(T.finish())
