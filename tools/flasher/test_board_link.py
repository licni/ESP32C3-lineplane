# 版本流水號: r4 (2026-11-04) 即時姿態:get_status / get_settings
# 舊: r3 (2026-11-04) 水平標定:level_set 成功(回兩個修正值,板上變未儲存)/ 沒放穩被拒(中文訊息)/ 舊韌體 404;save_settings
# 舊: r2 (2026-11-03) WiFi 設定:wifi_get / wifi_set(拒絕碼轉中文)/ wifi_scan(掃描中 → 結果)/ wifi_keep / reboot
# 舊: r1 (2026-11-02) 初版:USB 設定通道的電腦端測試(假板子照 web_server.cpp r33 的協定回應,不需要板子與序列埠)
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
        self.wifi = {"ssid": "Home", "pw": "secret123", "host": "lineplane", "tmo": 30, "forceap": 0, "txp": 5, "txmin": 2, "txmax": 20,
                     "tmomin": 10, "tmomax": 120, "apssid": "HappySuperGG_Plane", "apnow": "HappySuperGG_Plane", "apprefix": "HappySuperGG_Plane",
                     "apsfx": "", "appw": "12345678", "apsfxmax": 14, "build": "test"}
        self.scan_polls = 0
        self.kept = False
        self.rebooted = False
        self.still = True          # 水平標定:飛機放穩了
        self.has_level = True      # False = 舊韌體,/api/level 回 404

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
            return 200, "application/json", b'{"ok":true,"code":"bkapplied","gen":7,"names":["a"],"wifisaved":1}'
        if (method, path) == ("POST", "/api/reboot"):
            self.rebooted = True
            return 200, "application/json", b'{"ok":true,"code":"reboot"}'
        if (method, path) == ("POST", "/api/wifi/keep"):
            self.kept = True
            return 200, "application/json", b'{"ok":true,"code":"kept"}'
        if (method, path) == ("GET", "/api/wifi"):
            return 200, "application/json", json.dumps(self.wifi, ensure_ascii=False).encode("utf-8")
        if (method, path) == ("POST", "/api/wifi"):
            # 照 handleWifiSet:欄位不齊 badform,後綴太長 apsfxlong,密碼 1~7 碼 pwshort;通過就存起來(試用)
            for f in ("ssid", "pw", "host", "tmo", "forceap", "txp"):
                if f not in a:
                    return 400, "application/json", b'{"ok":false,"code":"badform"}'
            if len(a.get("apsfx", "").encode("utf-8")) > 14:
                return 400, "application/json", b'{"ok":false,"code":"apsfxlong"}'
            if 0 < len(a["pw"]) < 8:
                return 400, "application/json", b'{"ok":false,"code":"pwshort"}'
            self.wifi.update({k: a[k] for k in ("ssid", "pw", "host", "apsfx", "appw") if k in a})
            self.wifi.update(tmo=int(a["tmo"]), forceap=int(a["forceap"]), txp=int(a["txp"]))
            return 200, "application/json", b'{"ok":true,"code":"saved"}'
        if (method, path) == ("POST", "/api/wifi/scan"):
            self.scan_polls = 0
            return 200, "application/json", b'{"ok":true,"code":"scanning"}'
        if (method, path) == ("GET", "/api/wifi/scan"):
            self.scan_polls += 1
            if self.scan_polls < 3:   # 前兩次還在掃
                return 200, "application/json", b'{"run":1}'
            return 200, "application/json", json.dumps({"run": 0, "n": 2, "list": [["GG iPhone", -48, 6, 0], ["Home 家", -70, 11, 1]]}, ensure_ascii=False).encode("utf-8")
        if (method, path) == ("GET", "/api/status"):
            return 200, "application/json", b'{"p":1.25,"rp":-2.4,"r":-3.0,"rr":-13.7,"a":0.96,"st":1,"imu":1,"f":{"s":1}}'
        if (method, path) == ("GET", "/api/settings"):
            return 200, "application/json", b'{"shared":{"noseAxis":0,"upAxis":4,"pitchTrim":3.6,"rollTrim":13.7},"profile":{}}'
        if (method, path) == ("POST", "/api/level") and self.has_level:
            # 照 handleLevel:沒放穩 levelstill;成功填兩個修正值(未儲存)
            if not self.still:
                return 400, "application/json", b'{"ok":false,"code":"levelstill"}'
            self.dirty = True
            return 200, "application/json", b'{"ok":true,"code":"level","pt":-2.3,"rt":1.0}'
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

    def test_level_set_and_save(self):
        self.link.board.dirty = False
        r = bl.level_set(self.b)
        self.assertEqual((r["pt"], r["rt"]), (-2.3, 1.0))
        self.assertTrue(self.link.board.dirty)   # 填了修正值但還沒儲存
        bl.save_settings(self.b)
        self.assertTrue(self.link.board.saved)
        self.assertFalse(self.link.board.dirty)

    def test_status_and_settings(self):
        s = bl.get_status(self.b)
        self.assertEqual((s["p"], s["r"], s["rr"], s["imu"]), (1.25, -3.0, -13.7, 1))
        sh = bl.get_settings(self.b)["shared"]
        self.assertEqual((sh["noseAxis"], sh["upAxis"], sh["rollTrim"]), (0, 4, 13.7))

    def test_level_refused_not_still(self):
        self.link.board.still = False
        with self.assertRaises(bl.BoardError) as cm:
            bl.level_set(self.b)
        self.assertIn("放穩", str(cm.exception))

    def test_level_old_firmware(self):
        self.link.board.has_level = False
        with self.assertRaises(bl.BoardError) as cm:
            bl.level_set(self.b)
        self.assertIn("2026.11.04.1", str(cm.exception))

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

    def test_wifi_get_set_keep_reboot(self):
        w = bl.wifi_get(self.b)
        self.assertEqual((w["ssid"], w["apprefix"], w["apsfxmax"]), ("Home", "HappySuperGG_Plane", 14))
        cfg = {"ssid": "GG iPhone", "pw": "hotspot99", "host": w["host"], "tmo": w["tmo"], "forceap": 0, "txp": w["txp"], "apsfx": "3號", "appw": "abcd1234"}
        bl.wifi_set(self.b, cfg)
        board = self.link.board.wifi
        self.assertEqual((board["ssid"], board["pw"], board["apsfx"], board["appw"], board["forceap"]), ("GG iPhone", "hotspot99", "3號", "abcd1234", 0))
        # 板子拒絕 → 中文訊息
        with self.assertRaises(bl.BoardError) as cm:
            bl.wifi_set(self.b, dict(cfg, pw="short"))
        self.assertIn("至少 8 碼", str(cm.exception))
        with self.assertRaises(bl.BoardError) as cm:
            bl.wifi_set(self.b, dict(cfg, apsfx="太長太長太長"))
        self.assertIn("太長", str(cm.exception))
        with self.assertRaises(bl.BoardError):
            bl.wifi_set(self.b, {"ssid": "x"})   # 欄位不齊
        bl.wifi_keep(self.b)
        bl.reboot(self.b)
        self.assertTrue(self.link.board.kept and self.link.board.rebooted)

    def test_wifi_scan(self):
        items = bl.wifi_scan(self.b, timeout=5, sleep=lambda s: None)
        self.assertEqual(items, [("GG iPhone", -48, 6, 0), ("Home 家", -70, 11, 1)])
        self.assertEqual(self.link.board.scan_polls, 3)

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
