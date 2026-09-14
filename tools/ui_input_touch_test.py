# 版本流水號: r1 (2026-09-14) 網頁輸入與觸控:數值框打錯誤內容(負值/超範圍/文字/半數字/空白)被擋下並顯示回實際值;
# 角度補償圖上手指滑動不捲動網頁,圖外照常捲;手指拖曲線點可改值. 手機模擬(412px,觸控). penv python.
# 會改設定(只改 RAM):確認待機且無未儲存 → 備份 → 測試 → 放棄變更並還原比對.
import asyncio
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
CDP_PORT = 9338

T.init("ui_input_touch_test")
T.protect()


EDIT = [None]   # 網頁正在編輯的風格編號(從頁面讀)


def prof():
    return T.get(f"/api/settings?p={EDIT[0]}")["profile"]


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

            await call("Runtime.enable")
            await call("Page.enable")
            await call("Emulation.setDeviceMetricsOverride", width=412, height=900, deviceScaleFactor=1, mobile=True)
            await call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
            await call("Page.navigate", url=f"http://{T.HOST}/#tab-prof")
            await asyncio.sleep(7)
            EDIT[0] = await js("VALS.edit")
            T.log(f"  網頁正在編輯第 {EDIT[0] + 1} 組")

            # ---- 數值框 ----
            T.log("\n== 數值框打錯誤內容(計時器頁「第一段基本油門」)==")
            find = ("[...document.querySelectorAll('#prof .prm')].find(e=>e.textContent.includes('第一段基本油門')).querySelector('.val')")
            before = prof()["phase1Pct"]
            for text, name in (("-1", "負值"), ("150", "超過 100"), ("abc", "文字"), ("12abc", "數字接文字"), ("", "清空"), ("  ", "只有空白")):
                await js(f"(()=>{{const i={find};i.scrollIntoView({{block:'center'}});i.focus();i.select();}})()")
                await call("Input.dispatchKeyEvent", type="keyDown", key="Backspace", code="Backspace", windowsVirtualKeyCode=8)
                await call("Input.dispatchKeyEvent", type="keyUp", key="Backspace", code="Backspace", windowsVirtualKeyCode=8)
                if text:
                    await call("Input.insertText", text=text)
                await call("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13)
                await call("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13)
                await asyncio.sleep(1.5)
                shown = await js(f"{find}.value")
                toast = await js("(()=>{const t=document.getElementById('toast');return t.hidden?'':t.textContent})()")
                now = prof()["phase1Pct"]
                T.check(f"{name}「{text}」:板上值不變({now}),框內顯示回 {shown!r},提示「{toast}」",
                        now == before and shown is not None and float(shown) == before and toast != "", (now, shown, toast))
            await js(f"(()=>{{const i={find};i.focus();i.select();}})()")
            await call("Input.insertText", text=str(before + 1))
            await call("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13)
            await asyncio.sleep(1.5)
            T.check(f"正確值 {before + 1}:寫入成功,框內顯示 {await js(f'{find}.value')}", prof()["phase1Pct"] == before + 1)
            T.post("/api/revert")
            await js("loadVals()")
            await asyncio.sleep(1)

            # ---- 觸控捲動 ----
            T.log("\n== 角度補償圖:手指滑動 ==")
            await js("document.querySelector('nav button[data-pane=comp]').click()")   # r1:改 location.hash 不會切分頁
            await asyncio.sleep(2)
            box = await js("(()=>{const s=document.getElementById('cvSvg');s.scrollIntoView({block:'center'});const r=s.getBoundingClientRect();"
                           "return [r.left,r.top,r.width,r.height,getComputedStyle(s).touchAction]})()")
            await asyncio.sleep(0.5)
            T.log("  曲線圖位置", box)
            T.check("(前提)曲線圖有顯示在畫面上", box[2] > 100 and box[3] > 100, box)
            # web_page r41 起改成 pinch-zoom(單指不捲頁,雙指縮放交給瀏覽器),這裡跟著改
            T.check("曲線圖設定 touch-action:pinch-zoom(單指不捲頁,雙指可縮放)", box[4] == "pinch-zoom", box[4])
            # r3:synthesizeScrollGesture 在無頭 Edge 任何地方都捲不動(對照組也不動),改用逐點觸控事件
            async def swipe(x, y, dy, steps=12):
                ya = await js("window.scrollY")
                await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
                for k in range(1, steps + 1):
                    await call("Input.dispatchTouchEvent", type="touchMove", touchPoints=[{"x": x, "y": y + dy * k / steps}])
                    await asyncio.sleep(0.016)
                await call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
                await asyncio.sleep(0.8)
                return ya, await js("window.scrollY")

            # 對照組:圖外一般內容上滑動,確認觸控事件真的能捲網頁,否則「圖內不動」不算數
            outs = await js("(()=>{const r=document.getElementById('cvSvg').getBoundingClientRect();"
                            "const y=Math.min(innerHeight-60,r.bottom+60);const e=document.elementFromPoint(innerWidth/2,y);"
                            "return [innerWidth/2,y,e?e.tagName+'.'+e.className:'',!!(e&&e.closest('#cvSvg'))]})()")
            T.log("  圖外位置", outs)
            ya, yb = await swipe(outs[0], outs[1], -200)
            T.check(f"(對照組)手指在圖外往上滑:網頁會捲動(scrollY {ya} → {yb})", not outs[3] and yb - ya > 50, (ya, yb))
            await js("document.getElementById('cvSvg').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.5)
            box = await js("(()=>{const r=document.getElementById('cvSvg').getBoundingClientRect();return [r.left,r.top,r.width,r.height]})()")
            # 圖內空白處(避開點與把手)
            xin, yin = box[0] + box[2] * 0.55, box[1] + box[3] * 0.5
            hit = await js(f"(()=>{{const e=document.elementFromPoint({xin},{yin});return [!!e.closest('#cvSvg'),!!e.closest('[data-h]')]}})()")
            T.log("  圖內位置在曲線圖上 / 在點或把手上:", hit)
            ya, yb = await swipe(xin, yin, -200)
            T.check(f"手指在曲線圖內空白處往上滑:網頁不動(scrollY {ya} → {yb})", hit[0] and abs(yb - ya) < 2, (ya, yb))
            ya, yb = await swipe(xin, yin, 200)
            T.check(f"手指在曲線圖內空白處往下滑:網頁不動(scrollY {ya} → {yb})", hit[0] and abs(yb - ya) < 2, (ya, yb))

            # ---- 手指拖曲線點 ----
            await js("document.getElementById('cvSvg').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.5)
            p0 = prof()
            pt = await js("(()=>{const e=document.querySelector('#cvSvg [data-h=pt][data-side=up][data-i=\"1\"]');const r=e.getBoundingClientRect();"
                          "return [r.left+r.width/2,r.top+r.height/2]})()")
            sy = await js("window.scrollY")
            x, y = pt
            await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
            for k in range(1, 9):
                await call("Input.dispatchTouchEvent", type="touchMove", touchPoints=[{"x": x + 5 * k, "y": y}])
                await asyncio.sleep(0.03)
            await call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
            await asyncio.sleep(2.5)
            p1 = prof()
            sy2 = await js("window.scrollY")
            T.check(f"手指拖朝上點 1 往右 40px:補償 {p0['up1p']} → {p1['up1p']},網頁沒捲動({sy} → {sy2})",
                    p1["up1p"] != p0["up1p"] and abs(sy2 - sy) < 2, (p0["up1p"], p1["up1p"], sy, sy2))
            T.post("/api/revert")
            T.check("頁面沒有 JS 錯誤", not errs, errs)
    finally:
        edge.terminate()


asyncio.run(main())
T.log("\n== 收尾 ==")
T.post("/api/revert")
T.restore_and_verify()
sys.exit(T.finish())
