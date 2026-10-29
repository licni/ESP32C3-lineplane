# 版本流水號: r2 (2026-10-29) 假韌體改成有效的 ESP 映像檔(檢查碼,SHA-256);版本清單,映像檔校驗,損壞檔測試
# 舊: r1 (2026-10-21) 初版:fw_image 單元測試(不需要網路與板子,GitHub Actions 打包前執行)
import hashlib
import unittest

import fw_image as f


def esp_header(chip=f.CHIP_ID_C3):
    h = bytearray(24)
    h[0] = f.ESP_IMAGE_MAGIC
    h[12:14] = chip.to_bytes(2, "little")
    return bytes(h)


def part_entry(name, ptype, sub, off, size):
    e = bytearray(32)
    e[0:2] = f.PART_MAGIC
    e[2], e[3] = ptype, sub
    e[4:8] = off.to_bytes(4, "little")
    e[8:12] = size.to_bytes(4, "little")
    e[12:12 + len(name)] = name.encode()
    return bytes(e)


def esp_image(payload, chip=f.CHIP_ID_C3):
    """一段資料的有效 ESP 映像檔:表頭,段落,對齊 16 的 XOR 檢查碼,附加 SHA-256."""
    h = bytearray(esp_header(chip))
    h[1] = 1
    h[23] = 1
    d = h + (0).to_bytes(4, "little") + len(payload).to_bytes(4, "little") + payload
    ck = 0xEF
    for x in payload:
        ck ^= x
    d += b"\x00" * (15 - len(d) % 16) + bytes([ck])
    return bytes(d + hashlib.sha256(d).digest())


def app_image(ver="2026.10.07.1", board="MINI", chip=f.CHIP_ID_C3, size=200000):
    payload = bytearray(b"\x5a" * size)
    mark = f.ID_PREFIX + f"{ver}|{board}|".encode() + b"\x00" if board else f.ID_PREFIX + f"{ver}|".encode() + b"\x00"
    payload[5000:5000 + len(mark)] = mark
    return esp_image(bytes(payload), chip)


def full_image(app):
    d = bytearray(b"\xff" * f.APP_OFFSET)
    boot = esp_image(b"\x11" * 1000)
    d[0:len(boot)] = boot
    table = part_entry("nvs", 1, 2, 0x9000, 0x5000) + part_entry("otadata", 1, 0, 0xE000, 0x2000) + \
        part_entry("app0", 0, 0x10, 0x10000, 0x1E0000) + part_entry("app1", 0, 0x11, 0x1F0000, 0x1E0000)
    d[f.PARTITION_OFFSET:f.PARTITION_OFFSET + len(table)] = table
    d[f.OTADATA_OFFSET:f.OTADATA_OFFSET + f.OTADATA_SIZE] = f.boot_app0()
    return bytes(d) + app


class FwImageTest(unittest.TestCase):
    def test_app(self):
        a = f.analyze(app_image())
        self.assertEqual((a["kind"], a["version"], a["board"], a["problems"]), ("app", "2026.10.07.1", "MINI", []))
        self.assertTrue(a["warnings"])   # 提醒只適合已燒過完整檔的板子

    def test_full_oled(self):
        a = f.analyze(full_image(app_image(board="OLED")))
        self.assertEqual((a["kind"], a["version"], a["board"], a["problems"], a["warnings"]), ("full", "2026.10.07.1", "OLED", [], []))

    def test_old_mark_without_board_is_mini(self):
        self.assertEqual(f.find_identity(app_image(board=None)), ("2026.10.07.1", "MINI"))

    def test_wrong_chip(self):
        self.assertTrue(f.analyze(app_image(chip=0))["problems"])        # ESP32
        self.assertTrue(f.analyze(full_image(app_image(chip=9)))["problems"])   # ESP32-S3

    def test_not_firmware(self):
        a = f.analyze(b"hello" * 1000)
        self.assertEqual(a["kind"], "bad")
        self.assertTrue(a["problems"])

    def test_too_big_app(self):
        self.assertTrue(f.analyze(app_image(size=f.APP_MAX + 1))["problems"])

    def test_corrupt(self):
        d = bytearray(app_image())
        d[100] ^= 1   # 改一個位元組:XOR 檢查碼對不上
        self.assertTrue(f.analyze(bytes(d))["problems"])
        self.assertTrue(f.analyze(app_image()[:150000])["problems"])   # 下載不完整

    def test_no_identity_warns(self):
        a = f.analyze(esp_image(b"\x5a" * 50000))
        self.assertIsNone(a["version"])
        self.assertEqual(len(a["warnings"]), 2)

    def test_boot_app0(self):
        b = f.boot_app0()
        self.assertEqual(len(b), 0x2000)
        self.assertEqual(sum(1 for x in b if x != 0xFF), 12)   # 和 Arduino 核心 boot_app0.bin 一樣只有 12 個位元組不是 0xFF

    def test_names(self):
        self.assertEqual(f.asset_names("2026.10.07.1", "OLED"), ("lineplane-full-2026.10.07.1-oled.bin", "firmware-2026.10.07.1-oled.bin"))
        self.assertLess(f.ver_key("2026.09.14.9"), f.ver_key("2026.09.14.10"))

    def test_release_list_and_offers(self):
        def rel(v, names):
            return {"tag_name": "v" + v, "draft": False, "published_at": "2026-10-07T01:02:03Z", "body": "x",
                    "assets": [{"name": n, "browser_download_url": "https://example/" + n} for n in names]}
        fake = [rel("2026.09.24.2", ["firmware-2026.09.24.2.bin"]),
                rel("2026.10.07.1", ["firmware-2026.10.07.1.bin", "lineplane-full-2026.10.07.1.bin"]),
                {"tag_name": "flasher-v1.0.0", "draft": False, "assets": []}]
        orig = f._get_json
        f._get_json = lambda url: fake
        try:
            rels = f.list_releases()
        finally:
            f._get_json = orig
        self.assertEqual([(r["version"], r["latest"], r["date"]) for r in rels],
                         [("2026.10.07.1", True, "2026-10-07"), ("2026.09.24.2", False, "2026-10-07")])
        self.assertEqual(f.release_offers(rels[0], "MINI"), (True, True))
        self.assertEqual(f.release_offers(rels[1], "MINI"), (False, True))
        self.assertEqual(f.release_offers(rels[1], "OLED"), (False, False))

    def test_verify_image(self):
        app = app_image()
        self.assertEqual(f.verify_image(app), (True, len(app)))
        bad = bytearray(app)
        bad[-1] ^= 1   # 只改 SHA-256
        self.assertFalse(f.verify_image(bytes(bad))[0])


if __name__ == "__main__":
    unittest.main()
