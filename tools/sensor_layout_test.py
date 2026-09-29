"""離線 Edge 檢查監看小格:字級、溢出、更新前後尺寸,不連線或寫入開發板."""
import asyncio
import base64
import json
import pathlib
import re
import subprocess
import tempfile
import urllib.request

import websockets

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'test_logs'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'


async def main():
    OUT.mkdir(exist_ok=True)
    source = (ROOT / 'src/web_page.h').read_text(encoding='utf-8-sig')
    html = source.split('R"HTML(', 1)[1].rsplit(')HTML"', 1)[0]
    fit = source.split('function setAxisReadout(id,values){', 1)[1].split('function renderStatus(s){', 1)[0]
    # 使用正式 HTML/CSS 與縮字函式,移除 API 輪詢,以可重現資料覆蓋顯示值.
    html = re.sub(r'<script>.*?</script>', '', html, flags=re.S)
    html = html.replace('</body>', '<script>function setAxisReadout(id,values){' + fit + '</script></body>')
    fixture = OUT / 'sensor_layout_preview.html'
    fixture.write_text(html, encoding='utf-8')
    js_source = '\n'.join(re.findall(r'<script>(.*?)</script>', source, re.S))
    js_file = OUT / 'sensor_layout_syntax.js'
    js_file.write_text(js_source, encoding='utf-8')
    subprocess.run(['node', '--check', str(js_file)], check=True)
    with tempfile.TemporaryDirectory(prefix='sensor_edge_') as profile:
        process = subprocess.Popen([EDGE, '--headless=new', '--disable-gpu',
                                    '--remote-debugging-port=9347', f'--user-data-dir={profile}',
                                    'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(50):
                try:
                    pages = json.loads(urllib.request.urlopen('http://127.0.0.1:9347/json', timeout=1).read())
                    url = next(p['webSocketDebuggerUrl'] for p in pages if p['type'] == 'page')
                    break
                except Exception:
                    await asyncio.sleep(.2)
            async with websockets.connect(url, max_size=20000000) as ws:
                seq = 0

                async def call(method, **params):
                    nonlocal seq
                    seq += 1
                    await ws.send(json.dumps(dict(id=seq, method=method, params=params)))
                    while True:
                        message = json.loads(await ws.recv())
                        if message.get('id') == seq:
                            assert 'error' not in message, message
                            return message.get('result', {})

                async def js(expression):
                    result = await call('Runtime.evaluate', expression=expression, returnByValue=True, awaitPromise=True)
                    assert 'exceptionDetails' not in result, result
                    return result['result'].get('value')

                await call('Page.enable')
                await call('Page.navigate', url=fixture.as_uri())
                await asyncio.sleep(.7)
                normal = dict(acc='1.02 g', still='是(3.2 秒)', armSw='沒按下', esc='DShot 300',
                              timing='0.8 ms / 1 ms', gyro='0.1 / -0.2 / 0.3', bias='0.02 / -0.03 / 0.01',
                              impact='尚未發生', vib='0.03 g / 是')
                long = dict(normal, esc='DShot 1200 · 123456 RPM', timing='123.4 ms / 12345 ms',
                            gyro='-2000.0 / -1999.9 / -1888.8', bias='-123.45 / -123.45 / -123.45',
                            impact='12.34 g / 80 ms(123456 秒前)')
                snapshot = """[...document.querySelectorAll('.sensor-grid .v')].map(e=>({
                  id:e.id,size:parseFloat(getComputedStyle(e).fontSize),
                  overflow:e.scrollHeight>e.clientHeight||e.scrollWidth>e.clientWidth||[...e.children].some(c=>c.scrollWidth>c.clientWidth),
                  axes:[...e.children].map(c=>({text:c.textContent,x:c.offsetLeft,y:c.offsetTop})),
                  width:e.parentElement.offsetWidth,height:e.parentElement.offsetHeight
                }))"""
                results = []
                for width in (320, 375, 412, 860):
                    await call('Emulation.setDeviceMetricsOverride', width=width, height=1000, deviceScaleFactor=1, mobile=True)
                    baseline = None
                    for label, values in [('normal', normal), ('long', long), ('restored', normal)]:
                        await js('Object.entries(' + json.dumps(values) + ').forEach(([id,v])=>{if(id==="gyro"||id==="bias")setAxisReadout(id,v.split(" / ").map(Number));else document.getElementById(id).textContent=v});fitSensorValues()')
                        data = await js(snapshot)
                        assert all(not d['overflow'] for d in data), (width, label, data)
                        assert all(d['size'] == 17 for d in data if d['id'] in ('acc', 'armSw', 'vib')), data
                        geometry = [(d['width'], d['height']) for d in data]
                        if baseline is None:
                            baseline = geometry
                            base_sizes = [d['size'] for d in data]
                            base_axes = {d['id']:(d['size'],[(a['x'],a['y']) for a in d['axes']]) for d in data if d['axes']}
                        assert geometry == baseline, (width, label, geometry, baseline)
                        for d in data:
                            if d['axes']:
                                assert (d['size'],[(a['x'],a['y']) for a in d['axes']]) == base_axes[d['id']], (width,label,d)
                                assert all(len(a['text'])==8 and re.fullmatch(r' *-?\d+\.\d{2}',a['text']) for a in d['axes'])
                        if label == 'restored':
                            assert [d['size'] for d in data] == base_sizes
                        results.append(dict(width=width, case=label, values=data))
                    if width in (375, 860):
                        await js("document.querySelector('.sensor-grid').parentElement.scrollIntoView({block:'center'})")
                        shot = await call('Page.captureScreenshot', format='png')
                        (OUT / f'sensor_layout_{width}.png').write_bytes(base64.b64decode(shot['data']))
                (OUT / 'sensor_layout_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
                print('PASS: 4 widths x 3 data sets; no overflow, stable geometry, short values 17px; axes keep font/position, two decimals and sign slot.')
                await call('Browser.close')
        finally:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


asyncio.run(main())
