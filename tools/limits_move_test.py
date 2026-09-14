# 版本流水號: r2 (2026-09-14) 參數按鈕改成 −/+ 兩顆
# 舊: r1 (2026-09-14) 油門上下限搬到角度補償頁撞牆檢查下方:位置,預設收起,展開可改值,重建面板保持展開,計時器頁已移除
# penv python. 會改設定(只改 RAM):確認待機且無未儲存 → 備份 → 測試 → 放棄變更並還原比對. 會存兩張截圖到 %TEMP%.
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

if len(sys.argv) > 1:
    os.environ["LP_HOST"] = sys.argv[1]
import websockets  # noqa: E402

import lp_test as T  # noqa: E402

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP_PORT = 9339
SHOT = tempfile.gettempdir()

T.init("limits_move_test")
T.protect()


async def main():
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

            async def js(expr):
                r = await call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
                return r.get("result", {}).get("value")

            async def shot(name):
                r = await call("Page.captureScreenshot", format="png")
                p = os.path.join(SHOT, name)
                with open(p, "wb") as f:
                    f.write(base64.b64decode(r["data"]))
                return p

            await call("Runtime.enable")
            await call("Emulation.setDeviceMetricsOverride", width=412, height=900, deviceScaleFactor=1, mobile=True)
            await call("Page.navigate", url=f"http://{T.HOST}/#tab-prof")
            await asyncio.sleep(7)
            edit = await js("VALS.edit")
            cards = await js("[...document.querySelectorAll('#profCards .prm .nm')].map(h=>h.textContent)")
            T.check(f"計時器頁已沒有油門上下限(目前:{cards})", not any("油門上限" in c or "油門下限" in c for c in cards) and len(cards) >= 8, cards)

            await js("document.querySelector('nav button[data-pane=comp]').click()")
            await asyncio.sleep(2)
            info = await js("(()=>{const d=document.getElementById('cvLim');if(!d)return null;"
                            "return {open:d.open,prevId:d.previousElementSibling&&d.previousElementSibling.id,last:d.parentNode.lastElementChild===d,"
                            "parent:d.parentNode.id,inputs:d.querySelectorAll('.val').length,labels:[...d.querySelectorAll('.prm')].map(e=>e.textContent.slice(0,8)),"
                            "h:d.getBoundingClientRect().height}})()")
            T.log("  cvLim:", info)
            T.check("角度補償頁有「油門上下限」區塊,在撞牆檢查正下方,是面板最後一塊", info and info["prevId"] == "cvWall" and info["last"] and info["parent"] == "curvePanel", info)
            T.check(f"預設收起(高度 {info['h']:.0f}px)", info and info["open"] is False and info["h"] < 60, info)
            await js("document.getElementById('cvLim').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.5)
            print("  截圖(收起):", await shot("lp_limits_closed.png"))

            await js("document.querySelector('#cvLim summary').click()")
            await asyncio.sleep(0.5)
            info = await js("(()=>{const d=document.getElementById('cvLim');return {open:d.open,h:d.getBoundingClientRect().height,"
                            "labels:[...d.querySelectorAll('.prm')].map(e=>e.textContent.slice(0,8))}})()")
            T.check(f"點標題展開:出現下限與上限({info['labels']})", info["open"] and info["h"] > 100 and len(info["labels"]) == 2, info)
            print("  截圖(展開):", await shot("lp_limits_open.png"))

            before = T.get(f"/api/settings?p={edit}")["profile"]
            newmax = before["maxPct"] - 1
            await js(f"(()=>{{const i=[...document.querySelectorAll('#cvLim .prm')].find(e=>e.textContent.includes('上限')).querySelector('.val');"
                     f"i.value='{newmax}';i.dispatchEvent(new Event('change'))}})()")
            await asyncio.sleep(1.5)
            after = T.get(f"/api/settings?p={edit}")["profile"]
            T.check(f"展開後改上限 {before['maxPct']} → {after['maxPct']}", after["maxPct"] == newmax, after["maxPct"])
            await js("document.querySelector('#cvLim .prm .ctl .st[data-d=\"-1\"]').click()")   # 下限 −
            await asyncio.sleep(1.5)
            after2 = T.get(f"/api/settings?p={edit}")["profile"]
            T.check(f"下限 − 按鈕:{before['minPct']} → {after2['minPct']}", after2["minPct"] < before["minPct"] or before["minPct"] <= 10, after2["minPct"])   # 下限最低 10%(韌體 settings r17)

            # 切換選取(面板重建)後仍展開,且仍在最後
            await js("cvSel={t:'db',side:'up'};buildCurvePanel();drawCurve()")
            await asyncio.sleep(0.5)
            await js("cvSel={t:'pt',side:'up',i:1};buildCurvePanel();drawCurve()")
            await asyncio.sleep(0.5)
            await js("document.querySelector('#cvPhase button[data-ph=\"2\"]').click()")
            await asyncio.sleep(0.8)
            info = await js("(()=>{const d=document.getElementById('cvLim');return d&&{open:d.open,prevId:d.previousElementSibling.id,last:d.parentNode.lastElementChild===d}})()")
            T.check("切換選取與切到第二段後:仍保持展開,仍在撞牆檢查下方", info and info["open"] and info["prevId"] == "cvWall" and info["last"], info)
            T.post("/api/revert")
            await asyncio.sleep(1)
            T.check("頁面沒有 JS 錯誤", not errs, errs)
    finally:
        edge.terminate()


asyncio.run(main())
T.post("/api/revert")
T.restore_and_verify()
sys.exit(T.finish())
