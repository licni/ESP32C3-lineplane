# 版本流水號: r1 (2026-09-13) 熱點名稱後綴測試:驗證規則,不送後綴沿用,改名後重開機實際廣播並用固定密碼連入,還原
# 需要電腦無線網卡(netsh). 會暫時新增連新熱點名稱用的 WiFi 設定檔,結束刪除. 結束時 WiFi 設定還原成測試前.
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

HOST = "192.168.4.1"
PREFIX = "HappySuperGG_Plane"
TEMP_PROFILE = "LP_TEST_APNAME"
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    passed += bool(cond)
    failed += not cond
    print("  OK  " if cond else "  FAIL", name, "" if cond else detail, flush=True)


def get():
    return json.loads(urllib.request.urlopen(f"http://{HOST}/api/wifi", timeout=6).read())


def post(path, data):
    req = urllib.request.Request(f"http://{HOST}{path}", data=urllib.parse.urlencode(data).encode())
    try:
        return json.loads(urllib.request.urlopen(req, timeout=6).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def form(w, **over):
    d = {"ssid": w["ssid"], "pw": w["pw"], "host": w["host"], "tmo": w["tmo"], "forceap": w["forceap"], "txp": w["txp"]}
    d.update(over)
    return d


def netsh(*args):
    return subprocess.run(["netsh", "wlan", *args], capture_output=True, text=True, encoding="cp950", errors="replace").stdout


def wait_http(timeout=40):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            return get()
        except Exception:  # noqa: BLE001
            time.sleep(1)
    return None


def connect(profile):
    for _ in range(3):
        netsh("connect", f"name={profile}", "interface=Wi-Fi")
        w = wait_http(25)
        if w:
            return w
    return None


def reboot():
    post("/api/reboot", {})
    time.sleep(8)


w0 = get()
print("測試前 WiFi 設定:", {k: w0.get(k) for k in ("ssid", "host", "tmo", "forceap", "txp", "apssid", "apsfx", "apnow")})
check("燒錄後熱點名稱仍是固定開頭,後綴空白", w0["apssid"] == PREFIX and w0["apsfx"] == "" and w0["apnow"] == PREFIX and w0["apprefix"] == PREFIX, w0)

# ---- 驗證規則(都不會存)----
for sfx, code, name in (("A" * 15, "apsfxlong", "15 個英數字"), ("中文字五個", "apsfxlong", "5 個中文字(15 位元組)"),
                        (" 3", "apsfxspace", "開頭空白"), ("3 ", "apsfxspace", "結尾空白"), ("a\x01b", "apsfxbad", "控制字元")):
    r = post("/api/wifi", form(w0, apsfx=sfx))
    check(f"拒絕{name}({code})", not r["ok"] and r["code"] == code, r)
check("被拒絕後後綴沒變", get()["apsfx"] == "")
r = post("/api/wifi", form(w0, apsfx="A" * 14))
check("14 個英數字可以", r["ok"] and get()["apssid"] == PREFIX + "A" * 14, r)
r = post("/api/wifi", form(w0, apsfx="三號機"))
check("中文 3 字(9 位元組)可以", r["ok"] and get()["apssid"] == PREFIX + "三號機", (r, get()["apssid"]))
r = post("/api/wifi", form(w0, apsfx="2 號"))
check("中間有空白可以", r["ok"] and get()["apsfx"] == "2 號", r)
r = post("/api/wifi", form(w0))
check("沒送後綴:沿用目前的(2 號)", r["ok"] and get()["apsfx"] == "2 號", get()["apsfx"])
r = post("/api/wifi", form(w0, apsfx="3", appw="99999999", appassword="99999999"))
w = get()
check("存成 3:下次開機名稱 HappySuperGG_Plane3,目前廣播的還是舊名稱", r["ok"] and w["apssid"] == PREFIX + "3" and w["apnow"] == PREFIX, w)
check("API 沒有熱點密碼欄位可改(送了也被忽略)", "appw" not in w and "appassword" not in w)

# ---- 重開機實際廣播 ----
print("== 重開機,掃描新熱點名稱 ==", flush=True)
reboot()
seen = False
for _ in range(10):
    netsh("disconnect", "interface=Wi-Fi")
    out = netsh("show", "networks", "mode=bssid")
    if f"{PREFIX}3" in out:
        seen = True
        break
    time.sleep(3)
check("電腦掃描到熱點 HappySuperGG_Plane3", seen)
xml = f"""<?xml version="1.0"?><WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1"><name>{TEMP_PROFILE}</name>
<SSIDConfig><SSID><name>{PREFIX}3</name></SSID></SSIDConfig><connectionType>ESS</connectionType><connectionMode>manual</connectionMode>
<MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption>
<sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>12345678</keyMaterial></sharedKey></security></MSM></WLANProfile>"""
path = os.path.join(tempfile.gettempdir(), "lp_test_apname.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(xml)
netsh("add", "profile", f"filename={path}", "interface=Wi-Fi")
w = connect(TEMP_PROFILE)
check("用固定密碼 12345678 連上新名稱的熱點,網頁可用,目前廣播名稱 = HappySuperGG_Plane3", w and w["apnow"] == PREFIX + "3", w)

# ---- 還原 ----
print("== 還原測試前的 WiFi 設定並重開機 ==", flush=True)
if w:
    r = post("/api/wifi", form(w0, apsfx=w0["apsfx"]))
    check("還原寫入", r["ok"], r)
    reboot()
netsh("delete", "profile", f"name={TEMP_PROFILE}")
w = connect("HappySuperGG_Plane")
check("重開後連回原本熱點 HappySuperGG_Plane", w and w["apnow"] == PREFIX, w)
if w:
    same = all(w[k] == w0[k] for k in ("ssid", "pw", "host", "tmo", "forceap", "txp", "apssid", "apsfx"))
    check("WiFi 設定與測試前完全相同", same, w)
print(f"\n通過 {passed},失敗 {failed}")
sys.exit(1 if failed else 0)
