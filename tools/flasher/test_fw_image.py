# 版本流水號: r1 (2026-10-21) 初版:fw_image 單元測試(不需要網路與板子,GitHub Actions 打包前執行)
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


def app_image(ver="2026.10.07.1", board="MINI", chip=f.CHIP_ID_C3, size=200000):
    d = bytearray(b"\x00" * size)
    d[0:24] = esp_header(chip)
    mark = f.ID_PREFIX + f"{ver}|{board}|".encode() + b"\x00" if board else f.ID_PREFIX + f"{ver}|".encode() + b"\x00"
    d[5000:5000 + len(mark)] = mark
    return bytes(d)


def full_image(app):
    d = bytearray(b"\xff" * f.APP_OFFSET)
    d[0:24] = esp_header()
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

    def test_no_identity_warns(self):
        d = bytearray(app_image())
        d[5000:5010] = b"\x00" * 10
        a = f.analyze(bytes(d))
        self.assertIsNone(a["version"])
        self.assertEqual(len(a["warnings"]), 2)

    def test_boot_app0(self):
        b = f.boot_app0()
        self.assertEqual(len(b), 0x2000)
        self.assertEqual(sum(1 for x in b if x != 0xFF), 12)   # 和 Arduino 核心 boot_app0.bin 一樣只有 12 個位元組不是 0xFF

    def test_urls(self):
        self.assertEqual(f.full_image_url("2026.10.07.1", "OLED"),
                         "https://github.com/licni/ESP32lineplane-firmware/releases/download/v2026.10.07.1/lineplane-full-2026.10.07.1-oled.bin")
        self.assertLess(f.ver_key("2026.09.14.9"), f.ver_key("2026.09.14.10"))


if __name__ == "__main__":
    unittest.main()
