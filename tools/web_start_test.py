# 版本流水號: r1 (2026-09-14) 網頁「開始起飛程序」按鈕:API 規則(與手勢同一套檢查)+ 無頭 Edge 真點擊(按兩下才開始)
# 需要 penv 的 python(websockets). 會改設定:確認待機且無未儲存 → 備份 → 測試 → 還原比對.
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
CDP_PORT = 9337

T.init("web_start_test")
T.protect()
T.ser_open()
T.cmd("sim off", expect="sim")


def of(evs, ty, arg=None):
    return [e for e in evs if e[2] == ty and (arg is None or e[3] == arg)]


def level():
    T.sim("gyro 0 0 0")
    T.sim("vib 0")
    T.sim("att 0 0 1.0")


T.configure(shared={"disturbMode": 2, "countdownSec": 5})
level()
time.sleep(1.8)

# ---- API ----
T.log("\n== API ==")
n0 = T.ev_total()
r = T.post("/api/start")
st = T.wait_state("wait_still", 2)
g = of(T.events_after(n0), 3)
T.check("按開始:進入等待放穩,事件記「網頁按開始」(來源 2)", r["ok"] and T.fstate(st) == "wait_still" and g and g[0][3] == 2, (r, T.fstate(st), g))
st = T.wait_state("countdown", 3)
T.check("放穩後照常倒數", T.fstate(st) == "countdown", T.fstate(st))
r = T.post("/api/start")
T.check("倒數中再按開始:拒絕(startstate)", not r["ok"] and r["code"] == "startstate", r)
st = T.wait_state("takeoff", 7, poll=0.05)
T.check("倒數完馬達啟動", T.fstate(st) == "takeoff", T.fstate(st))
r = T.post("/api/start")
T.check("馬達運轉中按開始:拒絕", not r["ok"] and r["code"] == "startstate", r)
T.post("/api/estop")
T.wait_state("done", 2)
time.sleep(1.7)
r = T.post("/api/start")
st = T.wait_state("wait_still", 2)
T.check("飛行結束後可以再按開始", r["ok"] and T.fstate(st) == "wait_still", T.fstate(st))
T.post("/api/cancel")
time.sleep(1.7)

T.setp(T.TEST_SLOT, "phase2Pct", 81)
T.post("/api/start")
time.sleep(0.5)
st = T.status()
T.check("有未儲存變更:狀態機拒絕(rj=1),停在待機", T.fstate(st) == "standby" and st["f"]["rj"] == 1, st["f"])
T.post("/api/revert")
time.sleep(1.7)

T.sim("att 45 0 1.0")
time.sleep(0.3)
T.post("/api/start")
time.sleep(0.5)
st = T.status()
T.check("機頭 45°(超過水平限制):拒絕(rj=3)", T.fstate(st) == "standby" and st["f"]["rj"] == 3, st["f"])
level()
time.sleep(1.7)

T.post("/api/start")
T.wait_state("wait_still", 2)
T.sim("gyro 0 0 90")
T.wait_state("standby", 1.5)
T.sim("gyro 0 0 0")
r = T.post("/api/start")
T.check(f"網頁開始的起飛程序也能扭轉機尾取消,封鎖期內按開始:拒絕(startblock)", not r["ok"] and r["code"] == "startblock"
        and T.status()["f"]["er"] == 8, (r, T.status()["f"]["er"]))
time.sleep(5.5)

T.sim("fail 1")
time.sleep(0.4)
T.post("/api/start")
time.sleep(0.5)
st = T.status()
T.check("感測器故障:拒絕(rj=2)", T.fstate(st) == "standby" and st["f"]["rj"] == 2, st["f"])
T.reboot()
level()
time.sleep(1.0)

T.configure(shared={"disturbMode": 2, "countdownSec": 5, "gestureEnable": 0})
r = T.post("/api/start")
T.check("上電後直接倒數模式:拒絕(startauto)", not r["ok"] and r["code"] == "startauto", r)
T.configure(shared={"disturbMode": 2, "countdownSec": 5})
level()
time.sleep(1.8)


# ---- 網頁真點擊 ----
async def ui():
    prof = tempfile.mkdtemp(prefix="lp_cdp_")
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", f"--remote-debugging-port={CDP_PORT}",
                             "--window-size=412,900", f"http://{T.HOST}/#tab-mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
                r = await call("Runtime.evaluate", expression=expr, returnByValue=True)
                return r.get("result", {}).get("value")

            async def click(sel):
                xy = await js(f"(()=>{{const e=document.querySelector('{sel}');if(!e||e.hidden)return null;"
                              f"const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}})()")
                if not xy:
                    return False
                for t in ("mousePressed", "mouseReleased"):
                    await call("Input.dispatchMouseEvent", type=t, x=xy[0], y=xy[1], button="left", clickCount=1)
                return True

            await call("Runtime.enable")
            await asyncio.sleep(6)
            vis = await js("!document.getElementById('btnStart').hidden")
            T.check("待機時狀態列出現「開始起飛程序」鈕", vis)
            await click("#btnStart")
            await asyncio.sleep(0.4)
            label = await js("document.getElementById('btnStart').textContent")
            T.check(f"按一下:不開始,按鈕變「{label}」", T.fstate() == "standby" and "再按一下" in label, label)
            await asyncio.sleep(3.2)
            label = await js("document.getElementById('btnStart').textContent")
            T.check(f"3 秒沒按第二下:恢復「{label}」,仍在待機", T.fstate() == "standby" and label == "開始起飛程序", label)
            await click("#btnStart")
            await asyncio.sleep(0.3)
            await click("#btnStart")
            # r1 第一次跑:板子放穩只要 1 秒,輪詢到時已進入倒數 → 兩個狀態都算已開始
            st = T.wait_state(("wait_still", "countdown"), 2)
            T.check(f"連按兩下:開始起飛程序({T.fstate(st)})", T.fstate(st) in ("wait_still", "countdown"), T.fstate(st))
            await asyncio.sleep(1.0)
            hidden = await js("document.getElementById('btnStart').hidden")
            cancel = await js("!document.getElementById('btnCancel').hidden")
            T.check("起飛程序中開始鈕隱藏,出現取消倒數鈕", hidden and cancel, (hidden, cancel))
            await click("#btnCancel")
            T.wait_state("standby", 2)
            await call("Page.captureScreenshot", format="png")
            T.check("頁面沒有 JS 錯誤", not errs, errs)
    finally:
        edge.terminate()


T.log("\n== 網頁真點擊 ==")
asyncio.run(ui())
T.log("\n== 收尾 ==")
T.restore_and_verify()
sys.exit(T.finish())
