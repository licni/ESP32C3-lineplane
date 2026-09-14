# 版本流水號: r5 (2026-09-14) 參數按鈕改成 −/+ 兩顆,面板改點 + 走一格
# 舊: r4 (2026-09-13) 測試固定選用風格 A(網頁編輯飛行使用那組,GG 選的組可能只有 1 點),結束選回
# 舊: r3 (2026-09-13) 第二段只能拖基本油門把手
# 舊: r2 (2026-09-13) 開始前確認待機且無未儲存變更;加第二段獨立曲線與「由第一段複製曲線」測試
# 舊: r1 (2026-09-13) 角度補償曲線圖的拖曳操作測試(無頭 Edge + Chrome DevTools Protocol)
# ============================================================================
# 用真的滑鼠事件在曲線圖上拖曳點與把手,再從 API 讀回設定確認有寫進去. 測完放棄變更.
# 需要 websockets 套件(PlatformIO 的 penv 內建):
#   %USERPROFILE%\.platformio\penv\Scripts\python.exe tools/curve_ui_test.py [板子位址]
# ============================================================================
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

import board_backup

HOST = sys.argv[1] if len(sys.argv) > 1 else "lineplane.local"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9333
SHOT_DIR = tempfile.gettempdir()
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  OK  ", name)
    else:
        failed += 1
        print("  FAIL", name, detail)


def api(path, data=None):
    req = urllib.request.Request(f"http://{HOST}{path}", data=data)
    return json.loads(urllib.request.urlopen(req, timeout=8).read())


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

    async def center(self, selector):
        return await self.js(f"(()=>{{const r=document.querySelector({json.dumps(selector)}).getBoundingClientRect();"
                             f"return [r.left+r.width/2,r.top+r.height/2]}})()")

    async def drag(self, x, y, dx, dy, steps=8):
        await self.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
        for k in range(1, steps + 1):
            await self.call("Input.dispatchMouseEvent", type="mouseMoved", x=x + dx * k / steps, y=y + dy * k / steps,
                            button="left", buttons=1)
            await asyncio.sleep(0.03)
        await self.call("Input.dispatchMouseEvent", type="mouseReleased", x=x + dx, y=y + dy, button="left", clickCount=1)

    async def shot(self, name):
        r = await self.call("Page.captureScreenshot", format="png")
        path = os.path.join(SHOT_DIR, name)
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["data"]))
        return path


async def main():
    board_backup.require_idle(HOST)   # 板上有人在調(未儲存)或在飛就不測,也不放棄變更
    # r4:網頁的角度補償頁編輯的是「飛行使用」那一組. GG 選用的組可能只有 1 點,測試固定用風格 A(至少 2 點),結束選回原本那組
    old_active = api("/api/settings?p=0")["active"]
    api("/api/select", b"p=0")
    before = api("/api/settings?p=0")["profile"]
    if before["upN"] < 2:
        raise SystemExit("風格 A 朝上少於 2 點,這支測試需要至少 2 點")
    prof = tempfile.mkdtemp(prefix="lp_cdp_")
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", f"--remote-debugging-port={PORT}",
                             "--window-size=900,1100", f"http://{HOST}/#tab-comp"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(40):
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=2).read())
                pages = [t for t in tabs if t.get("type") == "page" and HOST in t.get("url", "")]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.5)
        if not ws_url:
            raise RuntimeError("CDP page not found")
        async with websockets.connect(ws_url, max_size=20_000_000) as ws:
            c = Cdp(ws)
            await c.call("Page.enable")
            await asyncio.sleep(6)   # 等頁面載入設定並畫出曲線
            n_pts = await c.js("document.querySelectorAll('#cvSvg [data-h=pt]').length")
            # 板上可能是 GG 調過的風格,點數不一定是出廠的 3+3,一律照實際點數測
            want = before["upN"] + before["dnN"]
            check(f"曲線圖畫出 {want} 個可調點(朝上 {before['upN']} + 朝下 {before['dnN']})", n_pts == want, n_pts)
            dn_last = before["dnN"]
            kdn_a, kdn_p = f"dn{dn_last}a", f"dn{dn_last}p"

            # 1. 拖曳朝上點 2:往右 40px(油門 +),往下 25px(角度 -)
            x, y = await c.center("#cvSvg [data-h=pt][data-side=up][data-i='2']")
            await c.drag(x, y, 40, 25)
            await asyncio.sleep(2.5)
            p = api("/api/settings?p=0")["profile"]
            check(f"拖曳點:朝上點 2 角度 {before['up2a']}→{p['up2a']},補償 {before['up2p']}→{p['up2p']}",
                  p["up2a"] < before["up2a"] and p["up2p"] > before["up2p"], (p["up2a"], p["up2p"]))
            title = await c.js("document.querySelector('#curvePanel h3').textContent")
            check(f"面板跟著選取:{title}", "朝上 點 2" in title, title)
            glow = await c.js("document.querySelectorAll('#cvSvg .cv-pt.sel').length")
            check("選中的點有亮紅光暈樣式(cv-pt sel)", glow == 1, glow)
            await c.shot("lp_curve_after_drag.png")

            # 2. 拖曳下限把手:往右 36px
            x, y = await c.center("#cvSvg [data-h=min]")
            await c.drag(x, y, 36, 0)
            await asyncio.sleep(2.5)
            p2 = api("/api/settings?p=0")["profile"]
            check(f"拖曳下限把手:{before['minPct']}→{p2['minPct']}", p2["minPct"] > before["minPct"], p2["minPct"])

            # 3. 拖曳死區上緣把手:往上 30px(角度 +)
            x, y = await c.center("#cvSvg [data-h=db][data-side=up]")
            await c.drag(x, y, 0, -30)
            await asyncio.sleep(2.5)
            p3 = api("/api/settings?p=0")["profile"]
            check(f"拖曳補速起點把手:{before['upDb']}→{p3['upDb']}(不會越過點 1 的 {p3['up1a']})",
                  p3["upDb"] > before["upDb"] and p3["upDb"] < p3["up1a"], (p3["upDb"], p3["up1a"]))

            # 4. 拖曳點越過鄰點:朝上點 1 往上拖很遠,角度應被夾在點 2 之下
            x, y = await c.center("#cvSvg [data-h=pt][data-side=up][data-i='1']")
            await c.drag(x, y, 0, -300)
            await asyncio.sleep(2.5)
            p4 = api("/api/settings?p=0")["profile"]
            check(f"點不能越過鄰點:點 1 角度 {p4['up1a']} < 點 2 角度 {p4['up2a']}", p4["up1a"] < p4["up2a"], (p4["up1a"], p4["up2a"]))

            # 5. 只點一下(不拖)朝下最後一點:只選取,數值不變
            x, y = await c.center(f"#cvSvg [data-h=pt][data-side=dn][data-i='{dn_last}']")
            await c.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
            await c.call("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
            await asyncio.sleep(1.5)
            p5 = api("/api/settings?p=0")["profile"]
            title = await c.js("document.querySelector('#curvePanel h3').textContent")
            check(f"點一下只選取不改值:{title}", f"朝下 點 {dn_last}" in title and p5[kdn_a] == p4[kdn_a] and p5[kdn_p] == p4[kdn_p], title)

            # 6. 面板 + 按鈕(按一下走一格)調整選取點的補償
            await c.js("[...document.querySelectorAll('#curvePanel .prm')][1].querySelector('.ctl .st[data-d=\"1\"]').click()")
            await asyncio.sleep(2.5)
            p6 = api("/api/settings?p=0")["profile"]
            check(f"面板 + 按鈕:朝下點 {dn_last} 補償 {p5[kdn_p]}→{p6[kdn_p]}", p6[kdn_p] == min(50, p5[kdn_p] + 1), p6[kdn_p])

            # 7. 切到第二段:基本油門標籤換成第二段
            await c.js("document.querySelector('#cvPhase button[data-ph=\"2\"]').click()")
            await asyncio.sleep(1)
            tag = await c.js("[...document.querySelectorAll('#cvSvg .cv-tagt')].map(t=>t.textContent).join('|')")
            check(f"切換第二段:{tag}", f"{p6['phase2Pct']}%" in tag, tag)
            dirty = api("/api/status")["dirty"]
            check("有變更時標記未儲存", dirty == 1, dirty)

            # 8. 第二段只顯示(兩段共用一條曲線):在第二段拖點會被擋下,數值不變
            await asyncio.sleep(0.5)
            x, y = await c.center("#cvSvg [data-h=pt][data-side=up][data-i='1']")
            await c.drag(x, y, -30, 0)
            await asyncio.sleep(2.0)
            p7 = api("/api/settings?p=0")["profile"]
            check("第二段拖點被擋下(曲線不變)", p7 == p6, "")
            n_handles = await c.js("document.querySelectorAll('#cvSvg [data-h=db],#cvSvg [data-h=min],#cvSvg [data-h=max]').length")
            n_base = await c.js("document.querySelectorAll('#cvSvg [data-h=base]').length")
            check("第二段只有基本油門把手(沒有死區/上下限把手)", n_handles == 0 and n_base == 1, (n_handles, n_base))
            check("沒有第二段曲線參數(p2 前綴)", not any(k.startswith("p2") for k in p7), [k for k in p7 if k.startswith("p2")][:3])

            # 8b. 第二段拖基本油門把手:往左 30px,改的是第二段基本油門(與風格頁同一個參數),曲線不變
            x, y = await c.center("#cvSvg [data-h=base]")
            await c.drag(x, y, -30, 0)
            await asyncio.sleep(2.5)
            p8 = api("/api/settings?p=0")["profile"]
            curve_same = all(p8[k] == p7[k] for k in p7 if k[:2] in ("up", "dn"))
            check(f"第二段拖基本油門:{p7['phase2Pct']}→{p8['phase2Pct']},第一段 {p8['phase1Pct']} 與曲線不變",
                  p8["phase2Pct"] < p7["phase2Pct"] and p8["phase1Pct"] == p7["phase1Pct"] and curve_same, "")
            v2 = await c.js("[...document.querySelectorAll('#curvePanel .prm .val')].map(e=>e.value||e.textContent).join('|')")
            check(f"面板的第二段基本油門跟著變:{v2}", str(p8["phase2Pct"]) in v2, v2)

            # 9. 撞牆檢查:列出兩段各自被上下限卡住的角度,與前端計算一致
            wall = await c.js("document.getElementById('cvWall')?.innerText||''")
            check("撞牆檢查區塊有第一段與第二段", "第一段" in wall and "第二段" in wall, wall[:80])
            print("  截圖:", await c.shot("lp_curve_final.png"))
    finally:
        edge.terminate()
        api("/api/revert", b"")
        p = api("/api/settings?p=0")["profile"]
        check("收尾放棄變更,回到原值", p == before, "")
        api("/api/select", f"p={old_active}".encode())
        check(f"選回原本飛行使用的第 {old_active + 1} 組", api("/api/settings?p=0")["active"] == old_active, "")
    print(f"\n通過 {passed},失敗 {failed}")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
