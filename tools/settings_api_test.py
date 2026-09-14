# 版本流水號: r4 (2026-09-13) 複製測試不假設第 6 組名稱是 TEST(GG 改過名)
# 舊: r3 (2026-09-13) 可調點數改 1~4
# 舊: r2 (2026-09-13) 開始前確認待機並備份板上設定,結束時原樣還原(不再回預設,避免洗掉 GG 調好的值)
# 舊: r1 (2026-09-13) 設定 API 回歸測試(會改寫並儲存板子上的設定,結束時全部回預設)
# ============================================================================
# 用法: python tools/settings_api_test.py [板子位址]
# 前提: 板子在待機狀態,電腦與板子在同一網路.
# ============================================================================
import json
import sys
import time
import urllib.parse
import urllib.request

import board_backup

HOST = "http://" + (sys.argv[1] if len(sys.argv) > 1 else "lineplane.local")
passed = 0
failed = 0


def get(path):
    return json.loads(urllib.request.urlopen(HOST + path, timeout=8).read())


def post(path, **data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(HOST + path, data=body)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:   # 400 也帶 JSON
        return json.loads(e.read())


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  OK  ", name)
    else:
        failed += 1
        print("  FAIL", name, detail)


def vals(p=0):
    return get(f"/api/settings?p={p}")


def wait_back():
    for _ in range(40):
        time.sleep(1)
        try:
            return get("/api/status")
        except Exception:  # noqa: BLE001
            pass
    raise RuntimeError("board did not come back")


print("準備:確認待機,備份板上設定,全部回預設並儲存")
board_backup.require_idle(sys.argv[1] if len(sys.argv) > 1 else "lineplane.local")
SNAP = board_backup.backup(sys.argv[1] if len(sys.argv) > 1 else "lineplane.local")
post("/api/defaults", p="s")
for i in range(6):
    post("/api/defaults", p=i)
post("/api/select", p=0)
post("/api/save")

meta = get("/api/meta")
check("meta 有 6 組風格與曲線點數範圍", meta["profiles"] == 6 and meta["curveMin"] == 1 and meta["curveMax"] == 4)
v = vals(0)
check("預設值:第一段 75%,第二段 85%,下限 30", v["profile"]["phase1Pct"] == 75 and v["profile"]["phase2Pct"] == 85
      and v["profile"]["minPct"] == 30)
check("預設不髒", not v["dirtyShared"] and not any(v["dirtyProfiles"]))

r = post("/api/set", p=0, k="phase1Pct", v=80)
v = vals(0)
check("設定第一段 80%", r["ok"] and v["profile"]["phase1Pct"] == 80, r)
check("改值後標記未儲存", v["dirtyProfiles"][0] and get("/api/status")["dirty"] == 1)

r = post("/api/set", p=0, k="phase1Pct", v=150)
check("超範圍被拒(range)", not r["ok"] and r["code"] == "range", r)
r = post("/api/set", p=0, k="minPct", v=100)
check("下限不可 >= 上限(minmax)", not r["ok"] and r["code"] == "minmax", r)
r = post("/api/set", p=0, k="up1a", v=10)
check("曲線點不可越過死區(order)", not r["ok"] and r["code"] == "order", r)
r = post("/api/set", p=0, k="phase1Sec", v=300)
check("第一段時間不可 >= 總時間(phasetime)", not r["ok"] and r["code"] == "phasetime", r)
r = post("/api/set", p="s", k="upAxis", v=1)
check("方位兩軸不可同軸(axis)", not r["ok"] and r["code"] == "axis", r)
r = post("/api/set", p="s", k="lapSec", v=5.23)
check("浮點對齊細調步進(5.23 → 5.2)", r["ok"] and abs(vals(0)["shared"]["lapSec"] - 5.2) < 1e-6, vals(0)["shared"]["lapSec"])

v = vals(0)
check("新參數預設:換段有過渡(1),提早降落關閉,抖動 0.8g/1.0 秒/水平 20°,啟用 10 秒",
      v["profile"]["phaseMode"] == 1 and v["shared"]["earlyLand"] == 0 and abs(v["shared"]["earlyLandVib"] - 0.8) < 1e-6
      and abs(v["shared"]["earlyLandHold"] - 1.0) < 1e-6 and v["shared"]["earlyLandTilt"] == 20
      and v["shared"]["earlyLandArm"] == 10, (v["profile"]["phaseMode"], v["shared"]))
r0 = post("/api/set", p=0, k="phaseMode", v=3)
check("換段方式只有 0~2", not r0["ok"] and r0["code"] == "range", r0)
r1 = post("/api/set", p=0, k="phaseMode", v=2)
r2 = post("/api/set", p="s", k="earlyLand", v=1)
r3 = post("/api/set", p="s", k="earlyLandVib", v=1.25)
r4 = post("/api/set", p="s", k="earlyLandVib", v=12)
r5 = post("/api/set", p="s", k="earlyLandHold", v=1.5)
v = vals(0)
check("換段改平均分攤,開啟提早降落,抖動 1.25g,持續 1.5 秒", r1["ok"] and r2["ok"] and r3["ok"] and r5["ok"]
      and v["profile"]["phaseMode"] == 2 and v["shared"]["earlyLand"] == 1
      and abs(v["shared"]["earlyLandVib"] - 1.25) < 1e-6 and abs(v["shared"]["earlyLandHold"] - 1.5) < 1e-6, v["shared"])
check("抖動門檻超範圍被拒", not r4["ok"] and r4["code"] == "range", r4)

r = post("/api/set", p=0, k="upN", v=5)
check("可調點最多 4 點(5 點被拒)", not r["ok"] and r["code"] == "range" and "up5a" not in vals(0)["profile"], r)
r = post("/api/set", p=0, k="upN", v=4)
p = vals(0)["profile"]
angles = [p[f"up{i}a"] for i in range(1, 5)]
check("補速改 4 點:角度平均分布 38/55/73/90", r["ok"] and angles == [38, 55, 73, 90], (r, angles))
pcts = [p[f"up{i}p"] for i in range(1, 5)]
check("補速改 4 點:補償沿用舊曲線(20°=0%,45°=8% 之間內插)", pcts[0] == 6 and pcts[3] == 20, pcts)
r = post("/api/set", p=0, k="dnN", v=1)
p = vals(0)["profile"]
check("減速改 1 點:-90° -25%", r["ok"] and p["dnN"] == 1 and (p["dn1a"], p["dn1p"]) == (-90, -25), (r, p["dn1a"], p["dn1p"]))
r = post("/api/set", p=0, k="dnN", v=0)
check("可調點最少 1 點(0 點被拒)", not r["ok"] and r["code"] == "range", r)

r = post("/api/name", p=1, name="練習機")
check("中文命名", r["ok"] and vals(1)["names"][1] == "練習機", r)
r = post("/api/name", p=1, name="一二三四五六七八九十")   # 30 位元組,上限 23
n = vals(1)["names"][1]
check("名稱過長截在字元邊界(7 個中文字)", r["ok"] and n == "一二三四五六七", n)

name5 = vals(5)["names"][5]   # r4:GG 可能改過第 6 組的名稱,不假設是 TEST
r = post("/api/copy", **{"from": 0, "to": 5})
v5 = vals(5)
check(f"複製 A → 第 6 組:飛法跟過去,名稱保留「{name5}」", r["ok"] and v5["profile"]["phase1Pct"] == 80 and v5["names"][5] == name5, (r, v5["names"][5]))

trim = post("/api/set", p="s", k="pitchTrim", v=2.5)
time.sleep(0.3)
st = get("/api/status")
check("角度修正套用到控制角度(p - rp = 2.5)", trim["ok"] and abs((st["p"] - st["rp"]) - 2.5) < 0.2, (st["p"], st["rp"]))

r = post("/api/save")
v = vals(0)
check("儲存後不髒", r["ok"] and not v["dirtyShared"] and not any(v["dirtyProfiles"]), r)

r = post("/api/set", p=0, k="phase2Pct", v=90)
post("/api/revert")
check("放棄變更:第二段回到 85", vals(0)["profile"]["phase2Pct"] == 85)

post("/api/defaults", p=0)
check("回預設只改 RAM(第一段變 75 且未儲存)", vals(0)["profile"]["phase1Pct"] == 75 and vals(0)["dirtyProfiles"][0])
post("/api/revert")
check("回預設後放棄變更救得回來(80)", vals(0)["profile"]["phase1Pct"] == 80)

r = post("/api/select", p=1)
check("選用風格 B 立即生效", r["ok"] and vals(1)["active"] == 1, r)

print("重新開機,確認存檔保留")
post("/api/reboot")
time.sleep(3)
wait_back()
v0, v1, v5 = vals(0), vals(1), vals(5)
check("重開後 A 第一段仍是 80", v0["profile"]["phase1Pct"] == 80)
check("重開後 A 補速 4 點,減速 1 點", v0["profile"]["upN"] == 4 and v0["profile"]["dnN"] == 1)
check("重開後名稱與 TEST 複本保留", v1["names"][1] == "一二三四五六七" and v5["profile"]["phase1Pct"] == 80)
check("重開後飛行風格仍是 B", v0["active"] == 1)
check("重開後角度修正仍是 2.5", abs(v0["shared"]["pitchTrim"] - 2.5) < 1e-6)
check("重開後換段方式與提早降落設定保留", v0["profile"]["phaseMode"] == 2 and v0["shared"]["earlyLand"] == 1
      and abs(v0["shared"]["earlyLandVib"] - 1.25) < 1e-6)
check("重開後不髒", not v0["dirtyShared"] and not any(v0["dirtyProfiles"]))

print("收尾:還原測試前的板上設定")
errs = board_backup.restore(HOST.replace("http://", ""), SNAP)
check("還原寫入成功", not errs, errs)
d = board_backup.diff(SNAP, board_backup.backup(HOST.replace("http://", "")))
check("還原後與測試前完全相同", not d, d[:5])

print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
