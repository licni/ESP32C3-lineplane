# 版本流水號: r1 (2026-09-13) 全功能測試 段 5:電變手動輸出(GPIO5 實測),心跳逾時,校正旗標,PWM 頻率(重開機套用,實測週期)
# 會改設定:開頭確認待機並備份,結尾還原並比對,並重開機讓 PWM 頻率回到原本的值.
import sys
import threading
import time

import lp_test as T

T.init("t5_esc_service")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")
T.cmd("pwmcap on", expect="OK")


def of(evs, ty, arg=None):
    return [e for e in evs if e[2] == ty and (arg is None or e[3] == arg)]


class Beat:
    """模擬網頁每 0.2 秒送一次心跳"""

    def __init__(self):
        self.us = 1000
        self.run = True
        self.errs = []
        self.t = threading.Thread(target=self.loop, daemon=True)
        self.t.start()

    def loop(self):
        while self.run:
            r = T.post("/api/manual", us=self.us)
            if not r["ok"]:
                self.errs.append((self.us, r["code"]))
            time.sleep(0.2)

    def stop(self):
        self.run = False
        self.t.join()


s, p = T.configure(shared={"disturbMode": 2, "countdownSec": 20})
T.sim("att 0 0 1.0")
time.sleep(1.8)
base = T.get("/api/settings?p=0")["shared"]
lo, hi = base["escMinUs"], base["escMaxUs"]

# ---- 手動輸出 ----
T.log(f"\n== 手動輸出(0%={lo}µs,100%={hi}µs)==")
r = T.post("/api/manual", us=1300)
T.check("沒從最低開始(直接 1300µs):拒絕 manuallow", not r["ok"] and r["code"] == "manuallow", r)
n0 = T.ev_total()
b = Beat()
time.sleep(0.5)
b.us = 1300
time.sleep(0.8)
st = T.status()
T.check(f"從最低開始後改 1300µs:man=1,電變 {st['esc']},GPIO5 實測 {st['cap'][2]}µs", st["man"] == 1 and st["esc"] == 1300
        and abs(st["cap"][2] - 1300) <= 12 and of(T.events_after(n0), 14), (st["man"], st["esc"], st["cap"]))
b.us = hi
time.sleep(0.8)
st = T.status()
T.check(f"最高 {hi}µs:GPIO5 實測 {st['cap'][2]}µs", st["esc"] == hi and abs(st["cap"][2] - hi) <= 12, st["cap"])
T.check("心跳期間沒有錯誤", not b.errs, b.errs)
r1 = T.post("/api/manual", us=hi + 1)
r2 = T.post("/api/manual", us=lo - 1)
T.check("超出 0%~100% 脈寬:拒絕 range", not r1["ok"] and r1["code"] == "range" and not r2["ok"] and r2["code"] == "range", (r1, r2))
n1 = T.ev_total()
T.sim("pulse x 3 150")
time.sleep(0.5)
T.check("手動輸出中推啟動手勢:不理會", T.fstate() == "standby" and not of(T.events_after(n1), 3))
T.check("手動輸出中重新開機被拒(busy)", T.post("/api/reboot")["code"] == "busy")
T.check("手動輸出中設定校正被拒(busy)", T.post("/api/calib", on=1)["code"] == "busy")
b.us = 1500
time.sleep(0.6)
b.stop()
t_stop = time.time()
st = T.status()
while st["man"] == 1 and time.time() - t_stop < 2:
    time.sleep(0.02)
    st = T.status()
dt = time.time() - t_stop
time.sleep(0.3)
st = T.status()
T.check(f"停送心跳 {dt:.2f} 秒後自動回最低:電變 {st['esc']},GPIO5 實測 {st['cap'][2]}µs,事件 15(逾時 arg 1)",
        dt <= 0.9 and st["esc"] == lo and abs(st["cap"][2] - lo) <= 12 and of(T.events_after(n0), 15, 1), (dt, st["esc"], st["cap"]))
r = T.post("/api/manual", us=1500)
T.check("逾時結束後再開始又要從最低(1500 被拒)", not r["ok"] and r["code"] == "manuallow", r)
b = Beat()
time.sleep(0.4)
b.us = 1400
time.sleep(0.6)
b.run = False
T.post("/api/manual/stop")
t_s = time.time()
time.sleep(0.25)
st = T.status()
T.check(f"網頁上鎖(manual/stop)立即回最低:0.25 秒內電變 {st['esc']}µs", st["esc"] == lo and st["man"] == 0, (st["esc"], st["man"]))
b.stop()
time.sleep(1.8)
T.gesture_push(2.5)
T.wait_state("countdown", 4)
r = T.post("/api/manual", us=lo)
T.check("倒數中手動輸出被拒(manualstate)", not r["ok"] and r["code"] == "manualstate", r)
T.post("/api/cancel")
time.sleep(0.3)

# ---- 校正旗標 ----
T.log("\n== 電變校正旗標(實際校正要拔電再接電,USB 無法做,只測旗標與條件)==")
T.setp("s", "gestureG", 2.1)
r = T.post("/api/calib", on=1)
T.check("有未儲存變更時設定校正:拒絕 calibdirty", not r["ok"] and r["code"] == "calibdirty", r)
T.post("/api/revert")
r = T.post("/api/calib", on=1)
st = T.status()
T.check("設定校正旗標:成功,cal[2]=1", r["ok"] and st["cal"][2] == 1, (r, st["cal"]))
r = T.post("/api/calib", on=0)
st = T.status()
T.check("取消校正旗標:cal[2]=0", r["ok"] and st["cal"][2] == 0, (r, st["cal"]))

# ---- PWM 頻率 ----
for hz in (50, 400):
    T.log(f"\n== PWM {hz}Hz(儲存後重新開機套用)==")
    T.setp("s", "escPwmHz", hz)
    T.save()
    T.post("/api/reboot")
    T.wait_back()
    time.sleep(2)
    T.cmd("pwmcap on", expect="OK")
    time.sleep(1.0)
    st = T.status()
    per = round(1e6 / hz)
    T.check(f"{hz}Hz:狀態 hz={st['hz']},GPIO5 實測週期 {st['cap'][3]}µs(預期 {per}),脈寬 {st['cap'][2]}µs",
            st["hz"] == hz and abs(st["cap"][3] - per) <= per * 0.01 and abs(st["cap"][2] - lo) <= 12, st["cap"])
    time.sleep(0.5)
    b = Beat()
    time.sleep(0.4)
    b.us = 1500
    time.sleep(0.8)
    st = T.status()
    b.stop()
    T.check(f"{hz}Hz 手動 1500µs:GPIO5 實測 {st['cap'][2]}µs", abs(st["cap"][2] - 1500) <= 12, st["cap"])
    time.sleep(0.8)
r = T.post("/api/set", p="s", k="escPwmHz", v=450)
T.check("PWM 450Hz 超出範圍被拒", not r["ok"], r)

T.log("\n== 收尾:還原設定並重開機讓 PWM 頻率回到原本 ==")
T.restore_and_verify()
T.post("/api/reboot")
T.wait_back()
time.sleep(2)
T.cmd("pwmcap on", expect="OK")
time.sleep(1.0)
st = T.status()
hz0 = T.SNAP["shared"]["escPwmHz"]
T.check(f"重開後回到 {hz0}Hz,GPIO5 實測週期 {st['cap'][3]}µs", st["hz"] == hz0 and abs(st["cap"][3] - 1e6 / hz0) <= 1e6 / hz0 * 0.01, st["cap"])
T.cmd("pwmcap off", expect="OK")
sys.exit(T.finish())
