# 版本流水號: r1 (2026-10-30) 網頁假伺服器:沒有板子也能開啟 web_page.h 的網頁(截圖,寫說明書,離線看版面用)
# ============================================================================
# 從 src/web_page.h 取出 HTML,用 Python 內建 http.server 提供 / 與板子的 API(/api/meta,/api/settings,/api/status,
# /api/events,/api/log,/api/wifi,/api/fw;POST 一律回 ok). 參數表與出廠值直接從 src/settings.cpp 解析(SP/PP 表,defaultShared/defaultProfile),
# 所以出廠值改了這裡自動跟上. 情境(姿態,飛行狀態,風格設定)由 scenario 字典決定,截圖工具可改.
# 飛行紀錄(/api/log)用簡單的球面軌跡合成:水平圈 + 幾個拉起,油門照曲線算,看起來像真飛.
# 用法:python3 tools/web_mock.py [埠號]   → http://127.0.0.1:埠號/#tab-comp
#       或由 tools/comp_manual_pdf.py 匯入,用 serve_in_thread() 開在背景.
# ============================================================================
import http.server
import json
import math
import os
import re
import struct
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def page_html():
    s = read(os.path.join(SRC, "web_page.h"))
    m = re.search(r'R"HTML\((.*)\)HTML"', s, re.S)
    return m.group(1)


def _num(t):
    t = t.strip().rstrip("f")
    return float(t) if ("." in t or "e" in t) else int(t)


def parse_params():
    """SP/PP 表 → {key: (field, min, max, fine, coarse)};shared 與 profile 分開."""
    s = read(os.path.join(SRC, "settings.cpp"))
    out = {"shared": {}, "profile": {}}
    for kind, pre in (("shared", "SP"), ("profile", "PP")):
        for m in re.finditer(pre + r'\("(\w+)",\s*PARAM_\w+,\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,)]+)\)', s):
            key, field, mn, mx, fi, co = m.groups()
            consts = {"THROTTLE_FLOOR_PCT": 10, "CURVE_MIN_POINTS": 1, "CURVE_MAX_POINTS": 4}
            vals = [consts.get(x.strip(), None) for x in (mn, mx, fi, co)]
            vals = [v if v is not None else _num(x) for v, x in zip(vals, (mn, mx, fi, co))]
            out[kind][key] = (field.strip(), *vals)
    return out


ENUMS = {"IMU_AXIS_PX": 0, "IMU_AXIS_NX": 1, "IMU_AXIS_PY": 2, "IMU_AXIS_NY": 3, "IMU_AXIS_PZ": 4, "IMU_AXIS_NZ": 5,
         "ESC_PROTO_PWM50": 0, "DISTURB_EXTEND": 0, "ARM_WAIT_DEFAULT_MIN": 3, "WAG_STOP_DEFAULT_DEG": 30,
         "PHASE_STEP": 0, "PHASE_STEP_RAMP": 1, "PHASE_SPREAD": 2, "LANDING_RAMP": 0, "COMP_CURVE": 0}


def parse_defaults(params):
    """defaultShared / defaultProfile(B~E 組那段)的 `x.field = value` → {key: value}. 曲線點另外處理."""
    s = read(os.path.join(SRC, "settings.cpp"))
    def block(name):
        m = re.search(r"static void " + name + r"\([^)]*\)\s*\{(.*?)\n\}", s, re.S)
        return m.group(1)
    assigns = {}
    for name, var in (("defaultShared", "s"), ("defaultGFeedback", "p"), ("defaultPulse", "p"), ("defaultProfile", "p")):
        body = block(name)
        if name == "defaultProfile":
            body = body.split("if (index == 0)")[0]   # 只取 B~E 的共同值
        for m in re.finditer(r"\b" + var + r"\.([\w.\[\]]+)\s*=\s*([^;]+);", body):
            assigns[m.group(1)] = m.group(2).strip()
    out = {"shared": {}, "profile": {}}
    for kind in ("shared", "profile"):
        for key, (field, *_rest) in params[kind].items():
            if field in assigns:
                v = assigns[field]
                out[kind][key] = ENUMS[v] if v in ENUMS else _num(v)
    # 曲線:up/down/side(出廠 B~E)
    curves = {"up": [(20, 0), (45, 8), (70, 15), (90, 20)], "dn": [(-3, 0), (-30, -10), (-60, -20), (-90, -25)],
              "sd": [(20, 0), (45, 0), (70, 0), (90, 0)]}
    for pre, pts in curves.items():
        out["profile"][pre + "Db"] = pts[0][0]
        out["profile"][pre + "N"] = 3
        for i, (a, c) in enumerate(pts[1:], 1):
            out["profile"][f"{pre}{i}a"] = a
            out["profile"][f"{pre}{i}p"] = c
        out["profile"][f"{pre}4a"] = pts[-1][0]
        out["profile"][f"{pre}4p"] = pts[-1][1]
    out["profile"].setdefault("takeoffPct", out["profile"].get("phase1Pct", 75))
    for k, v in (("takeoffHold", 0), ("landingMode", 0), ("landingBuzz", 0)):   # defaultProfile 在 index 分支之後才設,上面只取前段
        out["profile"].setdefault(k, v)
    return out


# ---------------------------------------------------------------- 情境
def default_scenario():
    params = parse_params()
    d = parse_defaults(params)
    return {
        "params": params,
        "shared": d["shared"],
        "profiles": [dict(d["profile"]) for _ in range(6)],
        "names": ["A", "B", "C", "D", "E", "測試"],
        "active": 1, "edit": 1,
        "status": {"p": 0.0, "r": 0.0, "sd": 0.0, "az": 0.0, "state": 1, "t": 0.0, "lg": 0.0, "gt": 0.0},
    }


def curve_pct(prof, pre, x, sign=1):
    """與韌體 sideCompPct 同一套折線."""
    x = x * sign
    pa, pp = prof[pre + "Db"] * sign, 0
    if x <= pa:
        return 0.0
    for i in range(1, prof[pre + "N"] + 1):
        a, c = prof[f"{pre}{i}a"] * sign, prof[f"{pre}{i}p"]
        if x <= a:
            return pp + (c - pp) * (x - pa) / (a - pa) if a > pa else c
        pa, pp = a, c
    return pp


def pitch_comp(prof, deg):
    return curve_pct(prof, "up", deg, 1) if deg >= 0 else curve_pct(prof, "dn", deg, -1)


def side_factor(pitch, roll_rate=0.0):
    pf = 1.0 if pitch >= 0 else max(0.0, 1.0 + pitch / 45.0)
    rf = min(1.0, max(0.0, (180.0 - abs(roll_rate)) / 90.0))
    return pf * rf


def status_json(sc):
    st = sc["status"]
    prof = sc["profiles"][sc["active"]]
    sf = side_factor(st["p"])
    cmp_ = pitch_comp(prof, st["p"])
    scmp = curve_pct(prof, "sd", st["sd"], 1) * sf
    s = st["state"]
    base = prof["phase1Pct"] if st["t"] < prof["phase1Sec"] else prof["phase2Pct"]
    comp = (cmp_ + scmp + st["gt"]) if s == 5 else 0
    out = min(prof["maxPct"], max(prof["minPct"], base + comp)) if s == 5 else 0
    f = {"s": s, "ss": st["t"], "cd": 0, "t": st["t"], "base": base if s == 5 else 0, "comp": comp, "out": out, "lg": st["lg"], "gt": st["gt"] if s == 5 else 0,
         "ph": 2 if st["t"] >= prof["phase1Sec"] else 1, "tb": 0, "lc": 0, "er": 0, "rj": 0, "rja": -1, "da": 0, "dg": 0, "dga": -1, "ge": 1, "au": 0,
         "fp": sc["active"], "set": 0, "tw": 0, "gb": 0, "aw": 0, "arm": 0, "al": 0, "awl": -1, "lp": 0}
    return {"p": st["p"], "rp": st["p"], "r": st["r"], "sd": st["sd"], "scmp": scmp, "az": st["az"], "sf": sf, "a": 1.0, "g": [0, 0, 0], "b": [0, 0, 0],
            "st": 1, "sts": 12.0, "imu": 1, "esc": 1000, "ex": 300, "late": 0, "up": 600, "heap": 180000, "ws": 1, "ip": "192.168.4.1", "rssi": -55,
            "cd": 0, "ota": 1, "act": sc["active"], "dirty": 0, "lock": 1 if s == 5 else 0, "cmp": cmp_, "imp": [0, 0, -1], "vib": 0.02, "lvl": 1, "hold": 0,
            "push": 0, "glamp": 0, "gpeak": 0, "push3": 0, "dist": [0, 0, -1], "f": f, "man": 0, "cal": [0, 0, 0, 0, 0], "dsh": -1, "proto": 0, "hz": 100,
            "evn": 0, "rpm": [0, 0, 0, 0, 0, 0, 0, -1], "sim": 0, "cap": [0, 0, 0, 0, 0, 0, -1], "gear": [0, 1400, 0], "wt": [0, 0, 0, 0],
            "fw": [0, 0, 0, 0, 0, 0], "asoff": 0, "swp": 21}


def meta_json(sc):
    p = sc["params"]
    return {"shared": {k: list(v[1:]) for k, v in p["shared"].items()}, "profile": {k: list(v[1:]) for k, v in p["profile"].items()},
            "profiles": 6, "curveMin": 1, "curveMax": 4}


def settings_json(sc, idx):
    return {"active": sc["active"], "dirtyActive": False, "edit": idx, "names": sc["names"], "dirtyShared": False,
            "dirtyProfiles": [False] * 6, "shared": sc["shared"], "profile": sc["profiles"][idx]}


def synth_log(sc, seconds=240):
    """合成飛行紀錄:起飛 3 秒緩啟動,之後水平圈(每 4 秒一圈,高度角 12°),在第 40,90,140 秒各拉一個 45° 的斜爬升-俯衝,第 200 秒降落."""
    prof = sc["profiles"][sc["active"]]
    R, V = 18.0, 2 * math.pi * 18.0 / 4.0
    samples = []
    for i in range(seconds * 10):
        t = i / 10
        az = (t * 90.0) % 360
        eps, pitch = 12.0, 0.0
        for t0 in (40, 90, 140):
            if t0 <= t < t0 + 6:
                ph = (t - t0) / 6 * math.pi
                eps = 12 + 50 * math.sin(ph)
                pitch = 55 * math.cos(ph)
        if t < 3:
            state, thr, lineg = 4, prof["phase1Pct"] * t / 2 if t < 2 else prof["phase1Pct"], 0.5 + t
        elif t < 200:
            state = 5
            base = prof["phase1Pct"] if t < prof["phase1Sec"] else prof["phase2Pct"]
            comp = pitch_comp(prof, pitch) + curve_pct(prof, "sd", eps, 1) * side_factor(pitch)
            speed = V * (1 - 0.12 * math.sin(math.radians(eps)) - 0.15 * max(0, pitch) / 90)
            lineg = speed * speed / R / 9.81 - math.sin(math.radians(eps))
            if prof["compMode"] != 0:
                trim = max(-prof["gLimit"], min(prof["gLimit"], (prof["gTarget"] - lineg) * prof["gGain"]))
                comp = (comp if prof["compMode"] == 1 else 0) + trim
            thr = min(prof["maxPct"], max(prof["minPct"], base + comp))
        elif t < 215:
            state, thr, lineg, eps, pitch = 6, prof["landingPct"], 2.0, 5, -5
        else:
            state, thr, lineg, eps, pitch = 7, 0, 0.0, 0, 2
        acc = 1.0 + lineg * 0.9 + abs(pitch) / 90
        samples.append(struct.pack("<bBBBBbBBBBB", int(pitch), int(thr), int(min(25.5, acc) * 10), int(0.05 * 50), 0, 0, state,
                                   1 if (state == 5 and abs(pitch) < 20 and eps < 20) else 0, int(max(0, min(25.5, lineg)) * 10),
                                   int(max(0, min(90, eps))), int(az * 256 / 360) & 0xFF))
    return samples


class Handler(http.server.BaseHTTPRequestHandler):
    scenario = None
    html = None
    log = None

    def log_message(self, *a):
        pass

    def _send(self, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        sc = self.scenario
        path, _, q = self.path.partition("?")
        args = dict(x.split("=", 1) for x in q.split("&") if "=" in x)
        if path == "/":
            return self._send(self.html, "text/html; charset=utf-8")
        if path == "/api/meta":
            return self._send(meta_json(sc))
        if path == "/api/settings":
            return self._send(settings_json(sc, int(args.get("p", sc["edit"]))))
        if path == "/api/status":
            return self._send(status_json(sc))
        if path == "/api/events":
            return self._send({"total": 0, "oldest": 0, "ev": []})
        if path == "/api/log":
            since = int(args.get("since", 0))
            if since > len(self.log):
                since = 0
            body = struct.pack("<IIHH", since, len(self.log) - since, 100, 11) + b"".join(self.log[since:])
            return self._send(body, "application/octet-stream")
        if path == "/api/wifi":
            return self._send({"ssid": "", "pw": "", "host": "lineplane", "tmo": 20, "forceap": 0, "txp": 8, "txmin": 2, "txmax": 20, "tmomin": 5,
                               "tmomax": 120, "apssid": "HappySuperGG_Plane", "apnow": "HappySuperGG_Plane", "apprefix": "HappySuperGG_Plane",
                               "apsfx": "", "appw": "", "apsfxmax": 16, "build": "mock"})
        if path == "/api/fw":
            return self._send({"ver": "2026.10.29.2", "board": "MINI", "build": "mock", "busy": 0, "pending": 0, "remain": -1, "rb": 0, "rbver": "",
                               "check": 0, "err": "", "prog": 0, "rver": "", "newer": 0, "rsize": 0, "notes": "", "src": ""})
        if path == "/api/backup":
            return self._send({"ok": True, "code": "ok", "text": "LP-MOCK"})
        return self._send({"ok": False, "code": "nf"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else b""
        if self.path == "/mock/scenario":
            # 截圖工具改情境:{"status":{...},"profile":{索引:{鍵:值}},"active":n,"edit":n}. 風格改了就重新合成紀錄
            patch = json.loads(body.decode("utf-8") or "{}")
            sc = self.scenario
            sc["status"].update(patch.get("status", {}))
            for idx, vals in patch.get("profile", {}).items():
                sc["profiles"][int(idx)].update(vals)
            for k in ("active", "edit"):
                if k in patch:
                    sc[k] = patch[k]
            if "profile" in patch or "active" in patch:
                type(self).log = synth_log(sc)
            return self._send({"ok": True})
        return self._send({"ok": True, "code": "ok"})


def make_server(port=0, scenario=None):
    sc = scenario or default_scenario()
    cls = type("H", (Handler,), {"scenario": sc, "html": page_html(), "log": synth_log(sc)})
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), cls)
    return srv, sc


def serve_in_thread(scenario=None):
    srv, sc = make_server(0, scenario)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv, sc, f"http://127.0.0.1:{srv.server_address[1]}"


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv, sc = make_server(port)
    print(f"假伺服器 http://127.0.0.1:{port}/#tab-comp  (Ctrl+C 結束)")
    srv.serve_forever()
