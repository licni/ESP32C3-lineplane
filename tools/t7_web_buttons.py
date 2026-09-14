# 版本流水號: r1 (2026-09-13) 全功能測試 段 7:網頁取消倒數與緊急停止按鈕(無頭 Edge,真的滑鼠點擊)
# 規格:取消倒數單按即可;緊急停止飛行中連按三下才生效(1.5 秒內沒按滿三下重新計算).
# 需要 penv 的 python(內建 websockets). 會改設定:備份,結尾還原並比對.
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets

import lp_test as T

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP_PORT = 9334

T.init("t7_web_buttons")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")
T.configure(shared={"disturbMode": 2})


class Cdp:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    async def call(self, method, **params):
        self.n += 1
        my = self.n
        await self.ws.send(json.dumps({"id": my, "method": method, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == my:
                return msg.get("result", {})

    async def js(self, expr):
        r = await self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")

    async def click(self, sel):
        xy = await self.js(f"(()=>{{const e=document.querySelector('{sel}');if(!e||e.hidden)return null;"
                           f"const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}})()")
        if not xy:
            return False
        for t in ("mousePressed", "mouseReleased"):
            await self.call("Input.dispatchMouseEvent", type=t, x=xy[0], y=xy[1], button="left", clickCount=1)
        return True


async def wait_js(c, expr, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if await c.js(expr):
            return True
        await asyncio.sleep(0.1)
    return False


async def main():
    prof = tempfile.mkdtemp(prefix="lp_cdp_")
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", f"--remote-debugging-port={CDP_PORT}",
                             "--window-size=600,1000", f"http://{T.HOST}/#tab-mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(40):
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=2).read())
                pages = [t for t in tabs if t.get("type") == "page" and T.HOST in t.get("url", "")]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.5)
        async with websockets.connect(ws_url, max_size=20_000_000) as ws:
            c = Cdp(ws)
            await c.call("Page.enable")
            await c.call("Runtime.enable")
            await asyncio.sleep(5)
            T.sim("att 0 0 1.0")
            # --- 取消倒數 ---
            T.gesture_push(2.5)
            T.wait_state("countdown", 4)
            vis = await wait_js(c, "!document.getElementById('btnCancel').hidden", 3)
            T.check("倒數中網頁出現「取消倒數」鈕,不出現緊急停止", vis and await c.js("document.getElementById('btnEstop').hidden"))
            await c.click("#btnCancel")
            st = T.wait_state("standby", 2)
            T.check("取消倒數單按一次 → 待機(er=7)", T.fstate(st) == "standby" and st["f"]["er"] == 7, st["f"])
            # --- 緊急停止 ---
            T.gesture_push(2.5)
            T.wait_state("flying", 12)
            vis = await wait_js(c, "!document.getElementById('btnEstop').hidden", 3)
            T.check("飛行中出現緊急停止鈕", vis)
            await c.click("#btnEstop")
            await asyncio.sleep(0.3)
            label = await c.js("document.getElementById('btnEstop').textContent")
            T.check(f"按一下:不停,按鈕顯示「{label}」", T.fstate() == "flying" and "2" in label, label)
            await c.click("#btnEstop")
            await asyncio.sleep(1.7)
            label = await c.js("document.getElementById('btnEstop').textContent")
            T.check(f"按兩下後停 1.7 秒:計數重來,按鈕回「{label}」,仍在飛行", T.fstate() == "flying" and "連按三下" in label, label)
            await c.click("#btnEstop")
            await asyncio.sleep(0.2)
            T.check("計數重來後再按一下:不停", T.fstate() == "flying")
            await c.click("#btnEstop")
            await asyncio.sleep(0.15)
            await c.click("#btnEstop")
            st = T.wait_state("done", 1.5)
            T.check("1.5 秒內按滿三下 → 緊急停止(er=6)", T.fstate(st) == "done" and st["f"]["er"] == 6, st["f"])
            hidden = await wait_js(c, "document.getElementById('btnEstop').hidden", 3)
            T.check("停止後緊急停止鈕隱藏", hidden)
            errs = await c.js("window.__errs||0")
            T.log("  (頁面 JS 例外計數)", errs)
    finally:
        edge.terminate()


asyncio.run(main())
T.log("\n== 收尾 ==")
T.restore_and_verify()
sys.exit(T.finish())
