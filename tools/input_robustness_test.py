# 版本流水號: r2 (2026-09-14) 收輪行程案例改用板上下限 +50;名稱測試分開檢查拒絕/接受
# 舊: r1 (2026-09-14) 錯誤輸入耐受測試:負值,超出範圍,文字,空白,半數字,曲線點越界/交錯,亂碼名稱,各 API 垃圾參數,隨機灌 300 筆
# 檢查:每筆都被拒絕(或安全處理),板子不重開不當機,設定與 WiFi 設定完全不變,控制迴圈沒被拖慢.
# 會改設定(名稱測試只改 RAM,結尾放棄變更並還原比對). 用法: python tools/input_robustness_test.py [板子位址]
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request

if len(sys.argv) > 1:
    os.environ["LP_HOST"] = sys.argv[1]
import lp_test as T  # noqa: E402
import board_backup  # noqa: E402

T.init("input_robustness_test")
T.protect()
st0 = T.status()
up0, ev0 = st0["up"], T.ev_total()
wifi0 = T.get("/api/wifi")
T.post("/api/timing/reset")
meta = T.get("/api/meta")


def raw(method, path, body=None, ctype="application/x-www-form-urlencoded"):
    req = urllib.request.Request(f"http://{T.HOST}{path}", data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", ctype)
    try:
        r = urllib.request.urlopen(req, timeout=8)
        return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def post(path, data):
    code, b = raw("POST", path, urllib.parse.urlencode(data).encode())
    try:
        return code, json.loads(b)
    except Exception:  # noqa: BLE001
        return code, {"raw": b[:80]}


def alive():
    st = T.status()
    return st["up"] >= up0 and not [e for e in T.events_after(ev0) if e[2] == 1], st


bad_all = []


def expect_reject(name, path, data, codes=None):
    code, r = post(path, data)
    ok = r.get("ok") is False and (codes is None or r.get("code") in codes)
    if not ok:
        bad_all.append((name, data, code, r))
    return ok


# ---- A. /api/set 數值 ----
T.log("\n== A. 參數值:負值,超範圍,文字,空白,半數字,非數字 ==")
cases = [("-1", "range"), ("101", "range"), ("abc", "value"), ("", "value"), (" ", "value"), ("12abc", "value"),
         ("1e999", "value"), ("nan", "value"), ("inf", "value"), ("-inf", "value"), ("٣", "value"), ("五十", "value"),
         ("1,5", "value"), ("50%", "value"), ("x" * 3000, "value"), ("99999999999999999999", "range"), ("-0.5", "range")]
n_bad = 0
for v, c in cases:
    if not expect_reject(f"phase1Pct={v[:12]!r}", "/api/set", {"p": T.TEST_SLOT, "k": "phase1Pct", "v": v}, [c]):
        n_bad += 1
T.check(f"油門 phase1Pct:{len(cases)} 種錯誤值全部拒絕(-1/101 → range,文字/空白/12abc/nan/inf → value)", n_bad == 0, bad_all[-3:])
rng = [("gestureG", "0.4"), ("gestureG", "6.1"), ("crashG", "-14"), ("countdownSec", "300"), ("escMinUs", "0"),
       ("escMaxUs", "99999"), ("pitchTrim", "-31"), ("lineLength", "abc"), ("gearMinUs", "12abc"), ("twistCancel", "-45")]
T.check("共用設定 10 種錯誤值全部拒絕", all(expect_reject(f"s.{k}={v}", "/api/set", {"p": "s", "k": k, "v": v}) for k, v in rng), bad_all[-3:])

T.log("\n== A2. 曲線點越界,交錯,交叉驗證 ==")
prof = T.get(f"/api/settings?p={T.TEST_SLOT}")["profile"]
cross = [("up1a", "95", ["range"]), ("up1a", "0", ["range"]), ("up1p", "51", ["range"]), ("up1p", "-51", ["range"]),
         ("up1a", str(prof["upDb"]), ["order"]), ("dn1a", "5", ["range"]), ("dn1a", str(prof["dnDb"]), ["order"]),
         ("upDb", "90", ["range"]), ("upN", "0", ["range"]), ("upN", "5", ["range"]), ("dnN", "abc", ["value"]),
         ("minPct", str(prof["maxPct"]), ["minmax"]), ("maxPct", str(prof["minPct"]), ["minmax"]),
         ("phase1Sec", str(prof["flightSec"]), ["phasetime", "range"])]
if prof["upN"] >= 2:
    cross.append(("up2a", str(prof["up1a"]), ["order"]))
T.check(f"曲線點與交叉驗證 {len(cross)} 種全部拒絕(越界 range,交錯/壓到死區 order,下限≥上限 minmax,第一段≥總時間 phasetime)",
        all(expect_reject(f"{k}={v}", "/api/set", {"p": T.TEST_SLOT, "k": k, "v": v}, c) for k, v, c in cross), bad_all[-3:])
# r1/r2:單改上限碰不到收輪行程交叉檢查(上限最小 1500,板上下限 1400 → 永遠合法),改用批次同時送下限 1480 上限 1520
code_g, b_g = raw("POST", "/api/setmany?p=s", b"gearMinUs=1480\ngearMaxUs=1520", "text/plain")
T.check("收輪行程上下限差不到 100(批次送 1480/1520):拒絕 gearrange", json.loads(b_g).get("code") == "gearrange", b_g)
shared_x = [("noseAxis", str(T.get('/api/settings?p=0')['shared']['upAxis']), ["axis"]),
            ("twistCancel", "5", ["twistdeg"])]
T.check("共用設定交叉驗證(收輪行程,方位同軸,扭轉角度)拒絕", all(expect_reject(f"s.{k}={v}", "/api/set", {"p": "s", "k": k, "v": v}, c)
                                                  for k, v, c in shared_x), bad_all[-3:])
T.check("錯誤的參數名與風格編號拒絕", all([
    expect_reject("unknown key", "/api/set", {"p": 0, "k": "notakey", "v": "1"}, ["key"]),
    expect_reject("p=9", "/api/set", {"p": 9, "k": "phase1Pct", "v": "50"}, ["scope"]),
    expect_reject("p=-1", "/api/set", {"p": -1, "k": "phase1Pct", "v": "50"}, ["scope"]),
    expect_reject("p=xyz", "/api/set", {"p": "xyz", "k": "phase1Pct", "v": "50"}, ["scope"]),
    expect_reject("缺 v", "/api/set", {"p": 0, "k": "phase1Pct"}, ["badform"]),
]), bad_all[-3:])

# ---- B. setmany ----
T.log("\n== B. 批次寫入(setmany)垃圾內容:不可只寫進一半 ==")
many = ["phase1Pct=50\nphase2Pct=abc", "phase1Pct=50\nnotakey=1", "phase1Pct=-1", "=5", "phase1Pct", "\n\n\n", "x" * 5000,
        "phase1Pct=50\nminPct=90\nmaxPct=80", "up1a=10\nup2a=5"]
okb = True
for body in many:
    code, b = raw("POST", f"/api/setmany?p={T.TEST_SLOT}", body.encode(), "text/plain")
    r = json.loads(b)
    okb &= r["ok"] is False
T.check(f"{len(many)} 種批次垃圾全部整批拒絕", okb)
T.check("批次被拒後設定沒有被寫進一半(沒有未儲存變更)", T.status()["dirty"] == 0, T.status()["dirty"])

# ---- C. 名稱 ----
T.log("\n== C. 風格名稱:空白,超長,控制字元,emoji,亂碼位元組 ==")
T.check("空白名稱拒絕", expect_reject("name empty", "/api/name", {"p": 1, "name": "   "}, ["name"]))
T.check("風格編號錯拒絕", expect_reject("name p=7", "/api/name", {"p": 7, "name": "x"}))
T.check("換行/tab 等控制字元拒絕", expect_reject("name ctrl", "/api/name", {"p": 1, "name": 'a"b\\c\n\t<script>'}, ["name"]))
code, b = raw("POST", "/api/name", b"p=1&name=%FF%FE%80abc")
T.check("非 UTF-8 亂碼位元組拒絕", json.loads(b).get("code") == "name", b)
code, b = raw("POST", "/api/name", b"p=1&name=%E4%B8")   # 半個中文字
T.check("半個中文字(不完整 UTF-8)拒絕", json.loads(b).get("code") == "name", b)
names_ok = True
for nm in ("一二三四五六七八九十" * 5, 'a"b\\c<script>alert(1)</script>', "😀🛩️✈️飛機"):
    r = post("/api/name", {"p": 1, "name": nm})[1]
    try:
        names = T.get("/api/settings?p=1")["names"]   # 嚴格 UTF-8 解碼
        T.log(f"  名稱 {nm[:14]!r} → {r.get('code')} 讀回 {names[1]!r}")
    except Exception as e:  # noqa: BLE001
        names_ok = False
        T.log("  讀回失敗:", e)
T.check("超長(截在字元邊界),引號/反斜線/<script>,emoji 名稱:接受後設定 JSON 仍正確", names_ok)
T.post("/api/revert")

# ---- D. 其他 API ----
T.log("\n== D. 其他 API 垃圾參數 ==")
d = [
    ("select p=abc", "/api/select", {"p": "abc"}), ("select p=9", "/api/select", {"p": 9}),
    ("copy from=abc", "/api/copy", {"from": "abc", "to": 1}), ("copy 1->1", "/api/copy", {"from": 1, "to": 1}),
    ("copy from=99", "/api/copy", {"from": 99, "to": 1}), ("copy from=12abc", "/api/copy", {"from": "0abc", "to": 1}),
    ("manual us=abc", "/api/manual", {"us": "abc"}), ("manual us=-1", "/api/manual", {"us": -1}),
    ("manual us=99999", "/api/manual", {"us": 99999}), ("manual us=1000abc", "/api/manual", {"us": "1000abc"}),
    ("manual 缺 us", "/api/manual", {}),
    ("wifi tmo=abc", "/api/wifi", dict(ssid=wifi0["ssid"], pw=wifi0["pw"], host=wifi0["host"], tmo="abc", forceap=wifi0["forceap"], txp=wifi0["txp"])),
    ("wifi tmo=12abc", "/api/wifi", dict(ssid=wifi0["ssid"], pw=wifi0["pw"], host=wifi0["host"], tmo="12abc", forceap=wifi0["forceap"], txp=wifi0["txp"])),
    ("wifi txp=-5", "/api/wifi", dict(ssid=wifi0["ssid"], pw=wifi0["pw"], host=wifi0["host"], tmo=wifi0["tmo"], forceap=wifi0["forceap"], txp=-5)),
    ("wifi host=bad name", "/api/wifi", dict(ssid=wifi0["ssid"], pw=wifi0["pw"], host="bad name!", tmo=wifi0["tmo"], forceap=wifi0["forceap"], txp=wifi0["txp"])),
    ("wifi pw=短", "/api/wifi", dict(ssid="x", pw="123", host=wifi0["host"], tmo=wifi0["tmo"], forceap=wifi0["forceap"], txp=wifi0["txp"])),
    ("wifi ssid 超長", "/api/wifi", dict(ssid="s" * 40, pw="", host=wifi0["host"], tmo=wifi0["tmo"], forceap=wifi0["forceap"], txp=wifi0["txp"])),
    ("wifi 缺欄位", "/api/wifi", {"ssid": "x"}), ("txpower abc", "/api/txpower", {"txp": "abc"}),
    ("txpower 99", "/api/txpower", {"txp": 99}), ("geartest on=xyz(=放下)", "/api/geartest", {"on": "xyz"}),
]
res = []
for name, path, data in d:
    code, r = post(path, data)
    res.append((name, r.get("ok"), r.get("code")))
T.log("  ", res)
T.check("其他 API 的垃圾參數都被拒絕(geartest on=xyz 視為放下,屬安全處理)",
        all(ok is False for n, ok, c in res if not n.startswith("geartest")), [x for x in res if x[1] is not False])
gets = ["/api/log?since=abc", "/api/log?since=-1", "/api/log?since=99999999999", "/api/events?since=abc", "/api/events?since=-5",
        "/api/settings?p=abc", "/api/settings?p=-9", "/api/settings?p=99", "/api/nothing", "/api/set", "/%FF%FE"]
gc = [raw("GET", g)[0] for g in gets]
T.log("  GET 回應碼:", dict(zip(gets, gc)))
T.check("GET 垃圾參數與不存在的網址都有正常回應(200/404/405,沒有斷線)", all(c in (200, 404, 405) for c in gc), gc)

# ---- E. 隨機灌 ----
T.log("\n== E. 隨機灌 300 筆錯誤值(所有參數名) ==")
random.seed(20260914)
junk = ["abc", "", " ", "--1", "1..2", "0x", "1e", "NaN", "Infinity", "null", "true", "[]", "{}", "'", '"', "\\", "%00", "\x00",
        "中文", "😀", "1 2", "+-3", "12abc", "٣", "1/2", "\r\n"]
okr = 0
t0 = time.time()
for i in range(300):
    scope = random.choice(["s", str(T.TEST_SLOT)])
    params = meta["shared"] if scope == "s" else meta["profile"]
    key = random.choice(list(params.keys()) if isinstance(params, dict) else [p[0] for p in params])
    if random.random() < 0.5:
        v = random.choice(junk)
    else:
        info = params[key] if isinstance(params, dict) else next(p for p in params if p[0] == key)
        lo, hi = (info[0], info[1]) if isinstance(info, list) else (info["min"], info["max"])
        v = str(random.choice([lo - random.uniform(1, 1000), hi + random.uniform(1, 1000)]))
    code, r = post("/api/set", {"p": scope, "k": key, "v": v})
    okr += r.get("ok") is False
T.log(f"  300 筆用了 {time.time()-t0:.1f} 秒,拒絕 {okr} 筆")
T.check("隨機 300 筆錯誤值全部被拒絕", okr == 300, okr)

# ---- F. 結果 ----
T.log("\n== F. 板子狀態 ==")
ok, st = alive()
T.check(f"板子沒有重開(開機秒數 {up0} → {st['up']},沒有新的開機事件)", ok, st["up"])
T.check(f"控制迴圈最長延遲 {st['late']}ms,最長執行 {st['ex']}µs(灌測期間)", st["late"] <= 20 and st["ex"] < 5000, (st["late"], st["ex"]))
T.check(f"待機,可用記憶體 {st0['heap']} → {st['heap']} bytes", T.fstate(st) in ("standby", "done") and st["heap"] > st0["heap"] - 20000, (st0["heap"], st["heap"]))
T.check("沒有未儲存變更", st["dirty"] == 0, st["dirty"])
dd = board_backup.diff(T.SNAP, board_backup.backup(T.HOST))
T.check("飛行設定與測試前完全相同", not dd, dd[:5])
w1 = T.get("/api/wifi")
T.check("WiFi 設定與測試前完全相同", all(w1[k] == wifi0[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp", "apsfx")), w1)
if bad_all:
    T.log("  沒被拒絕的:", bad_all)
T.restore_and_verify()
sys.exit(T.finish())
