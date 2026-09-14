# 版本流水號: r1 (2026-09-13) 設定頁:觸地提早降落關閉時收起設定項目(無頭 Edge 讀 DOM). 只改 RAM,結束放棄變更.
# 用法: penv python tools/earlyland_hide_check.py [板子位址]
import asyncio
import json
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

import websockets

import board_backup

HOST = sys.argv[1] if len(sys.argv) > 1 else "lineplane.local"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9335
ok_all = True


def post(path, **d):
    req = urllib.request.Request(f"http://{HOST}{path}", data=urllib.parse.urlencode(d).encode())
    return json.loads(urllib.request.urlopen(req, timeout=8).read())


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print("  OK  " if cond else "  FAIL", name, "" if cond else detail)


JS = """(()=>{const card=document.getElementById('earlyCard');
 const rows=[...card.querySelectorAll('.prm')].map(e=>({t:e.textContent.slice(0,12),h:e.hidden||e.offsetParent===null}));
 return {rows, live:document.getElementById('elLive').hidden, h:card.getBoundingClientRect().height}})()"""


async def main():
    board_backup.require_idle(HOST)
    before = board_backup.backup(HOST)
    prof = tempfile.mkdtemp(prefix="lp_cdp_")
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", f"--remote-debugging-port={PORT}",
                             "--window-size=412,1400", f"http://{HOST}/#tab-set"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        async with websockets.connect(ws_url, max_size=20_000_000) as ws:
            n = 0

            async def js(expr):
                nonlocal n
                n += 1
                await ws.send(json.dumps({"id": n, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get("id") == n:
                        return m["result"]["result"].get("value")

            await asyncio.sleep(6)
            for v, name in ((0, "關閉"), (1, "開啟")):
                r = post("/api/set", p="s", k="earlyLand", v=v)
                await js("loadVals()")
                await asyncio.sleep(2)
                d = await js(JS)
                print(f"  [{name}] 卡片高 {d['h']:.0f}px,項目:", [(x['t'], 'hidden' if x['h'] else 'show') for x in d["rows"]], "即時列 hidden" if d["live"] else "即時列 show")
                shown = [x for x in d["rows"] if not x["h"]]
                if v == 0:
                    check("關閉:只剩開關一列,四個設定與即時抖動列收起", r["ok"] and len(shown) == 1 and d["live"], d)
                else:
                    check("開啟:開關 + 四個設定與即時抖動列都出現", r["ok"] and len(shown) == 5 and not d["live"], d)
    finally:
        edge.terminate()
        post("/api/revert")
        d = board_backup.diff(before, board_backup.backup(HOST))
        check("放棄變更後設定與測試前相同", not d, d)


asyncio.run(main())
sys.exit(0 if ok_all else 1)
