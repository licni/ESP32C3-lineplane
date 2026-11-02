# 版本流水號: r1 (2026-11-02) 初版:USB 設定通道的電腦端測試(假板子照 web_server.cpp r33 的協定回應,不需要板子與序列埠)
import json
import threading
import unittest
import urllib.parse
import urllib.request

import board_link as bl

PAGE = b"<!doctype html><html><head><meta charset=utf-8><title>t</title></head><body>fake page</body></html>"


class FakeBoard:
    """照韌體 Req::serialRequest 的規則解 @Q,回 @A. 另外夾雜一般訊息行,模擬板子同時印東西."""

    def __init__(self):
        self.out = b""
        self.seen = []
        self.dirty = True
        self.saved = False
        self.applied = None

    def feed_line(self, line):
        assert line.startswith(b"@Q ") and line.endswith(b"\n")
        head, _, enc = line[:-1].partition(b"\t")
        parts = head.decode().split(" ", 4)
        _, rid, method, kind, target = parts
        body = urllib.parse.unquote(enc.decode())
        path, _, query = target.partition("?")
        args = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
        if kind == "F":
            args.update(urllib.parse.parse_qsl(body, keep_blank_values=True))
        if body:
            args["plain"] = body
        self.seen.append((method, path, dict(args)))
        self.out += b"log line from board\n"   # 板子的訊息混在中間
        st, ctype, data = self.handle(method, path, args)
        self.out += f"@A {rid} {st} {len(data)} {ctype}\n".encode() + data + b"\n"

    def handle(self, method, path, a):
        if (method, path) == ("GET", "/"):
            return 200, "text/html; charset=utf-8", PAGE
        if (method, path) == ("GET", "/api/fw"):
            return 200, "application/json", b'{"ver":"2026.11.02.2","board":"MINI","build":"Nov  2 2026 10:00:00","pending":0}'
        if (method, path) == ("GET", "/api/log"):
            return 200, "application/octet-stream", bytes(range(256)) * 3 + b"\n@A 9 200 1 x\n"   # 二進位,含會混淆的內容
        if (method, path) == ("POST", "/api/setmany"):
            return 200, "application/json", json.dumps({"ok": True, "p": a.get("p"), "plain": a.get("plain")}).encode()
        if (method, path) == ("GET", "/api/backup"):
            if self.dirty:
                return 400, "application/json", b'{"ok":false,"code":"bkdirty"}'
            return 200, "application/json", json.dumps({"ok": True, "code": "bkmade", "text": "LP1:ABCDEF", "sel": a.get("sel"), "sec": a.get("sec")}).encode()
        if (method, path) == ("POST", "/api/save"):
            self.dirty = False
            self.saved = True
            return 200, "application/json", b'{"ok":true,"code":"saved"}'
        if (method, path) == ("POST", "/api/backup/check"):
            ok = a.get("text", "").startswith("LP1:")
            return (200 if ok else 400), "application/json", json.dumps({"ok": ok, "code": "bkok" if ok else "bkcrc", "gen": 7, "mask": 63, "sec": 15, "names": ["a", "b"], "newer": 0}).encode()
        if (method, path) == ("POST", "/api/backup/apply"):
            self.applied = a.get("text")
            return 200, "application/json", b'{"ok":true,"code":"bkapplied","gen":7,"names":["a"]}'
        if path == "/update":
            return 400, "application/json", b'{"ok":false,"code":"usbnoupload"}'
        return 404, "text/plain", b"Not found"


class Link:
    """SerialBridge ↔ FakeBoard 直接接線(write 進假板子,假板子的輸出餵回 feed)."""

    def __init__(self):
        self.board = FakeBoard()
        self.lines = []
        self.bridge = bl.SerialBridge(self.write, self.lines.append)

    def write(self, data):
        self.board.feed_line(data)
        out, self.board.out = self.board.out, b""
        # 分成小塊餵,模擬序列埠零碎到達
        threading.Thread(target=lambda: [self.bridge.feed(out[i:i + 7]) for i in range(0, len(out), 7)], daemon=True).start()
        return True


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.link = Link()
        self.b = self.link.bridge

    def test_get_json_and_log_lines(self):
        st, ct, data = self.b.get("/api/fw")
        self.assertEqual((st, ct), (200, "application/json"))
        self.assertEqual(json.loads(data)["ver"], "2026.11.02.2")
        self.assertEqual(self.link.lines, ["log line from board"])

    def test_binary_body(self):
        st, ct, data = self.b.get("/api/log?since=5")
        self.assertEqual(st, 200)
        self.assertEqual(data, bytes(range(256)) * 3 + b"\n@A 9 200 1 x\n")
        self.assertEqual(self.link.board.seen[-1][2], {"since": "5"})

    def test_text_body_with_newlines(self):
        body = "a=1\nb=中文\nc=x&y=2"
        st, _, data = self.b.request("POST", "/api/setmany?p=3", body)
        r = json.loads(data)
        self.assertEqual((r["p"], r["plain"]), ("3", body))

    def test_form_post(self):
        st, _, data = self.b.post("/api/backup/apply", {"text": "LP1:X+Y&Z 中", "sel": 63})
        self.assertEqual(self.link.board.applied, "LP1:X+Y&Z 中")

    def test_backup_export_with_save(self):
        asked = []
        code, fw = bl.backup_export(self.b, ask_save=lambda: asked.append(1) or True)
        self.assertEqual(code, "LP1:ABCDEF")
        self.assertEqual(fw["ver"], "2026.11.02.2")
        self.assertTrue(self.link.board.saved and asked)
        seen = [s for s in self.link.board.seen if s[1] == "/api/backup"][-1][2]
        self.assertEqual((seen["sel"], seen["sec"]), ("63", "15"))

    def test_backup_export_refused(self):
        with self.assertRaises(bl.BoardError):
            bl.backup_export(self.b, ask_save=lambda: False)

    def test_backup_check_apply(self):
        self.assertTrue(bl.backup_check(self.b, "LP1:ABC")["ok"])
        self.assertFalse(bl.backup_check(self.b, "junk")["ok"])
        r, rs = bl.backup_apply(self.b, "LP1:ABC")
        self.assertEqual((r["code"], rs["code"], self.link.board.applied), ("bkapplied", "saved", "LP1:ABC"))
        with self.assertRaises(bl.BoardError):
            bl.backup_check(bl.SerialBridge(lambda d: True, lambda s: None), "x")   # 沒回應

    def test_backup_file(self):
        text = bl.backup_file_text("LP1:ABC", {"ver": "v", "board": "MINI"}, "COM5")
        self.assertEqual(bl.backup_file_code(text), "LP1:ABC")
        self.assertEqual(bl.backup_file_code("# x\n\n  LP1:Q  \n"), "LP1:Q")

    def test_timeout(self):
        b = bl.SerialBridge(lambda d: True, lambda s: None)   # 寫出去沒人回
        with self.assertRaises(bl.BoardError):
            b.get("/api/fw", timeout=0.2)
        b2 = bl.SerialBridge(lambda d: False, lambda s: None)
        with self.assertRaises(bl.BoardError):
            b2.get("/api/fw", timeout=0.2)

    def test_proxy(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = bl.LocalProxy(self.b, d)
            url = p.start()
            try:
                with urllib.request.urlopen(url) as r:
                    self.assertEqual(r.read(), PAGE)
                with urllib.request.urlopen(url) as r:   # 第二次走快取,不再向板子要
                    self.assertEqual(r.read(), PAGE)
                self.assertEqual(sum(1 for s in self.link.board.seen if s[1] == "/"), 1)
                req = urllib.request.Request(url + "api/setmany?p=s", data=b"x=1\ny=2", method="POST", headers={"Content-Type": "text/plain"})
                with urllib.request.urlopen(req) as r:
                    self.assertEqual(json.loads(r.read())["plain"], "x=1\ny=2")
                req = urllib.request.Request(url + "api/backup/apply", data=b"text=LP1%3AZZ", method="POST",
                                             headers={"Content-Type": "application/x-www-form-urlencoded"})
                with urllib.request.urlopen(req) as r:
                    self.assertTrue(json.loads(r.read())["ok"])
                self.assertEqual(self.link.board.applied, "LP1:ZZ")
                with urllib.request.urlopen(url + "api/log") as r:
                    self.assertEqual(r.headers["Content-Type"], "application/octet-stream")
                    self.assertEqual(len(r.read()), 768 + 14)
                try:
                    urllib.request.urlopen(url + "api/nothing")
                    self.fail("should 404")
                except urllib.error.HTTPError as e:
                    self.assertEqual(e.code, 404)
            finally:
                p.stop()


if __name__ == "__main__":
    unittest.main()
