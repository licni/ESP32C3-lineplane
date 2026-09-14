# 版本流水號: r4 (2026-09-14) 事件順序不算機輪收腳事件 23(看板上的收腳設定,t4 不改;收腳時機由 t9 測),另外記錄
# 舊: r3 (2026-09-14) 撞擊斷電後推飛機不算手勢(拒絕原因 9):回待機改用網頁開始再取消;
#   飛行中鎖定段沒進入飛行就不送寫入類 API(不在飛行時那些 API 會真的改設定,儲存,重開機)
# 舊: r2 (2026-09-13) 感測器故障鎖定到重新上電:故障後重開機再測,加「又有回應仍極快閃」;撞擊測試移到最後一次重開之後(飛行紀錄才留得住)
# 舊: r1 (2026-09-13) 全功能測試 段 4:狀態燈(讀腳位),事件紀錄順序與數值,飛行紀錄,飛行中鎖定
# ============================================================================
# 燈號規格(規格第 3 節):解鎖熄滅 / 待機長亮 / 等待放穩慢閃 / 倒數快閃 / 飛行降落熄滅 /
#   正常結束閃 2 下停一下 / 撞擊斷電閃 3 下停一下 / 感測器故障極快閃 / 拒絕啟動急閃 1 秒
# 會改設定:開頭確認待機並備份,結尾還原並比對.
# ============================================================================
import struct
import sys
import time
import urllib.request

import lp_test as T

T.init("t4_led_log_lock")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")


def of(evs, ty, arg=None):
    return [e for e in evs if e[2] == ty and (arg is None or e[3] == arg)]


def level():
    T.sim("gyro 0 0 0")
    T.sim("vib 0")
    T.sim("att 0 0 1.0")


def launch():
    level()
    T.gesture_push(2.5)
    T.wait_state("wait_still", 2)
    T.wait_state("countdown", 3)
    return T.wait_state("takeoff", 30, poll=0.02)


def back_to_standby():
    """從結束狀態回到真正的待機. r3:撞擊斷電後推飛機不算手勢,重開機又會清掉飛行紀錄,所以用網頁開始再取消"""
    r = T.post("/api/start")
    T.wait_state(("wait_still", "countdown"), 2)
    T.post("/api/cancel")
    return r["ok"] and T.fstate(T.wait_state("standby", 1)) == "standby"


def inner(runs):
    """去掉頭尾(取樣開始/結束切斷的)段"""
    return runs[1:-1]


def near(v, target, tol):
    return abs(v - target) <= tol


s, p = T.configure(shared={"disturbMode": 2, "countdownSec": 20})
level()
time.sleep(1)

# ============ A. 燈號 ============
T.log("\n== A. 狀態燈(GPIO8 腳位實際電位,每 5ms 取樣)==")
# r1:板子可能停在上一個測試的「結束」狀態(閃 2 下),先開始再取消,回到真正的待機
back_to_standby()
runs = T.led_capture(1500)
T.check("待機:長亮", len(runs) == 1 and runs[0][0], runs)

T.sim("att 45 0 1.0")
time.sleep(0.3)
T.gesture_push(2.5)
runs = T.led_capture(1600)
fast = [r for r in runs if 35 <= r[1] <= 65]
T.log("  拒絕:", runs[:6], "...", runs[-3:])
T.check(f"拒絕啟動:急閃(50ms 亮滅 {len(fast)} 段)約 1 秒後回長亮", len(fast) >= 12 and runs[-1][0] and runs[-1][1] >= 300, runs)
level()

T.sim("fail 1")
T.sim("fail 1")
time.sleep(0.4)
runs = T.led_capture(1000)
vfast = [r for r in inner(runs) if 30 <= r[1] <= 50]
T.check(f"感測器故障(待機):極快閃 40ms({len(vfast)}/{len(inner(runs))} 段)", len(inner(runs)) >= 15 and len(vfast) >= len(inner(runs)) - 2, runs[:8])
T.sim("fail 0")
time.sleep(0.5)
runs = T.led_capture(1000)
T.check("感測器又有回應:仍極快閃(故障鎖定到重新上電)", len(inner(runs)) >= 15, runs[:6])
T.reboot()
level()
time.sleep(1.8)

T.gesture_push(2.5)
T.wait_state("wait_still", 2)
T.sim("vib 0.6 3")
time.sleep(0.2)
runs = T.led_capture(3200)
T.log("  等待放穩:", runs)
T.check("等待放穩:慢閃(每段約 500ms)", T.fstate() == "wait_still" and len(inner(runs)) >= 4 and all(near(r[1], 500, 25) for r in inner(runs)), runs)
T.sim("vib 0")
T.wait_state("countdown", 3)
runs = T.led_capture(2000)
T.log("  倒數:", runs[:6], "...")
T.check("倒數:快閃(每段約 125ms)", T.fstate() == "countdown" and len(inner(runs)) >= 12 and all(near(r[1], 125, 15) for r in inner(runs)), runs)
T.post("/api/cancel")

s, p = T.configure(shared={"disturbMode": 2, "countdownSec": 5})
launch()
T.wait_state("flying", 3)
runs = T.led_capture(1500)
T.check("飛行中:熄滅", len(runs) == 1 and not runs[0][0], runs)
T.sim("fail 1")
time.sleep(0.3)
runs = T.led_capture(1000)
T.check("飛行中感測器故障:仍熄滅(極快閃只在馬達沒轉時)", len(runs) == 1 and not runs[0][0], runs)
T.post("/api/estop")
T.wait_state("done", 1)
runs = T.led_capture(1000)
T.check("故障中停止後:極快閃(提醒重新上電)", len(inner(runs)) >= 15, runs[:6])
T.reboot()
s, p = T.configure(shared={"disturbMode": 2, "countdownSec": 5})

launch()
T.wait_state("flying", 3)
T.post("/api/estop")
T.wait_state("done", 1)
runs = T.led_capture(4200)
T.log("  正常結束:", runs)
on = [r for r in inner(runs) if r[0]]
long_off = [r for r in inner(runs) if not r[0] and r[1] > 1000]
T.check("正常結束:閃 2 下停一下(亮 150ms,每 2 秒 2 下,長暗約 1550ms)",
        on and all(near(r[1], 150, 15) for r in on) and long_off and all(near(r[1], 1550, 30) for r in long_off)
        and 3 <= len(on) <= 5, runs)

launch()
T.wait_state("flying", 3)
T.sim("pulse z 13.5 30")
T.wait_state("done", 1)
runs = T.led_capture(4200)
T.log("  撞擊斷電:", runs)
on = [r for r in inner(runs) if r[0]]
long_off = [r for r in inner(runs) if not r[0] and r[1] > 1000]
T.check("撞擊斷電:閃 3 下停一下(每 2 秒 3 下,長暗約 1250ms)",
        T.status()["f"]["er"] == 5 and on and all(near(r[1], 150, 15) for r in on) and long_off
        and all(near(r[1], 1250, 30) for r in long_off) and 5 <= len(on) <= 7, runs)
# ============ B. 事件紀錄:一趟完整飛行 ============
T.log("\n== B. 事件紀錄:手勢 → 倒數 5 秒 → 飛行 30 秒(第一段 10 秒)→ 降落 → 靜止觸地 ==")
level()
T.check("撞擊斷電後:網頁開始再取消,回到待機(推飛機不算手勢)", back_to_standby(), T.fstate())
n0 = T.ev_total()
log_total0 = None
T.gesture_push(2.5)
T.wait_state("takeoff", 10)
st = T.wait_state("done", 40)
time.sleep(0.3)
ev = T.events_after(n0)
T.log("  事件:", [(e[2], e[3], round(e[4], 2), round(e[5], 2), e[1]) for e in ev])
gear = of(ev, 23)
if gear:
    T.log("  (觀察)機輪收腳事件(看板上的收腳設定,不算在順序裡):", [("收起" if e[3] else "放下", round(e[4], 2)) for e in gear])
ev = [e for e in ev if e[2] != 23]
seq = [e[2] for e in ev]
T.check("事件順序:手勢 3 → 開始倒數 5 → 馬達啟動 8 → 換段 9 → 開始降落 10 → 馬達停止 11", seq == [3, 5, 8, 9, 10, 11], seq)
if seq == [3, 5, 8, 9, 10, 11]:
    g, c, m, ph, ls, sp = ev
    T.check(f"手勢推力 {g[4]:.2f}g(arg 0 = 真推力)", g[3] == 0 and near(g[4], 2.5, 0.15), g)
    T.check(f"倒數 {c[4]} 秒,首次(arg 0)", c[3] == 0 and c[4] == 5, c)
    T.check(f"馬達啟動:風格 #{m[3]},第一段 {m[4]}%;倒數耗時 {(m[1]-c[1])/1000:.2f} 秒", m[3] == T.TEST_SLOT and m[4] == 60
            and near((m[1] - c[1]) / 1000, 5, 0.1), m)
    T.check(f"換段:飛行 {ph[4]:.2f} 秒", near(ph[4], 10, 0.05) and near((ph[1] - m[1]) / 1000, 10, 0.05), ph)
    T.check(f"開始降落:時間到(arg 1),飛行 {ls[4]:.2f} 秒", ls[3] == 1 and near(ls[4], 30, 0.05), ls)
    T.check(f"馬達停止:靜止(arg 2){sp[4]:.2f} 秒 / 門檻 {sp[5]};降落 {(sp[1]-ls[1])/1000:.2f} 秒", sp[3] == 2 and sp[4] >= 1.0
            and sp[5] == 1.0 and 2.95 <= (sp[1] - ls[1]) / 1000 <= 3.3, sp)   # 桌上靜止在減力期間就累積,減力一走完就停

# ============ C. 飛行紀錄(/api/log)============
T.log("\n== C. 飛行紀錄 ==")
raw = urllib.request.urlopen(f"http://{T.HOST}/api/log?since=0", timeout=15).read()
start, count, sample_ms, size = struct.unpack("<IIHH", raw[:12])
T.check(f"格式:每筆 {size} 位元組,{sample_ms}ms 一筆,{count} 筆,長度正確", size == 8 and sample_ms == 100 and len(raw) == 12 + count * size,
        (start, count, sample_ms, size, len(raw)))
rows = [struct.unpack("<bBBBBbBB", raw[12 + i * 8:20 + i * 8]) for i in range(count)]
# 找最後一段飛行(狀態 4/5/6)
idx = [i for i, r in enumerate(rows) if r[6] in (4, 5, 6)]
last_run = []
for i in reversed(idx):
    if last_run and last_run[-1] - i > 1:
        break
    last_run.append(i)
last_run.reverse()
fl = [rows[i] for i in last_run]
n_fly = sum(1 for r in fl if r[6] == 5)
n_land = sum(1 for r in fl if r[6] == 6)
T.log(f"  最後一趟:緩啟動 {sum(1 for r in fl if r[6]==4)} 筆,飛行 {n_fly} 筆,降落 {n_land} 筆")
T.check(f"緩啟動 + 飛行 + 降落 33 秒 = 330 筆(每筆 100ms;實際 {len(fl)} 筆)", 326 <= len(fl) <= 334, len(fl))
p1 = [r[1] for r in fl if r[6] == 5][5:75]
p2 = [r[1] for r in fl if r[6] == 5][-100:]
T.check(f"紀錄的油門:第一段 {set(p1)},第二段 {set(p2)}", set(p1) == {60} and set(p2) == {80}, (set(p1), set(p2)))
before = rows[last_run[0] - 60:last_run[0]]
T.check("起飛前有倒數(狀態 3)與手勢推力紀錄(≥2.4g,旗標 GESTURE)", any(r[6] == 3 for r in before)
        and any(r[5] >= 24 and (r[7] & 0x08) for r in rows[last_run[0] - 90:last_run[0]]),
        [(r[5], r[6], r[7]) for r in before if r[5] > 5])
after = rows[last_run[-1] + 1:last_run[-1] + 3]
T.check("結束後狀態 7", after and after[0][6] == 7, after)
crash = [r for r in rows if r[2] >= 140]
T.check(f"之前的撞擊測試 14.5g 有記到總 G(最大 {max(r[2] for r in rows)/10:.1f}g)", crash, max(r[2] for r in rows))

# ============ D. 飛行中鎖定 ============
T.log("\n== D. 飛行中:設定/儲存/重開機/校正/手動輸出一律拒絕 ==")
launch()
st = T.wait_state("flying", 3)
# r3:不在飛行時下面的 API 會真的改設定,回預設,儲存,重開機,所以沒進入飛行就整段略過
flying = T.fstate(st) == "flying"
T.check("進入飛行(沒進入就略過寫入類 API)", flying, T.fstate(st))
if flying:
    T.check("飛行中 lock=1,ota=0", st["lock"] == 1 and st["ota"] == 0, (st["lock"], st["ota"]))
    res = {
        "set": T.post("/api/set", p="s", k="gestureG", v=2.1),
        "setmany": None,
        "name": T.post("/api/name", p=1, name="X"),
        "select": T.post("/api/select", p=1),
        "copy": T.post("/api/copy", **{"from": 0, "to": 1}),
        "defaults": T.post("/api/defaults", p="s"),
        "save": T.post("/api/save"),
        "revert": T.post("/api/revert"),
        "reboot": T.post("/api/reboot"),
        "calib": T.post("/api/calib", on=1),
        "manual": T.post("/api/manual", us=1000),
    }
    try:
        T.setmany("s", {"gestureG": 2.2})
        res["setmany"] = {"ok": True}
    except RuntimeError as e:
        res["setmany"] = {"ok": False, "code": str(e)}
    T.log("  回應:", {k: (v["ok"], v.get("code")) for k, v in res.items()})
    T.check("所有寫入類 API 都被拒絕(locked/busy/manualstate)", all(not v["ok"] for v in res.values()), res)
    st = T.status()
    T.check("被拒絕後仍在飛行,板子沒有重開,設定沒變", T.fstate(st) == "flying" and st["dirty"] == 0, (T.fstate(st), st["dirty"], st["up"]))
    r = T.cmd("orient +x +z", expect="OK")
    T.log(f"  (觀察)飛行中從 USB 序列埠送 orient +x +z:{r!r}")
T.post("/api/estop")
T.wait_state("done", 1)
time.sleep(0.3)
if flying:
    T.check("結束後解鎖(lock=0,ota=1)", T.status()["lock"] == 0 and T.status()["ota"] == 1)

# ============ E. 解鎖期燈號與開機事件 ============
T.log("\n== E. 重新開機:解鎖 3 秒熄滅,開機原因事件 ==")
T.post("/api/reboot")
t0 = time.time()
got = False
time.sleep(0.3)
while time.time() - t0 < 6:
    try:
        r = T.cmd("ledcap 6000", expect="OK ledcap")
        if "OK ledcap" in r and time.time() - t0 > 0.8:
            got = True
            break
    except Exception:  # noqa: BLE001
        pass
    time.sleep(0.05)
T.log(f"  開機後約 {time.time()-t0:.1f} 秒開始取樣")
time.sleep(6.3)
r = T.cmd("led", expect="led")
runs = [(x[0] == "+", int(x[1:])) for x in r.split("led runs=")[-1].split()[1:]] if "led runs" in r else []
T.log("  開機燈:", runs)
ev = T.events(0)["ev"]
boot = of(ev, 1)
armed = of(ev, 2)
T.check(f"開機第一筆事件:軟體重開機(原因 {boot[0][4] if boot else '?'})", boot and ev[0][2] == 1 and boot[0][4] == 3, ev[:2])
T.check(f"電變解鎖事件在開機後 {armed[0][1]/1000 if armed else '?'} 秒(手勢開啟 arg 1)", armed and armed[0][3] == 1 and 3.0 <= armed[0][1] / 1000 <= 4.0, armed)
T.check("解鎖期間熄滅,之後長亮", got and len(runs) == 2 and not runs[0][0] and runs[1][0] and runs[0][1] >= 800, runs)

T.log("\n== 收尾 ==")
T.restore_and_verify()
sys.exit(T.finish())
