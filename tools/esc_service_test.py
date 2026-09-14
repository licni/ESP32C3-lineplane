# 版本流水號: r1 (2026-09-13) 電變維護 API 測試:手動輸出(從最低開始,心跳逾時回最低,非待機拒絕,手動中拒絕重開機)與校正旗標
# ============================================================================
# 不改任何飛行設定(手動輸出與校正旗標都不在設定結構裡),板上有未儲存變更也可以跑.
# 會讓電變腳位輸出 1000~1300µs 幾秒. 結束時手動輸出停止,校正旗標還原成測試前的狀態.
# 用法: python tools/esc_service_test.py [板子位址]
# ============================================================================
import json
import sys
import time
import urllib.parse
import urllib.request

HOST = "http://" + (sys.argv[1] if len(sys.argv) > 1 else "lineplane.local")
passed = failed = 0


def get(path):
    return json.loads(urllib.request.urlopen(HOST + path, timeout=8).read())


def post(path, **data):
    req = urllib.request.Request(HOST + path, data=urllib.parse.urlencode(data).encode())
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  OK  ", name)
    else:
        failed += 1
        print("  FAIL", name, detail)


st = get("/api/status")
if st["f"]["s"] not in (1, 7):
    raise SystemExit(f"板子不在待機/結束(狀態 {st['f']['s']}),測試中止.")
sh = get("/api/settings?p=0")["shared"]
mn, mx = sh["escMinUs"], sh["escMaxUs"]
cal_before = st["cal"][2]
print(f"脈寬範圍 {mn}~{mx},校正旗標 {cal_before}")

r = post("/api/manual", us=mn + 300)
check("手動輸出不能從高油門開始(manuallow)", not r["ok"] and r["code"] == "manuallow", r)
r = post("/api/manual", us=mx + 50)
check("超出脈寬範圍被拒(range)", not r["ok"] and r["code"] == "range", r)

r = post("/api/manual", us=mn)
check("從最低油門開始手動輸出", r["ok"], r)
for us in (mn + 100, mn + 200, mn + 300):
    time.sleep(0.2)
    post("/api/manual", us=us)
time.sleep(0.15)
st = get("/api/status")
check(f"心跳中輸出跟著滑桿:{st['esc']} µs,man={st['man']}", st["esc"] == mn + 300 and st["man"] == 1, (st["esc"], st["man"]))
r = post("/api/reboot")
check("手動輸出中拒絕重新開機(busy)", not r["ok"] and r["code"] == "busy", r)
r = post("/api/calib", on=1)
check("手動輸出中拒絕設定校正(busy)", not r["ok"] and r["code"] == "busy", r)

time.sleep(0.8)   # 停止心跳
st = get("/api/status")
check(f"停止心跳 0.8 秒後回最低油門:{st['esc']} µs,man={st['man']}", st["esc"] == mn and st["man"] == 0, (st["esc"], st["man"]))
r = post("/api/manual", us=mn + 300)
check("逾時結束後再開始又要從最低油門(manuallow)", not r["ok"] and r["code"] == "manuallow", r)

post("/api/manual", us=mn)
time.sleep(0.2)
post("/api/manual", us=mn + 150)
r = post("/api/manual/stop")
time.sleep(0.1)
st = get("/api/status")
check(f"按上鎖立即回最低:{st['esc']} µs", r["ok"] and st["esc"] == mn and st["man"] == 0, (st["esc"], st["man"]))

dirty = st["dirty"]
r = post("/api/calib", on=1)
if dirty:
    check("有未儲存變更時拒絕設定校正(calibdirty)", not r["ok"] and r["code"] == "calibdirty", r)
else:
    check("待機且已儲存:設定下次通電校正", r["ok"] and get("/api/status")["cal"][2] == 1, r)
r = post("/api/calib", on=0)
check("取消校正旗標", r["ok"] and get("/api/status")["cal"][2] == 0, r)
if cal_before:
    post("/api/calib", on=1)
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
