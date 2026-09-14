# 版本流水號: r2 (2026-09-14) 拿掉「開始更新」事件來源檢查(舊韌體記的,重開後清空,本來就看不到);手動上傳改驗證不確認自動退回
# 舊: r1 (2026-09-14) 初版:韌體更新的另外三條路實測:網頁自動確認(真的瀏覽器),手動上傳韌體檔,無線燒錄
# ============================================================================
# 1. 瀏覽器開系統頁 → 按「檢查更新」看文字 → 用 API 安裝同版本 → 瀏覽器不關,板子重開回來後網頁自己送確認 → 待確認解除
# 2. POST /update 上傳 .pio/build 的 firmware.bin(與網頁「手動上傳韌體檔」同一個 API)→ 重開待確認 → 事件來源 0 → API 確認
# 3. pio run -e ota -t upload(無線燒錄)→ 重開待確認 → 事件來源 1 → API 確認
# 板子要在待機且沒有未儲存變更. 設定先備份,結束還原比對. penv python(要 websockets).
# ============================================================================
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid

os.environ.setdefault("LP_HOST", "lineplane.local")
import websockets  # noqa: E402

import lp_test as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP_PORT = 9351
PIO = os.path.join(os.environ["USERPROFILE"], ".platformio", "penv", "Scripts", "pio.exe")
BIN = os.path.join(ROOT, ".pio", "build", "esp32c3_supermini", "firmware.bin")

T.init("fw_paths_test")
T.protect()


def fw():
    return T.get("/api/fw")


def wait_reboot(up_before, timeout=150):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            s = T.get("/api/status")
            if s["up"] < up_before:
                return s
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.5)
    return None


def started_sources():
    return [round(e[4]) for e in T.events(0)["ev"] if e[2] == 25 and e[3] == 3]


# ---- 1. 瀏覽器自動確認 ----
async def browser():
    tmp = tempfile.mkdtemp(prefix="lp_cdp_")
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}", f"--remote-debugging-port={CDP_PORT}",
                             "--window-size=412,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(40):
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=2).read())
                pages = [t for t in tabs if t.get("type") == "page"]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.5)
        async with websockets.connect(ws_url, max_size=50_000_000) as ws:
            n = 0
            errs = []

            async def call(method, **params):
                nonlocal n
                n += 1
                my = n
                await ws.send(json.dumps({"id": my, "method": method, "params": params}))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get("method") == "Runtime.exceptionThrown":
                        errs.append(m["params"]["exceptionDetails"].get("text"))
                    if m.get("id") == my:
                        return m.get("result", {})

            async def js(e):
                r = await call("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True)
                return r.get("result", {}).get("value")

            await call("Runtime.enable")
            await call("Emulation.setDeviceMetricsOverride", width=412, height=900, deviceScaleFactor=1, mobile=True)
            await call("Page.navigate", url=f"http://{T.HOST}/#tab-sys")
            await asyncio.sleep(7)
            ver = await js("document.getElementById('fwVer').textContent")
            T.check(f"系統頁顯示韌體版本 {ver}", ver == fw()["ver"], ver)
            await js("document.getElementById('btnFwCheck').click()")
            txt = ""
            for _ in range(30):
                await asyncio.sleep(0.5)
                txt = await js("document.getElementById('fwCheckText').textContent")
                if "最新版" in txt or "新版本" in txt or "失敗" in txt or "連不上" in txt:
                    break
            hidden = await js("document.getElementById('btnFwInstall').hidden")
            T.check(f"按檢查更新:「{txt}」,同版本不顯示更新按鈕", "已是最新版" in txt and hidden, (txt, hidden))
            notes = await js("document.getElementById('fwNotes').textContent")
            T.check(f"顯示更新說明:「{notes[:40]}」", "修正" in notes, notes)
            # 用 API 安裝同版本,瀏覽器不關
            up = T.status()["up"] + 1
            r = T.post("/api/fw/install", ver=fw()["rver"])
            T.check(f"開始安裝:{r}", r["ok"], r)
            bar_seen = False
            for _ in range(80):
                await asyncio.sleep(0.5)
                b = await js("(()=>{const e=document.getElementById('fwBar');return e.hidden?'':e.textContent})()")
                if "下載安裝中" in b:
                    bar_seen = True
                    break
            T.check("頁首出現「韌體下載安裝中 xx%,請勿斷電」", bar_seen)
            s = await asyncio.get_event_loop().run_in_executor(None, wait_reboot, up)
            T.check("板子重開回來", s is not None)
            t0 = time.time()
            pend = None
            while time.time() - t0 < 30:
                await asyncio.sleep(1)
                pend = fw()["pending"]
                if pend == 0:
                    break
            T.check(f"網頁沒有重新整理,板子回來後自動確認({time.time() - t0:.0f} 秒內,待確認 {pend})", pend == 0, pend)
            ev = [e[3] for e in T.events(0)["ev"] if e[2] == 25]
            T.check(f"事件:待確認 → 已確認 {ev}", 1 in ev and 0 in ev, ev)
            await asyncio.sleep(2)
            bar = await js("document.getElementById('fwBar').hidden")
            T.check("確認後頁首提示消失", bar is True, bar)
            T.check("頁面沒有 JS 錯誤", not errs, errs)
    finally:
        edge.terminate()


asyncio.run(browser())
time.sleep(3)

# ---- 2. 手動上傳韌體檔(POST /update)----
T.log("\n== 手動上傳韌體檔 ==")
with open(BIN, "rb") as f:
    data = f.read()
boundary = uuid.uuid4().hex
body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"firmware\"; filename=\"firmware.bin\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
up = T.status()["up"] + 1
req = urllib.request.Request(f"http://{T.HOST}/update", data=body)
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
t0 = time.time()
try:
    r = json.loads(urllib.request.urlopen(req, timeout=180).read())
except urllib.error.HTTPError as e:
    r = json.loads(e.read())
T.check(f"上傳 {len(data)} 位元組完成({time.time() - t0:.0f} 秒):{r}", r.get("ok"), r)
s = wait_reboot(up)
f2 = fw()
T.check(f"重開後待確認(剩 {f2['remain']} 秒)", s is not None and f2["pending"] == 1, f2)
# 「開始更新」事件在舊韌體記錄,重開後事件紀錄清空看不到;改驗證上傳路徑也有記下預期分區:不確認 → 自動退回並提示
r = T.cmd("fwwin 20", expect="OK")
T.check(f"不確認,縮短時限 20 秒:{r}", "OK" in r, r)
s = wait_reboot(T.status()["up"], 90)
f2b = fw()
T.check(f"手動上傳沒確認:自動退回,網頁顯示已退回(上傳不知道版本,被退回版本空白):{f2b}", s is not None and f2b["pending"] == 0 and f2b["rb"] == 1, f2b)
ev = [e[3] for e in T.events(0)["ev"] if e[2] == 25]
T.check(f"事件:上次更新沒確認已退回(25/2):{ev}", 2 in ev, ev)

# ---- 3. 無線燒錄 ----
T.log("\n== 無線燒錄(pio -e ota)==")
up = T.status()["up"] + 1
p = subprocess.run([PIO, "run", "-e", "ota", "-t", "upload", "--upload-port", T.HOST], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
T.check("pio 無線燒錄成功", p.returncode == 0, p.stdout[-600:])
s = wait_reboot(up)
f3 = fw()
T.check(f"重開後待確認(剩 {f3['remain']} 秒)", s is not None and f3["pending"] == 1, f3)
r = T.post("/api/fw/confirm")
T.check(f"API 確認:{r}", r["ok"] and fw()["pending"] == 0, r)
st = T.wait_state("standby", 8)
T.check("停在待機,沒有自己倒數", T.fstate(st) == "standby", T.fstate(st))

T.restore_and_verify()
sys.exit(T.finish())
