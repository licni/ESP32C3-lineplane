# 版本流水號: r1 (2026-09-14) 參數 +/− 按鈕:按一下走一格,快速連點不少格,按住連續加速且放開才送出,按下後滑動不算,到上下限停住
# penv python. 會改設定(只改 RAM):確認待機且無未儲存 → 備份 → 測試 → 放棄變更並還原比對.
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
CDP_PORT = 9341

T.init("step_button_test")
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

            await call("Runtime.enable")
            await call("Emulation.setDeviceMetricsOverride", width=412, height=900, deviceScaleFactor=1, mobile=True)
            await call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
            await call("Page.navigate", url=f"http://{T.HOST}/#tab-prof")
            await asyncio.sleep(7)
            edit = await js("VALS.edit")

            def prof():
                return T.get(f"/api/settings?p={edit}")["profile"]

            async def btn(key, d):
                """把參數捲到畫面中間,回傳 +/− 按鈕中心座標"""
                return await js(f"(()=>{{const w=WIDGETS.find(w=>w.key==='{key}'&&w.el.isConnected);w.el.scrollIntoView({{block:'center'}});"
                                f"const b=w.el.querySelector('.st[data-d=\"{d}\"]');const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}})()")

            async def shown(key):
                return await js(f"Number(WIDGETS.find(w=>w.key==='{key}'&&w.el.isConnected).inp.value)")

            async def press(x, y, hold_s):
                await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
                await asyncio.sleep(hold_s)
                await call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])

            info = await js("(()=>{const w=WIDGETS.find(w=>w.key==='phase1Pct');return {n:w.el.querySelectorAll('.ctl button').length,"
                            "t:[...w.el.querySelectorAll('.ctl button')].map(b=>b.textContent),ta:getComputedStyle(w.el.querySelector('.st')).touchAction}})()")
            T.check(f"每個參數只剩兩顆按鈕 − / +,連點不觸發雙擊放大({info})", info["n"] == 2 and info["t"] == ["−", "+"] and info["ta"] == "manipulation", info)

            # 1. 按一下 + 走一格
            p0 = prof()
            x, y = await btn("phase1Pct", 1)
            await asyncio.sleep(0.5)
            await press(x, y, 0.08)
            await asyncio.sleep(1.5)
            p1 = prof()
            T.check(f"按一下 +:第一段油門 {p0['phase1Pct']} → {p1['phase1Pct']}(+1)", p1["phase1Pct"] == min(100, p0["phase1Pct"] + 1), p1["phase1Pct"])

            # 2. 快速連點 4 下 −(板子還沒回應就按下一下),不能少格,畫面不能放大
            for _ in range(4):
                bx, by = await js("(()=>{const w=WIDGETS.find(w=>w.key==='phase1Pct');const r=w.el.querySelector('.st[data-d=\"-1\"]').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
                await press(bx, by, 0.05)
                await asyncio.sleep(0.07)
            await asyncio.sleep(2.5)
            p2 = prof()
            scale = await js("visualViewport.scale")
            T.check(f"快速連點 4 下 −:{p1['phase1Pct']} → {p2['phase1Pct']}(−4),畫面縮放 {scale}", p2["phase1Pct"] == max(0, p1["phase1Pct"] - 4) and scale == 1, (p2["phase1Pct"], scale))
            T.check("連點後框內顯示與板上一致", await shown("phase1Pct") == p2["phase1Pct"], await shown("phase1Pct"))

            # 3. 按住 + 3.5 秒(總飛行時間,細調 5 粗調 30):框內一直加,板子邊按邊跟上,放開送最後的值;約 2 秒後改粗調
            x, y = await btn("flightSec", 1)
            await asyncio.sleep(0.5)
            f0 = prof()["flightSec"]
            await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
            await asyncio.sleep(1.5)
            mid_shown = await shown("flightSec")
            mid_board = prof()["flightSec"]
            mid_on = await js("WIDGETS.find(w=>w.key==='flightSec').el.querySelector('.st[data-d=\"1\"]').classList.contains('on')")
            await asyncio.sleep(2.0)
            await call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
            end_shown = await shown("flightSec")
            T.check(f"按住中:框內一直加({f0} → {mid_shown}),板子邊按邊跟上({mid_board}),按鈕變色", mid_shown > f0 and f0 < mid_board <= mid_shown and mid_on, (mid_shown, mid_board, mid_on))
            await asyncio.sleep(2)
            f1 = prof()["flightSec"]
            T.check(f"放開後板上 = 框內最後顯示:{f0} → {f1}(顯示 {end_shown}),5 的倍數", f1 == end_shown and f1 % 5 == 0, (f1, end_shown))
            T.check(f"按住 3.5 秒加了 {f1 - f0} 秒(有進入粗調 30,應大於 150)", f1 - f0 > 150 or f1 == 1800, f1 - f0)

            # 3b. 按住 + 加第一段時間,會超過總飛行時間(板子拒絕):停在最後被接受的值,顯示原因,不退回起點
            x, y = await btn("phase1Sec", 1)
            await asyncio.sleep(0.5)
            pp = prof()
            s0, fl = pp["phase1Sec"], pp["flightSec"]
            await js("window._toasts=[];const _t0=toast;toast=function(a,b){window._toasts.push(a);return _t0(a,b)}")
            await press(x, y, 6.0)
            end_shown = await shown("phase1Sec")
            await asyncio.sleep(2)
            toasts = await js("window._toasts")
            s1 = prof()["phase1Sec"]
            T.check(f"加到超過總飛行時間 {fl}:停在 {s1}(起點 {s0}),框內 {end_shown},提示 {toasts}", s0 < s1 < fl and end_shown == s1 and len(toasts) == 1, (s1, end_shown, toasts))

            # 4. 按下後手指滑動(捲頁):不算按
            s2 = prof()["phase1Sec"]
            x, y = await btn("phase1Sec", -1)
            await asyncio.sleep(0.5)
            await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
            for k in range(1, 9):
                await call("Input.dispatchTouchEvent", type="touchMove", touchPoints=[{"x": x, "y": y - 10 * k}])
                await asyncio.sleep(0.016)
            await call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
            await asyncio.sleep(2)
            s3 = prof()["phase1Sec"]
            T.check(f"按在 − 上滑動捲頁:值不變({s2} → {s3})", s3 == s2, s3)

            # 5. 按住 − 直到下限(第一段時間 10 秒):停在下限,放開後顯示與板上一致
            x, y = await btn("phase1Sec", -1)
            await asyncio.sleep(0.5)
            await press(x, y, 5.5)
            await asyncio.sleep(2)
            s4 = prof()["phase1Sec"]
            sh = await shown("phase1Sec")
            T.check(f"按住 − 到底:板上 {s4},框內 {sh}(下限 10 或被交叉驗證擋下時顯示回板上值)", sh == s4 and s4 < s3, (s4, sh))

            # 6. 鍵盤/程式 click():走一格
            await js("WIDGETS.find(w=>w.key==='phase1Pct').el.querySelector('.st[data-d=\"1\"]').click()")
            await asyncio.sleep(1.5)
            p3 = prof()
            T.check(f"程式 click() +:{p2['phase1Pct']} → {p3['phase1Pct']}(+1)", p3["phase1Pct"] == min(100, p2["phase1Pct"] + 1), p3["phase1Pct"])

            T.post("/api/revert")
            await asyncio.sleep(1)
            T.check("頁面沒有 JS 錯誤", not errs, errs)
    finally:
        edge.terminate()


asyncio.run(main())
T.post("/api/revert")
T.restore_and_verify()
sys.exit(T.finish())
