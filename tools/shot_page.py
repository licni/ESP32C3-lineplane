# 版本流水號: r1 (2026-09-13) 無頭 Edge 截圖工具:指定分頁,捲到某個元素,淺色/深色,回報 JS 例外
# 用法: penv python tools/shot_page.py 板子位址 分頁(mon/prof/comp/set/log/inst/esc/sys) CSS選擇器 輸出檔前綴 [dark]
import asyncio
import base64
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets

HOST, PANE, SEL, OUT = sys.argv[1:5]
DARK = len(sys.argv) > 5 and sys.argv[5] == "dark"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9336


async def main():
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

            await call("Runtime.enable")
            await call("Page.enable")
            await call("Emulation.setDeviceMetricsOverride", width=412, height=900, deviceScaleFactor=1, mobile=True)
            if DARK:
                await call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
            await call("Page.navigate", url=f"http://{HOST}/#tab-{PANE}")
            await asyncio.sleep(6)
            r = await call("Runtime.evaluate", returnByValue=True, expression=
                           f"(()=>{{const e=document.querySelector({json.dumps(SEL)});if(!e)return null;e.scrollIntoView({{block:'center'}});"
                           f"const r=e.getBoundingClientRect();return [r.top,r.height]}})()")
            await asyncio.sleep(1)
            print("element", r.get("result", {}).get("value"))
            shot = await call("Page.captureScreenshot", format="png")
            path = f"{OUT}{'_dark' if DARK else ''}.png"
            with open(path, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print("saved", path, "js errors:", errs)
    finally:
        edge.terminate()


asyncio.run(main())
