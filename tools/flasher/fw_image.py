# 版本流水號: r1 (2026-10-21) 初版:燒錄工具用的韌體檔分析,下載最新版與驗證
# ============================================================================
# 兩種檔案(tools/publish_firmware.py 產生,放在公開韌體專案 licni/ESP32lineplane-firmware):
#  - 完整燒錄檔 lineplane-full-版本[-oled].bin:開機程式 0x0 + 分割表 0x8000 + boot_app0 0xe000 + 韌體 0x10000,從 0x0 燒整片.
#    中間空白(含 NVS 設定區)是 0xFF,燒下去設定一定回出廠值. 全新板子用這個.
#  - 韌體更新檔 firmware-版本[-oled].bin:只有韌體本體,燒在 0x10000. 板上要已經有開機程式與分割表(燒過完整檔).
#    同時把 0xe000 寫成 boot_app0(和 PlatformIO USB 燒錄相同):讓開機程式從 0x10000 開機,不待確認,設定保留.
# 兩種檔案裡都有身分標記「LPFWID1:ESP32C3-lineplane|版本|MINI 或 OLED|」(fw_update.cpp FW_ID_MARK);
# 沒寫種類的舊檔當普通版(和板子 fw_update r7 同規則).
# 這個檔不碰視窗與序列埠,可以單獨測試(test_fw_image.py).
# ============================================================================
import hashlib
import json
import re
import urllib.request

APP_OFFSET = 0x10000
OTADATA_OFFSET = 0xE000
OTADATA_SIZE = 0x2000
PARTITION_OFFSET = 0x8000
APP_MAX = 0x1E0000            # min_spiffs.csv 的 app0/app1 大小
FLASH_SIZE = 0x400000         # SuperMini 4MB
ESP_IMAGE_MAGIC = 0xE9
PART_MAGIC = b"\xaa\x50"
CHIP_ID_C3 = 0x0005           # 韌體映像檔表頭的晶片代號(ESP32-C3)
ID_PREFIX = b"LPFWID1:ESP32C3-lineplane|"
BOARDS = {"MINI": "普通版", "OLED": "帶螢幕板"}

FW_REPO = "licni/ESP32lineplane-firmware"
RAW_BASE = f"https://raw.githubusercontent.com/{FW_REPO}/main/"
RELEASE_BASE = f"https://github.com/{FW_REPO}/releases/download/"
# (種類,manifest,檔名後綴):和 publish_firmware.py 的 VARIANTS 相同
VARIANTS = {"MINI": ("manifest.json", ""), "OLED": ("manifest-oled.json", "-oled")}
VER_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}\.\d+$")


def find_identity(data):
    """回 (版本, 種類) 或 None. 種類沒寫的舊檔回 MINI."""
    i = data.find(ID_PREFIX)
    if i < 0:
        return None
    tail = data[i + len(ID_PREFIX): i + len(ID_PREFIX) + 64].split(b"\x00")[0]
    parts = tail.decode("ascii", "replace").split("|")
    ver = parts[0] if parts else ""
    if not VER_RE.match(ver):
        return None
    board = parts[1] if len(parts) > 2 and parts[1] in BOARDS else "MINI"
    return ver, board


def image_chip_id(data, offset):
    """ESP 韌體映像檔表頭的晶片代號(表頭 24 位元組,chip_id 在第 12~13 位元組);不是映像檔回 None."""
    if len(data) < offset + 24 or data[offset] != ESP_IMAGE_MAGIC:
        return None
    return int.from_bytes(data[offset + 12: offset + 14], "little")


def partitions(data):
    """完整燒錄檔裡的分割表 [(名稱, 種類, 子種類, 位址, 大小)]."""
    out = []
    for p in range(PARTITION_OFFSET, PARTITION_OFFSET + 0xC00, 32):
        e = data[p: p + 32]
        if len(e) < 32 or e[:2] != PART_MAGIC:
            break
        name = e[12:28].split(b"\x00")[0].decode("ascii", "replace")
        out.append((name, e[2], e[3], int.from_bytes(e[4:8], "little"), int.from_bytes(e[8:12], "little")))
    return out


def analyze(data):
    """分析檔案內容. 回 dict:
    kind    'full'(完整燒錄檔,0x0)/'app'(韌體更新檔,0x10000)/'bad'
    version,board 身分標記(沒有是 None)
    problems  不能燒的原因(空清單 = 可以燒)
    warnings  可以燒但要提醒的事
    """
    r = {"kind": "bad", "size": len(data), "version": None, "board": None, "problems": [], "warnings": []}
    ident = find_identity(data)
    if ident:
        r["version"], r["board"] = ident
    if len(data) < 1024:
        r["problems"].append("檔案太小,不是韌體檔")
        return r
    is_full = (len(data) > APP_OFFSET + 24 and data[0] == ESP_IMAGE_MAGIC and data[PARTITION_OFFSET:PARTITION_OFFSET + 2] == PART_MAGIC
               and data[APP_OFFSET] == ESP_IMAGE_MAGIC)
    if is_full:
        r["kind"] = "full"
        if len(data) > FLASH_SIZE:
            r["problems"].append(f"檔案 {len(data)} 位元組,超過 4MB 快閃記憶體")
        if image_chip_id(data, 0) != CHIP_ID_C3 or image_chip_id(data, APP_OFFSET) != CHIP_ID_C3:
            r["problems"].append("這個檔案不是給 ESP32-C3 的")
        apps = [p for p in partitions(data) if p[1] == 0]
        if not any(p[3] == APP_OFFSET for p in apps):
            r["problems"].append("分割表裡沒有 0x10000 的韌體區,不是本專案的完整燒錄檔")
    elif data[0] == ESP_IMAGE_MAGIC:
        r["kind"] = "app"
        if image_chip_id(data, 0) != CHIP_ID_C3:
            r["problems"].append("這個檔案不是給 ESP32-C3 的")
        if len(data) > APP_MAX:
            r["problems"].append(f"韌體 {len(data)} 位元組,超過韌體區 {APP_MAX} 位元組")
        r["warnings"].append("這是韌體更新檔(只有韌體本體):只適合已經燒過完整燒錄檔的板子,設定會保留. 全新板子請用 lineplane-full-*.bin")
    else:
        r["problems"].append("不是 ESP32 韌體檔(開頭不是 0xE9)")
        return r
    if not ident:
        r["warnings"].append("檔案裡找不到線控飛機韌體的身分標記,可能不是本專案的韌體")
    return r


def boot_app0():
    """otadata 初始內容,和 Arduino 核心的 boot_app0.bin 相同:第 1 個序號,開機選 0x10000 的 app0,狀態未定(不待確認)."""
    d = bytearray(b"\xff" * OTADATA_SIZE)
    d[0:4] = (1).to_bytes(4, "little")
    d[28:32] = bytes.fromhex("9a984347")   # 序號 1 的 CRC32(ESP-IDF esp_rom_crc32_le)
    d[0x1000:0x1004] = (0).to_bytes(4, "little")
    return bytes(d)


def ver_key(ver):
    return tuple(int(x) for x in ver.split(".")) if ver and VER_RE.match(ver) else None


def board_name(board):
    return BOARDS.get(board, board or "不明")


def _get(url, timeout=20, progress=None):
    req = urllib.request.Request(url, headers={"User-Agent": "LineplaneFlasher"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = int(resp.headers.get("Content-Length") or 0)
        chunks, got = [], 0
        while True:
            b = resp.read(65536)
            if not b:
                break
            chunks.append(b)
            got += len(b)
            if progress:
                progress(got, total)
        return b"".join(chunks)


def latest_manifest(board):
    mname, _ = VARIANTS[board]
    man = json.loads(_get(RAW_BASE + mname).decode("utf-8"))
    if not VER_RE.match(man.get("version", "")):
        raise ValueError(f"{mname} 的版本號格式不對:{man.get('version')}")
    return man


def full_image_url(ver, board):
    return f"{RELEASE_BASE}v{ver}/lineplane-full-{ver}{VARIANTS[board][1]}.bin"


def download_latest_full(board, progress=None):
    """下載最新版完整燒錄檔並驗證. 回 (檔案內容, manifest). 驗證失敗丟 ValueError.
    驗證:身分標記的版本與種類,0x10000 起的韌體本體和 manifest 的大小與 SHA-256 相同(publish_firmware 發布時也檢查同一件事)."""
    man = latest_manifest(board)
    ver = man["version"]
    data = _get(full_image_url(ver, board), timeout=60, progress=progress)
    a = analyze(data)
    if a["kind"] != "full" or a["problems"]:
        raise ValueError("下載的檔案不是完整燒錄檔:" + ";".join(a["problems"] or ["格式不對"]))
    if (a["version"], a["board"]) != (ver, board):
        raise ValueError(f"下載的檔案身分是 {a['version']} {a['board']},應該是 {ver} {board}")
    app = data[APP_OFFSET: APP_OFFSET + int(man["size"])]
    if len(app) != int(man["size"]) or hashlib.sha256(app).hexdigest() != man["sha256"].lower():
        raise ValueError("下載的檔案檢查碼不對(下載不完整或被改過),請重新下載")
    return data, man
