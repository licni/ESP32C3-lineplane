# 版本流水號: r1 (2026-09-13) 板上設定備份/還原/比對,測試前確認待機
# ============================================================================
# 為什麼要有:GG 會在板子上調參數實測. 測試程式改寫設定後若只「回預設」,會把 GG 調好的值洗掉.
# 所有會改設定的測試一律:require_idle() → backup() → 測試 → restore().
# 單獨執行:python tools/board_backup.py save 檔名.json | restore 檔名.json | diff 檔名.json [板子位址]
# ============================================================================
import json
import sys
import urllib.parse
import urllib.request

STATE = ["arming", "standby", "wait_still", "countdown", "takeoff", "flying", "landing", "done"]


def _get(host, path):
    return json.loads(urllib.request.urlopen(f"http://{host}{path}", timeout=8).read())


def _post(host, path, data=None, raw=None, ctype=None):
    body = raw if raw is not None else urllib.parse.urlencode(data or {}).encode()
    req = urllib.request.Request(f"http://{host}{path}", data=body)
    if ctype:
        req.add_header("Content-Type", ctype)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def require_idle(host):
    st = _get(host, "/api/status")
    s = STATE[st["f"]["s"]]
    if s not in ("arming", "standby", "done") or st["lock"]:
        raise SystemExit(f"板子不在待機({s}),可能有人正在實測,測試中止,不動任何設定.")
    if st["dirty"]:
        raise SystemExit("板子有未儲存的變更(可能是 GG 正在調),測試中止,不動任何設定.")


def backup(host):
    first = _get(host, "/api/settings?p=0")
    snap = {"active": first["active"], "names": first["names"], "shared": first["shared"], "profiles": []}
    for i in range(len(first["names"])):
        snap["profiles"].append(_get(host, f"/api/settings?p={i}")["profile"])
    # 同時存一份檔案:測試中途當掉時可用 `board_backup.py restore 檔名` 手動救回
    import os, tempfile, time
    path = os.path.join(tempfile.gettempdir(), time.strftime("lineplane_backup_%Y%m%d_%H%M%S.json"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    print("  (板上設定已備份到", path, ")")
    return snap


def _lines(values):
    return "\n".join(f"{k}={v}" for k, v in values.items()).encode()


def restore(host, snap):
    """整批寫回並儲存. 回傳錯誤訊息清單(空 = 成功)."""
    errs = []
    r = _post(host, "/api/setmany?p=s", raw=_lines(snap["shared"]), ctype="text/plain")
    if not r["ok"]:
        errs.append(("shared", r))
    for i, prof in enumerate(snap["profiles"]):
        r = _post(host, f"/api/setmany?p={i}", raw=_lines(prof), ctype="text/plain")
        if not r["ok"]:
            errs.append((f"profile {i}", r))
        r = _post(host, "/api/name", {"p": i, "name": snap["names"][i]})
        if not r["ok"]:
            errs.append((f"name {i}", r))
    r = _post(host, "/api/select", {"p": snap["active"]})
    if not r["ok"]:
        errs.append(("select", r))
    r = _post(host, "/api/save")
    if not r["ok"]:
        errs.append(("save", r))
    return errs


def diff(a, b):
    """比對兩份快照,回傳不同處. 新版多出來的鍵(舊快照沒有)不算差異."""
    out = []
    if a["active"] != b["active"]:
        out.append(("active", a["active"], b["active"]))
    if a["names"] != b["names"]:
        out.append(("names", a["names"], b["names"]))
    for k, v in a["shared"].items():
        if k in b["shared"] and b["shared"][k] != v:
            out.append((f"shared.{k}", v, b["shared"][k]))
    for i, (pa, pb) in enumerate(zip(a["profiles"], b["profiles"])):
        for k, v in pa.items():
            if k in pb and pb[k] != v:
                out.append((f"p{i}.{k}", v, pb[k]))
    return out


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    host = sys.argv[3] if len(sys.argv) > 3 else "lineplane.local"
    if cmd == "save":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(backup(host), f, ensure_ascii=False, indent=1)
        print("saved", path)
    elif cmd == "restore":
        require_idle(host)
        with open(path, encoding="utf-8") as f:
            print(restore(host, json.load(f)) or "restored")
    elif cmd == "diff":
        with open(path, encoding="utf-8") as f:
            d = diff(json.load(f), backup(host))
        print("\n".join(map(str, d)) if d else "相同")
