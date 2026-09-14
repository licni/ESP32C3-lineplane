# 版本流水號: r1 (2026-09-14) README 用的網頁截圖(手機寬 412,淺色):監看,計時器,角度補償,設定,電變. 不拍系統頁(有家用 WiFi 名稱)
# 用法: penv python tools/readme_shots.py [板子位址]   輸出到 docs/images/
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets

HOST = sys.argv[1] if len(sys.argv) > 1 else "lineplane.local"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "images")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9357
# (分頁, 檔名, 捲到哪個元素的上緣, 截圖高度)
SHOTS = [("mon", "web_monitor.png", None, 900), ("prof", "web_timer.png", None, 900), ("comp", "web_curve.png", None, 1000),
         ("set", "web_settings.png", None, 900), ("esc", "web_esc.png", None, 900)]


async def main():
    os.makedirs(OUT, exist_ok=True)
    prof = tempfile.mkdtemp(prefix="lp_cdp_")
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", f"--remote-debugging-port={PORT}",
                             "--window-size=412,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(40):
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=2).read())
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
            await call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
            await call("Page.navigate", url=f"http://{HOST}/")
            await asyncio.sleep(7)
            for pane, name, sel, h in SHOTS:
                await call("Emulation.setDeviceMetricsOverride", width=412, height=h, deviceScaleFactor=2, mobile=True)
                await js(f"document.querySelector('nav button[data-pane={pane}]').click();window.scrollTo(0,0)")
                await asyncio.sleep(2.5)
                # 頁首網路狀態只寫「家用 WiFi」,不含名稱;保險起見把 IP/名稱類欄位隱藏
                await js("document.querySelectorAll('#netIp,#netHost').forEach(e=>e.textContent='--')")
                shot = await call("Page.captureScreenshot", format="png")
                path = os.path.join(OUT, name)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(shot["data"]))
                print("saved", path, os.path.getsize(path) // 1024, "KB")
            print("js errors:", errs)
    finally:
        edge.terminate()


asyncio.run(main())
