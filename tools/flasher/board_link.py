# 版本流水號: r1 (2026-11-02) 初版:電腦端 USB 設定通道(GG:插線用同一份網頁設定飛控)
# ============================================================================
# 三件事,都不碰視窗:
#  - SerialBridge:透過 USB 序列埠向板子送「網頁請求」(韌體 web_server.cpp r33 的 @Q/@A 協定),板子用同一組處理函式回應.
#    一次一筆(鎖),其他序列輸出(板子的訊息)照常交給 on_line. 協定:
#      送:@Q <編號> <GET|POST> <F|T> <路徑?查詢>\t<本文百分比編碼>\n   F = 表單編碼(板子解成參數),T = 其他(本文放 plain)
#      收:@A <編號> <狀態碼> <本文長度> <內容類型>\n<本文>\n            本文可為二進位(飛行紀錄)
#  - HttpBoard:同樣的介面,走 WiFi(http://lineplane.local 或 IP). 備份匯出/匯入兩種連線都能用.
#  - LocalProxy:電腦上的小網頁伺服器(127.0.0.1 隨機埠),瀏覽器開它就看到板子那一份網頁;
#    首頁從板子抓(依韌體版本快取在硬碟),其他請求全部轉給 SerialBridge. 網頁看到網址是 127.0.0.1 就知道是 USB 模式.
# ============================================================================
import http.server
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

RESP_RE = re.compile(rb"^@A (\S+) (\d{3}) (\d+) (.+?)\s*$")   # 內容類型可含空格(text/html; charset=utf-8)


class BoardError(Exception):
    pass


class SerialBridge:
    """掛在已開啟的序列埠讀取執行緒上. feed() 吃進所有收到的位元組,把 @A 回應配給等待中的 request(),其他整行交給 on_line."""

    def __init__(self, write, on_line):
        self._write = write          # function(bytes) -> bool
        self.on_line = on_line       # function(str)
        self._buf = b""
        self._pending = None         # (編號, 本文長度, 狀態碼, 類型)
        self._waiting = {}           # 編號 → [Event, result]
        self._lock = threading.Lock()   # 一次一筆
        self._seq = 0

    def feed(self, data):
        self._buf += data
        while True:
            if self._pending:
                rid, n, status, ctype = self._pending
                if len(self._buf) < n + 1:
                    return
                body, rest = self._buf[:n], self._buf[n:]
                self._buf = rest[1:] if rest[:1] == b"\n" else rest   # 本文後面固定一個換行
                self._pending = None
                w = self._waiting.get(rid)
                if w:
                    w[1] = (status, ctype, body)
                    w[0].set()
                continue
            i = self._buf.find(b"\n")
            if i < 0:
                if len(self._buf) > 8192:   # 沒有換行的雜訊
                    self.on_line(self._buf.decode("utf-8", "replace"))
                    self._buf = b""
                return
            line, self._buf = self._buf[:i], self._buf[i + 1:]
            m = RESP_RE.match(line)
            if m:
                self._pending = (m.group(1).decode(), int(m.group(3)), int(m.group(2)), m.group(4).decode("ascii", "replace"))
                continue
            text = line.decode("utf-8", "replace").rstrip("\r")
            if text.strip():
                self.on_line(text)

    def reset(self):
        """序列埠重開(板子重開機,拔插):清掉讀到一半的東西,等待中的請求當失敗."""
        self._buf = b""
        self._pending = None
        for w in list(self._waiting.values()):
            w[1] = None
            w[0].set()

    def request(self, method, path, body=b"", form=False, timeout=5.0):
        """回 (狀態碼, 內容類型, 本文 bytes). 連不上或逾時丟 BoardError."""
        if isinstance(body, str):
            body = body.encode("utf-8")
        with self._lock:
            self._seq = self._seq % 100000 + 1
            rid = str(self._seq)
            line = f"@Q {rid} {method.upper()} {'F' if form else 'T'} {path}\t{urllib.parse.quote(body, safe='')}\n".encode("utf-8")
            ev = threading.Event()
            self._waiting[rid] = [ev, None]
            try:
                if not self._write(line):
                    raise BoardError("序列埠沒有連線,送不出去")
                if not ev.wait(timeout):
                    raise BoardError(f"板子沒有回應({method} {path},{timeout:.0f} 秒)")
                res = self._waiting[rid][1]
                if res is None:
                    raise BoardError("序列埠中斷")
                return res
            finally:
                self._waiting.pop(rid, None)

    def get(self, path, timeout=5.0):
        return self.request("GET", path, timeout=timeout)

    def post(self, path, data=None, timeout=5.0):
        return self.request("POST", path, urllib.parse.urlencode(data or {}), form=True, timeout=timeout)


class HttpBoard:
    """走 WiFi:和 SerialBridge 同樣的 request()/get()/post()."""

    def __init__(self, host):
        host = host.strip().rstrip("/")
        if "://" not in host:
            host = "http://" + host
        self.base = host

    def request(self, method, path, body=b"", form=False, timeout=5.0):
        if isinstance(body, str):
            body = body.encode("utf-8")
        req = urllib.request.Request(self.base + path, data=body if method.upper() == "POST" else None, method=method.upper())
        if method.upper() == "POST":
            req.add_header("Content-Type", "application/x-www-form-urlencoded" if form else "text/plain")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type", ""), e.read()
        except (urllib.error.URLError, OSError) as e:
            raise BoardError(f"連不上 {self.base}:{getattr(e, 'reason', e)}") from e

    def get(self, path, timeout=5.0):
        return self.request("GET", path, timeout=timeout)

    def post(self, path, data=None, timeout=5.0):
        return self.request("POST", path, urllib.parse.urlencode(data or {}), form=True, timeout=timeout)


class LocalProxy:
    """本機網頁伺服器:GET / 回板子的網頁(快取),其他轉給 bridge. start() 回網址."""

    def __init__(self, bridge, cache_dir, log=None):
        self.bridge = bridge
        self.cache_dir = cache_dir
        self.log = log or (lambda m: None)
        self.server = None
        self.page_key = None
        self.requests = 0

    def start(self):
        if self.server:
            return self.url
        proxy = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):
                pass

            def _reply(self, status, ctype, body, cache=False):
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache" if cache else "no-store")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path.split("?")[0] == "/":
                    try:
                        self._reply(200, "text/html; charset=utf-8", proxy.page(), cache=True)
                    except BoardError as e:
                        self._reply(503, "text/html; charset=utf-8", proxy.error_page(str(e)))
                    return
                if self.path == "/favicon.ico":
                    self._reply(404, "text/plain", b"")
                    return
                self._forward("GET", b"", False)

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n) if n else b""
                form = "application/x-www-form-urlencoded" in (self.headers.get("Content-Type") or "")
                self._forward("POST", body, form)

            def _forward(self, method, body, form):
                proxy.requests += 1
                try:
                    status, ctype, data = proxy.bridge.request(method, self.path, body, form=form, timeout=6.0)
                    self._reply(status, ctype or "application/octet-stream", data)
                except BoardError as e:
                    self._reply(503, "application/json", ('{"ok":false,"code":"usblost","msg":"%s"}' % str(e).replace('"', "'")).encode("utf-8"))

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self.url

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def page(self):
        """板子的網頁,依韌體版本/板子/編譯時間快取(同一版韌體只透過 USB 抓一次,約 230KB)."""
        st, _, data = self.bridge.get("/api/fw", timeout=4)
        if st != 200:
            raise BoardError("讀不到韌體版本")
        import json
        fw = json.loads(data.decode("utf-8"))
        key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{fw.get('ver')}-{fw.get('board')}-{fw.get('build')}")
        path = os.path.join(self.cache_dir, key + ".html")
        if key != self.page_key or not os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    html = f.read()
            except OSError:
                self.log(f"從板子讀取網頁(韌體 {fw.get('ver')})…")
                st, _, html = self.bridge.get("/", timeout=20)
                if st != 200 or b"<html" not in html[:200].lower() and b"<!doctype" not in html[:200].lower():
                    raise BoardError("板子回的不是網頁")
                os.makedirs(self.cache_dir, exist_ok=True)
                with open(path, "wb") as f:
                    f.write(html)
                self.log(f"網頁已存快取({len(html):,} 位元組)")
            self.page_key = key
            self._html = html
        return self._html

    @staticmethod
    def error_page(msg):
        return ("<!doctype html><meta charset=utf-8><title>線控飛機設定器</title><body style='font-family:sans-serif;padding:2em'>"
                "<h2>連不到板子</h2><p>%s</p><p>請確認 USB 線接著,設定器還開著,然後重新整理這一頁.</p></body>" % msg).encode("utf-8")


def probe(board, timeout=2.0):
    """板子有沒有網頁 API(USB 需要韌體 2026.11.02.1 以上). 回 /api/fw 的 dict,沒有回 None."""
    import json
    try:
        st, _, data = board.get("/api/fw", timeout=timeout)
    except BoardError:
        return None
    if st != 200:
        return None
    try:
        return json.loads(data.decode("utf-8"))
    except ValueError:
        return None


BACKUP_ALL_PROFILES = 63   # 六組風格
BACKUP_SEC_ALL = 15        # 起飛降落與安全 + 安裝 + 電變 + WiFi


def backup_export(board, log=None, ask_save=None):
    """讀板上全部設定的備份碼. 有未儲存變更時呼叫 ask_save() 決定要不要先儲存(True = 儲存後繼續). 回 (備份碼, /api/fw dict)."""
    fw = probe(board) or {}
    for attempt in range(2):
        st, _, data = board.get(f"/api/backup?sel={BACKUP_ALL_PROFILES}&sec={BACKUP_SEC_ALL}", timeout=8)
        r = _json(data, "備份")
        if r.get("ok") and r.get("text"):
            return r["text"], fw
        if r.get("code") == "bkdirty" and attempt == 0:
            if not (ask_save and ask_save()):
                raise BoardError("板上有未儲存的變更,沒有備份")
            st, _, data = board.post("/api/save")
            rr = _json(data, "儲存")
            if not rr.get("ok"):
                raise BoardError("儲存失敗:" + str(rr.get("code")))
            if log:
                log("已儲存板上的變更")
            continue
        raise BoardError("板子拒絕備份:" + str(r.get("code")))
    raise BoardError("備份失敗")


def _json(data, what):
    import json
    try:
        return json.loads(data.decode("utf-8"))
    except ValueError:
        raise BoardError(f"板子對 {what} 的回應不是 JSON:{data[:60]!r}(韌體太舊?)")


def backup_check(board, code):
    """檢查備份碼. 回板子的 JSON(ok,code,gen,mask,sec,names,newer,…)."""
    _, _, data = board.post("/api/backup/check", {"text": code}, timeout=8)
    return _json(data, "備份檢查")


def backup_apply(board, code):
    """套用並儲存. 回 (套用結果 JSON, 儲存結果 JSON)."""
    _, _, data = board.post("/api/backup/apply", {"text": code}, timeout=8)
    r = _json(data, "備份套用")
    if not r.get("ok"):
        raise BoardError("套用失敗:" + str(r.get("code")))
    _, _, data = board.post("/api/save", timeout=8)
    rs = _json(data, "儲存")
    if not rs.get("ok"):
        raise BoardError("套用成功但儲存失敗:" + str(rs.get("code")))
    return r, rs


def backup_file_text(code, fw, source):
    """備份檔內容:註解行 + 備份碼(匯入時取最後一個非 # 開頭的行)."""
    return ("# 線控飛機油門控制器 設定備份(全部 6 組飛行風格 + 起飛降落與安全/安裝/電變/WiFi)\n"
            f"# 時間 {time.strftime('%Y-%m-%d %H:%M:%S')}  韌體 {fw.get('ver', '?')} {fw.get('board', '')}  來源 {source}\n"
            "# 還原:設定器「設定與備份」頁的「匯入備份到板子」,或把下面這串貼到板子網頁「備份」頁套用.\n"
            f"{code}\n")


def backup_file_code(text):
    lines = [x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith("#")]
    if not lines:
        raise BoardError("檔案裡沒有備份碼")
    return lines[-1]
