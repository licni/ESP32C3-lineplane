# 版本流水號: r2 (2026-09-13) 感測器故障鎖定到重新上電;外力大小記最大值
# 舊: r1 (2026-09-13) 全功能測試 段 1:起飛安全性(感測器模擬走真正的偵測路徑)
# ============================================================================
# 手勢推力門檻,手勢防連按,水平限制(機頭/滾轉),未儲存變更,感測器故障,等待放穩,
# 外力介入(延長/上限/重置/不理會),扭轉機尾取消(門檻,死區,方向,關閉,封鎖期),
# 起飛程序中傾斜取消(含 0.2 秒濾波),網頁取消,上電自動倒數(水平等待,扭轉不適用,傾斜取消,只一次).
# 會改設定:開頭確認待機並備份,結尾還原並比對.
# ============================================================================
import sys
import time

import lp_test as T

T.init("t1_start_safety")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")


def evs_since(n):
    return T.events_after(n)


def of(evs, ty, arg=None):
    return [e for e in evs if e[2] == ty and (arg is None or e[3] == arg)]


def level():
    T.sim("gyro 0 0 0")
    T.sim("vib 0")
    T.sim("att 0 0 1.0")


def to_standby():
    st = T.status()
    if T.fstate(st) in ("wait_still", "countdown"):
        T.post("/api/cancel")
    elif T.fstate(st) in ("takeoff", "flying", "landing"):
        T.post("/api/estop")
    time.sleep(0.3)


def start_countdown():
    """手勢(真推力)→ 放穩 → 倒數. 回傳倒數開始時的狀態."""
    T.gesture_push(2.5)
    st = T.wait_state("wait_still", 2)
    if T.fstate(st) != "wait_still":
        return st
    return T.wait_state("countdown", 3)


T.log("== 設定:手勢 2.0g,水平限制 35°,倒數 5 秒,外力 0.3g 延長 3 秒,扭轉 45°/封鎖 5 秒 ==")
T.configure()
level()
time.sleep(1.8)
st = T.status()
T.check("模擬水平靜止,待機", T.fstate(st) in ("standby", "done") and abs(st["p"]) < 1 and abs(st["r"]) < 1, (T.fstate(st), st["p"], st["r"]))

# ---- 1. 推力門檻 ----
n0 = T.ev_total()
T.gesture_push(1.5)
time.sleep(0.6)
st = T.status()
T.check(f"推力 1.5g < 門檻 2.0g:不啟動(3 秒最大推力 {st['push3']:.2f}g)", T.fstate(st) in ("standby", "done") and not of(evs_since(n0), 3)
        and 1.4 <= st["push3"] <= 1.6, (T.fstate(st), st["push3"]))
T.gesture_push(2.5)
st = T.wait_state("wait_still", 2)
g = of(evs_since(n0), 3)
T.check("推力 2.5g:手勢成立 → 等待放穩,事件記推力 ≈2.5g(真推力,非序列模擬)",
        T.fstate(st) == "wait_still" and g and g[0][3] == 0 and abs(g[0][4] - 2.5) < 0.15, (T.fstate(st), g))
T.check("試推燈亮(glamp)且達標最大推力 ≈2.5", st["glamp"] == 1 and abs(st["gpeak"] - 2.5) < 0.15, (st["glamp"], st["gpeak"]))
t_ws = time.time()
st = T.wait_state("countdown", 3)
T.check(f"靜止 1 秒後開始倒數(等待 {time.time()-t_ws:.2f} 秒,倒數 {st['f']['cd']:.1f})",
        T.fstate(st) == "countdown" and 0.8 <= time.time() - t_ws <= 1.8 and st["f"]["cd"] > 4.5, st["f"])
T.check("起飛程序中設定鎖定", st["lock"] == 1 and not T.post("/api/set", p="s", k="gestureG", v=2.1)["ok"], st["lock"])
n1 = T.ev_total()
T.post("/api/cancel")
time.sleep(0.3)
st = T.status()
T.check("網頁取消 → 待機(er=7),電變 1000µs,事件 7", T.fstate(st) == "standby" and st["f"]["er"] == 7 and st["esc"] == 1000
        and of(evs_since(n1), 7), (st["f"], st["esc"]))

# ---- 2. 手勢防連按:1.5 秒內第二次推力不算 ----
T.gesture_push(2.5)
T.wait_state("wait_still", 2)
t_push = time.time()
T.post("/api/cancel")
n2 = T.ev_total()
time.sleep(max(0, 0.7 - (time.time() - t_push)))
T.sim("pulse x 2.5 120")
time.sleep(0.4)
st = T.status()
T.check("取消後 0.7 秒再推:仍在 1.5 秒防連按內,不啟動", T.fstate(st) == "standby" and not of(evs_since(n2), 3), T.fstate(st))
time.sleep(max(0, 1.7 - (time.time() - t_push)))
T.sim("pulse x 2.5 120")
st = T.wait_state("wait_still", 1.5)
T.check("過 1.5 秒後再推:手勢成立", T.fstate(st) == "wait_still", T.fstate(st))
T.post("/api/cancel")

# ---- 3. 起飛前水平限制(手勢)----
for att, name in (("45 0", "機頭 +45°"), ("-40 0", "機頭 −40°"), ("0 40", "滾轉 +40°"), ("0 -50", "滾轉 −50°")):
    T.sim(f"att {att} 1.0")
    time.sleep(0.3)
    n3 = T.ev_total()
    T.gesture_push(2.5, rearm=5.2)   # 拒絕事件 5 秒最多一筆,等過才看得到事件
    time.sleep(0.5)
    st = T.status()
    rj = of(evs_since(n3), 4, 3)
    T.check(f"{name}:手勢被拒(rj=3),停在待機,事件記角度", T.fstate(st) == "standby" and st["f"]["rj"] == 3 and rj
            and (abs(rj[0][4]) > 35 or abs(rj[0][5]) > 35), (T.fstate(st), st["f"]["rj"], rj))
T.sim("att 34 0 1.0")
time.sleep(0.3)
T.gesture_push(2.5)
st = T.wait_state("wait_still", 2)
T.check("機頭 +34°(限制內)手勢成立", T.fstate(st) == "wait_still", (T.fstate(st), st["p"]))
T.post("/api/cancel")
level()
time.sleep(0.5)

# ---- 4. 未儲存變更拒絕 ----
T.setp(T.TEST_SLOT, "phase2Pct", 81)
n4 = T.ev_total()
T.gesture_push(2.5)
time.sleep(0.5)
st = T.status()
T.check("有未儲存變更:手勢被拒(rj=1),事件 4/1", T.fstate(st) == "standby" and st["f"]["rj"] == 1 and of(evs_since(n4), 4, 1), st["f"])
T.post("/api/revert")
time.sleep(0.3)
T.check("放棄變更後沒有未儲存", T.status()["dirty"] == 0)

# ---- 5. 感測器故障 ----
n5 = T.ev_total()
T.sim("fail 1")
time.sleep(0.4)
st = T.status()
T.check("模擬 I2C 失敗 → 感測器故障(imu=2),事件 12", st["imu"] == 2 and of(evs_since(n5), 12), (st["imu"], evs_since(n5)))
time.sleep(1.2)
T.cmd("gesture", expect="OK")
time.sleep(0.4)
st = T.status()
T.check("感測器故障時手勢(序列模擬)被拒(rj=2)", T.fstate(st) == "standby" and st["f"]["rj"] == 2, st["f"])
T.sim("fail 0")
time.sleep(2.0)
st = T.status()
e13 = of(evs_since(n5), 13)
T.check("感測器又有回應:仍維持故障(imu=2),事件 13 記「這次通電不採用」(arg 1)一次",
        st["imu"] == 2 and len(e13) == 1 and e13[0][3] == 1, (st["imu"], e13))
time.sleep(1.2)
T.cmd("gesture", expect="OK")
time.sleep(0.4)
st = T.status()
T.check("恢復回應後手勢仍被拒(rj=2)", T.fstate(st) == "standby" and st["f"]["rj"] == 2, st["f"])
st = T.reboot()
T.check("重新開機後感測器恢復使用(imu=1)", st["imu"] == 1 and T.fstate(st) == "standby", (st["imu"], T.fstate(st)))
level()
time.sleep(1.0)
st = start_countdown()
T.check("(準備)倒數中", T.fstate(st) == "countdown", T.fstate(st))
T.sim("fail 1")
time.sleep(0.5)
st = T.status()
T.check("倒數中感測器故障 → 取消回待機(rj=2,er=7),不啟動馬達", T.fstate(st) == "standby" and st["f"]["rj"] == 2 and st["f"]["er"] == 7, st["f"])
T.reboot()
level()
time.sleep(1.0)

# ---- 6. 等待放穩:持續晃動不開始倒數 ----
T.gesture_push(2.5)
T.wait_state("wait_still", 2)
T.sim("vib 0.6 3")
time.sleep(3)
st = T.status()
T.check(f"晃動中(Z 軸 3Hz ±0.6g)3 秒:仍在等待放穩(已放穩 {st['f']['set']:.1f} 秒)", T.fstate(st) == "wait_still", st["f"])
T.sim("vib 0")
t0 = time.time()
st = T.wait_state("countdown", 3)
T.check(f"停止晃動 {time.time()-t0:.2f} 秒後開始倒數", T.fstate(st) == "countdown" and time.time() - t0 < 2.0, T.fstate(st))

# ---- 7. 外力介入:延長 + 上限 ----
time.sleep(1.5)
cd_before = T.status()["f"]["cd"]
n7 = T.ev_total()
T.sim("pulse y 0.6 200")
st = T.wait_state("wait_still", 1)
d = of(evs_since(n7), 6)
T.check(f"倒數中側向外力 0.6g → 回等待放穩,事件 6(延長,量到 {d[0][4]:.2f}g ≥ 門檻)" if d else "倒數中側向外力 → 回等待放穩",
        T.fstate(st) == "wait_still" and d and d[0][3] == 1 and d[0][4] >= 0.3, (T.fstate(st), d))
time.sleep(0.4)
st = T.status()
T.check(f"狀態回報外力動作 da=1,外力最大 {st['f']['dg']:.2f}g(實際側推 0.6g)", st["f"]["da"] == 1 and 0.5 <= st["f"]["dg"] <= 0.65, st["f"])
st = T.wait_state("countdown", 3)
c = of(evs_since(n7), 5, 1)
exp = min(cd_before + 3, 15)
T.check(f"放穩後延長:倒數 {cd_before:.1f} → {st['f']['cd']:.1f}(預期約 {exp:.1f}),事件 5/1 記外力最大 {c[0][5]:.2f}g" if c else "放穩後延長",
        T.fstate(st) == "countdown" and c and abs(c[0][4] - exp) < 0.6 and 0.5 <= c[0][5] <= 0.65, (st["f"]["cd"], c))
st = T.status()
T.log(f"  設定頁外力指示:目前 {st['dist'][0]:.2f}g,3 秒最大 {st['dist'][1]:.2f}g")
T.check("設定頁外力指示的 3 秒最大值也反映實際外力(≥0.5g)", st["dist"][1] >= 0.5, st["dist"])
cds = []
for i in range(5):
    T.sim("pulse y 0.6 200")
    T.wait_state("wait_still", 1)
    st = T.wait_state("countdown", 3)
    cds.append(round(st["f"]["cd"], 2))
T.log("  連續 5 次外力後的倒數:", cds)
T.check("延長上限:倒數最多到 倒數秒數 +10 = 15 秒(從未超過,最後貼近 15)", max(cds) <= 15.05 and cds[-1] >= 14.0, cds)
T.post("/api/cancel")

# ---- 8. 外力:重置 / 不理會 ----
T.configure(shared={"disturbMode": 1})
st = start_countdown()
time.sleep(2.5)
n8 = T.ev_total()
T.sim("pulse y 0.6 200")
T.wait_state("wait_still", 1)
st = T.wait_state("countdown", 3)
c = of(evs_since(n8), 5, 2)
T.check(f"外力「重新倒數」:放穩後倒數回到 5 秒(實際 {st['f']['cd']:.1f}),事件 5/2", c and abs(c[0][4] - 5) < 0.05 and st["f"]["cd"] > 4.5, (st["f"], c))
T.post("/api/cancel")
T.configure(shared={"disturbMode": 2})
st = start_countdown()
time.sleep(1)
n8b = T.ev_total()
T.sim("pulse y 0.8 300")
time.sleep(0.6)
st = T.status()
T.check("外力「不理會」:大外力 0.8g 倒數照走", T.fstate(st) == "countdown" and not of(evs_since(n8b), 6), (T.fstate(st), st["f"]["cd"]))
st = T.wait_state(("takeoff", "flying"), 6)
T.check("倒數結束馬達啟動(緩啟動),事件 8", T.fstate(st) in ("takeoff", "flying") and of(evs_since(n8b), 8), T.fstate(st))
T.post("/api/estop")
time.sleep(0.3)
T.check("(收)緊急停止", T.fstate() == "done")

# ---- 9. 扭轉機尾取消 ----
T.configure()
level()
st = start_countdown()
T.sim("gyro 0 0 4")
time.sleep(2.0)
st = T.status()
T.check(f"扭轉死區:4°/秒轉 2 秒不累積(tw={st['f']['tw']})", T.fstate(st) == "countdown" and abs(st["f"]["tw"]) < 1, st["f"])
T.sim("gyro 0 0 90")
time.sleep(0.3)
T.sim("gyro 0 0 0")
st = T.status()
T.check(f"扭轉約 27°(< 45°):不取消,回報角度 {st['f']['tw']}°", T.fstate(st) == "countdown" and 15 <= st["f"]["tw"] <= 40, st["f"])
T.post("/api/cancel")
for rate, name in ((90, "順時針"), (-90, "逆時針")):
    st = start_countdown()
    n9 = T.ev_total()
    T.sim(f"gyro 0 0 {rate}")
    st = T.wait_state("standby", 1.5)
    T.sim("gyro 0 0 0")
    tw = of(evs_since(n9), 20)
    T.check(f"{name}扭轉 90°/秒:超過 45° 取消回待機(er=8),事件記 {tw[0][4]:.0f}°" if tw else f"{name}扭轉取消",
            T.fstate(st) == "standby" and st["f"]["er"] == 8 and tw and 45 <= tw[0][4] <= 60 and tw[0][3] == 5, (st["f"], tw))
    T.check(f"取消後封鎖手勢(gb={st['f']['gb']:.1f} 秒)", 4.0 <= st["f"]["gb"] <= 5.0, st["f"]["gb"])
    if rate > 0:
        n9b = T.ev_total()
        T.sim("pulse x 2.5 120")
        time.sleep(0.5)
        T.check("封鎖期內推手勢無效,也不記手勢事件", T.fstate() == "standby" and not of(evs_since(n9b), 3))
        time.sleep(5.0)
        T.sim("pulse x 2.5 120")
        st = T.wait_state("wait_still", 1.5)
        T.check("封鎖期過後手勢有效", T.fstate(st) == "wait_still", T.fstate(st))
        T.post("/api/cancel")
    time.sleep(5.2)
T.configure(shared={"twistCancel": 0})
level()
st = start_countdown()
T.sim("gyro 0 0 120")
time.sleep(1.0)
T.sim("gyro 0 0 0")
st = T.status()
T.check("扭轉取消關閉(0):轉 120° 不取消", T.fstate(st) == "countdown", st["f"])
T.post("/api/cancel")

# ---- 10. 起飛程序中傾斜取消(外力不理會,單純看角度)----
T.configure(shared={"disturbMode": 2})
level()
st = start_countdown()
T.sim("att 40 0 1.0")
time.sleep(0.08)
T.sim("att 0 0 1.0")
time.sleep(0.5)
st = T.status()
T.check("倒數中短暫傾斜 40°(<0.2 秒):不取消", T.fstate(st) == "countdown", st["f"])
n10 = T.ev_total()
T.sim("att 40 0 1.0")
st = T.wait_state("standby", 1.0)
tl = of(evs_since(n10), 21)
T.check("倒數中傾斜 40° 持續:取消回待機(er=9),事件 21 記機頭角度與限制 35",
        T.fstate(st) == "standby" and st["f"]["er"] == 9 and tl and tl[0][3] == 35 and tl[0][4] > 35, (st["f"], tl))
level()
T.gesture_push(2.5)
T.wait_state("wait_still", 2)
T.sim("att 0 -45 1.0")
st = T.wait_state("standby", 1.0)
T.check("等待放穩中滾轉 −45°:取消(er=9)", T.fstate(st) == "standby" and st["f"]["er"] == 9, st["f"])
level()

# ---- 11. 上電自動倒數(手勢關閉)----
T.log("== 手勢關閉,重新開機(開機後 3 秒解鎖前用序列埠把模擬姿態設成機頭 +45°)==")
T.configure(shared={"gestureEnable": 0, "disturbMode": 2})
T.cmd("powerontest", expect="OK")   # 韌體 flight r15 起只有上電才自動倒數,這次軟體重開算上電
T.post("/api/reboot")
t0 = time.time()
ok = False
while time.time() - t0 < 6:
    try:
        r = T.cmd("sim att 45 0 1.0", expect="OK sim")
        if "OK sim on" in r and time.time() - t0 > 0.8:
            ok = True
            break
    except Exception:  # noqa: BLE001
        pass
    time.sleep(0.1)
T.log(f"  開機後 {time.time()-t0:.1f} 秒設定好模擬姿態", ok)
st = T.wait_back()
time.sleep(4)
st = T.status()
T.check(f"解鎖後機頭 45°:不倒數,等待放平(aw=1,rj=4)", T.fstate(st) == "standby" and st["f"]["aw"] == 1 and st["f"]["rj"] == 4, st["f"])
rj = of(T.events(0)["ev"], 4, 4)
T.check("事件記「上電自動倒數暫停」與角度", rj and rj[0][4] > 35, rj)
time.sleep(3)
T.check("持續傾斜 3 秒仍不倒數", T.fstate() == "standby")
T.sim("att 0 0 1.0")
t0 = time.time()
st = T.wait_state("countdown", 3)
T.check(f"放平 {time.time()-t0:.2f} 秒後開始倒數(需維持 1 秒)", T.fstate(st) == "countdown" and 0.9 <= time.time() - t0 <= 2.0, st["f"])
T.sim("gyro 0 0 120")
time.sleep(1.0)
T.sim("gyro 0 0 0")
st = T.status()
T.check("上電自動倒數不做扭轉取消(轉 120° 照倒數)", T.fstate(st) == "countdown", st["f"])
n11 = T.ev_total()
T.sim("att 0 50 1.0")
st = T.wait_state("standby", 1.0)
T.check("自動倒數中傾斜 → 取消(er=9)", T.fstate(st) == "standby" and st["f"]["er"] == 9, st["f"])
T.sim("att 0 0 1.0")
time.sleep(4)
st = T.status()
T.check("取消後放平也不再自己倒數(au=1,每次上電只一次)", T.fstate(st) == "standby" and st["f"]["au"] == 1 and not of(evs_since(n11), 5), st["f"])
T.cmd("gesture", expect="OK")
T.sim("pulse x 3 120")
time.sleep(1)
T.check("手勢關閉時推飛機或序列手勢都不啟動", T.fstate() == "standby")

T.log("\n== 收尾 ==")
T.restore_and_verify()
sys.exit(T.finish())
