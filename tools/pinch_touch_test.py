# 版本流水號: r2 (2026-09-14) 雙指交給瀏覽器後不再檢查雙指捲頁(只記錄),加手勢說明框檢查
# 舊: r1 (2026-09-14) 曲線圖雙指:單指不捲頁,雙指移動網頁,雙指時不動曲線點,雙指縮放(放大後能縮回來),單指拖點仍可用
# 板上可能有 GG 未儲存的變更(GG:照測):開頭記下 RAM 值,結尾用 restore_unsaved 放回(不儲存). penv python.
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

import board_backup  # noqa: E402
import lp_test as T  # noqa: E402

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP_PORT = 9340
HERE = os.path.dirname(os.path.abspath(__file__))

T.init("pinch_touch_test")
st = T.status()
if T.fstate(st) not in ("arming", "standby", "done"):
    raise SystemExit("板子不在待機,不測")
ram = board_backup.backup(T.HOST)
ram_path = os.path.join(T.ROOT, "test_logs", time.strftime("pinch_touch_ram_%Y%m%d_%H%M%S.json"))
with open(ram_path, "w", encoding="utf-8") as f:
    json.dump(ram, f, ensure_ascii=False, indent=1)


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
                        return m.get("result", m.get("error", {}))

            async def js(expr):
                r = await call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
                return r.get("result", {}).get("value")

            async def touches(paths, steps=12):
                """paths: 每指 [(x0,y0),(x1,y1)]. 同時按下,一起移動,放開."""
                pts = lambda k: [{"x": p[0][0] + (p[1][0] - p[0][0]) * k / steps, "y": p[0][1] + (p[1][1] - p[0][1]) * k / steps, "id": i}
                                 for i, p in enumerate(paths)]
                # 多指時先放第一指再加第二指(真實手勢的順序)
                await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=pts(0)[:1])
                if len(paths) > 1:
                    await call("Input.dispatchTouchEvent", type="touchStart", touchPoints=pts(0))
                for k in range(1, steps + 1):
                    await call("Input.dispatchTouchEvent", type="touchMove", touchPoints=pts(k))
                    await asyncio.sleep(0.016)
                await call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
                await asyncio.sleep(0.8)

            await call("Runtime.enable")
            await call("Page.enable")
            await call("Emulation.setDeviceMetricsOverride", width=412, height=900, deviceScaleFactor=1, mobile=True)
            await call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
            await call("Page.navigate", url=f"http://{T.HOST}/#tab-prof")
            await asyncio.sleep(7)
            edit = await js("VALS.edit")
            await js("document.querySelector('nav button[data-pane=comp]').click()")
            await asyncio.sleep(2)
            await js("document.getElementById('cvSvg').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.6)
            ta = await js("getComputedStyle(document.getElementById('cvSvg')).touchAction")
            T.check(f"曲線圖 touch-action = {ta}(單指不捲頁,雙指可縮放)", ta == "pinch-zoom", ta)
            box = await js("(()=>{const r=document.getElementById('cvSvg').getBoundingClientRect();return [r.left,r.top,r.width,r.height]})()")
            cx, cy = box[0] + box[2] * 0.55, box[1] + box[3] * 0.5
            hit = await js(f"(()=>{{const a=document.elementFromPoint({cx},{cy}),b=document.elementFromPoint({cx+60},{cy});"
                           f"return [!!a.closest('#cvSvg')&&!a.closest('[data-h]'),!!b.closest('#cvSvg')&&!b.closest('[data-h]')]}})()")
            T.log("  兩指位置在圖內空白處:", hit)

            y0 = await js("window.scrollY")
            await touches([[(cx, cy), (cx, cy - 200)]])
            y1 = await js("window.scrollY")
            T.check(f"單指在圖內上滑:網頁不動(scrollY {y0} → {y1})", abs(y1 - y0) < 2, (y0, y1))

            # r2(web_page r42):雙指手勢完全交給瀏覽器(沒放大時捏合放大,放大後雙指拖動網頁),不再自己捲頁,這裡只記錄
            await touches([[(cx, cy), (cx, cy - 180)], [(cx + 60, cy), (cx + 60, cy - 180)]])
            y2 = await js("window.scrollY")
            T.log(f"  (記錄)未放大時雙指一起上滑:scrollY {y1} → {y2}(交給瀏覽器,手機實測為準)")
            g = await js("(()=>{const g=document.querySelector('.gesture'),s=document.getElementById('cvSvg');if(!g)return null;"
                         "const a=g.getBoundingClientRect(),b=s.getBoundingClientRect();return {txt:g.textContent,below:a.top>=b.bottom-1,"
                         "nextIsPanel:g.nextElementSibling&&g.nextElementSibling.id,same:g.parentNode.parentNode===s.parentNode.parentNode}})()")
            T.check("曲線圖旁有手勢說明框(手機寬度在圖下方,面板上面),寫明單指/雙指捏合/放大後雙指拖",
                    g and g["below"] and g["nextIsPanel"] == "curvePanel" and all(k in g["txt"] for k in ("單指", "雙指捏合", "放大後雙指拖")), g)
            ta_ok = await js("(()=>{const s=document.getElementById('cvSvg');return getComputedStyle(s).touchAction})()")
            T.check(f"曲線圖沒有攔截雙指(touch-action 仍為 {ta_ok})", ta_ok == "pinch-zoom", ta_ok)

            # 雙指時不動曲線點:第一指按在點上
            await js("document.getElementById('cvSvg').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.5)
            p0 = T.get(f"/api/settings?p={edit}")["profile"]
            pt = await js("(()=>{const e=document.querySelector('#cvSvg [data-h=pt][data-side=up][data-i=\"1\"]');const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
            await touches([[(pt[0], pt[1]), (pt[0] + 50, pt[1] + 40)], [(pt[0] - 80, pt[1] + 60), (pt[0] - 30, pt[1] + 100)]])
            await asyncio.sleep(2)
            p1 = T.get(f"/api/settings?p={edit}")["profile"]
            shown = await js("[VALS.profile[ck('up1a')],VALS.profile[ck('up1p')]]")
            T.check(f"一指按在點上加第二指一起移動:點不動,不送出(板上 {p0['up1a']}°/{p0['up1p']}% → {p1['up1a']}°/{p1['up1p']}%,畫面 {shown})",
                    p1["up1a"] == p0["up1a"] and p1["up1p"] == p0["up1p"] and shown == [p0["up1a"], p0["up1p"]], (p0["up1p"], p1["up1p"], shown))

            # 單指拖點仍可用
            await js("document.getElementById('cvSvg').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.5)
            pt = await js("(()=>{const e=document.querySelector('#cvSvg [data-h=pt][data-side=up][data-i=\"1\"]');const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
            direction = -40 if p0["up1p"] > 0 else 40
            sy = await js("window.scrollY")
            await touches([[(pt[0], pt[1]), (pt[0] + direction, pt[1])]])
            await asyncio.sleep(2.5)
            p2 = T.get(f"/api/settings?p={edit}")["profile"]
            sy2 = await js("window.scrollY")
            T.check(f"單指拖點仍可用:補償 {p0['up1p']} → {p2['up1p']},網頁沒捲動({sy} → {sy2})", p2["up1p"] != p0["up1p"] and abs(sy2 - sy) < 2,
                    (p0["up1p"], p2["up1p"], sy, sy2))

            # 雙指縮放(無頭瀏覽器可能不支援模擬捏合,先用圖外對照)
            async def pinch(x, y, scale):
                r = await call("Input.synthesizePinchGesture", x=int(x), y=int(y), scaleFactor=scale, gestureSourceType="touch")
                await asyncio.sleep(1.0)
                return r, await js("window.visualViewport.scale")

            await js("document.getElementById('cvSvg').scrollIntoView({block:'center'})")
            await asyncio.sleep(0.5)
            s0 = await js("window.visualViewport.scale")
            box = await js("(()=>{const r=document.getElementById('cvSvg').getBoundingClientRect();return [r.left,r.top,r.width,r.height]})()")
            below = await js("(()=>{const r=document.getElementById('cvSvg').getBoundingClientRect();return [innerWidth/2,Math.min(innerHeight-60,r.bottom+60)]})()")
            r_out, s_out = await pinch(below[0], below[1], 2.0)
            T.log(f"  (對照)圖外捏合放大:scale {s0} → {s_out},回應 {r_out}")
            if s_out and s_out > 1.2:
                await pinch(below[0], below[1], 0.5)
                s_back = await js("window.visualViewport.scale")
                r_in, s_in = await pinch(box[0] + box[2] / 2, box[1] + box[3] / 2, 2.0)
                T.check(f"圖內捏合放大:scale {s_back} → {s_in}", s_in > s_back * 1.3, (s_back, s_in))
                r_in2, s_in2 = await pinch(box[0] + box[2] / 2, box[1] + box[3] / 2, 0.5)
                T.check(f"放大後圖內捏合縮回:scale {s_in} → {s_in2}(不會被困在這頁)", s_in2 < s_in * 0.8, (s_in, s_in2))
            else:
                T.log("  !! 無頭瀏覽器的模擬捏合在圖外也沒有縮放效果,雙指縮放無法在這裡驗證,需要 GG 手機實測")
            T.check("頁面沒有 JS 錯誤", not errs, errs)
    finally:
        edge.terminate()


try:
    asyncio.run(main())
finally:
    T.log("\n== 收尾:放回測試前的 RAM 值(不儲存) ==")
    r = subprocess.run([sys.executable, os.path.join(HERE, "restore_unsaved.py"), ram_path, T.HOST], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    T.log(r.stdout.strip())
    T.check("設定與測試前 RAM 狀態相同(未儲存狀態保留)", r.returncode == 0, r.stdout[-200:])
sys.exit(T.finish())
