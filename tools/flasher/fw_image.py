# 版本流水號: r2 (2026-10-29) 版本清單(GG:韌體要讓使用者選,不要只下載最新版);舊版沒有完整燒錄檔時用最新完整檔的開機區組合;
#   ESP 映像檔自我校驗(XOR 檢查碼 + 附加的 SHA-256),本機檔與下載檔都檢查
# 舊: r1 (2026-10-21) 初版:燒錄工具用的韌體檔分析,下載最新版與驗證
# ============================================================================
# 兩種檔案(tools/publish_firmware.py 產生,放在公開韌體專案 licni/ESP32lineplane-firmware):
#  - 完整燒錄檔 lineplane-full-版本[-oled].bin:開機程式 0x0 + 分割表 0x8000 + boot_app0 0xe000 + 韌體 0x10000,從 0x0 燒整片.
#    中間空白(含 NVS 設定區)是 0xFF,燒下去設定一定回出廠值. 全新板子用這個.
#  - 韌體更新檔 firmware-版本[-oled].bin:只有韌體本體,燒在 0x10000. 板上要已經有開機程式與分割表(燒過完整檔).
#    同時把 0xe000 寫成 boot_app0(和 PlatformIO USB 燒錄相同):讓開機程式從 0x10000 開機,不待確認,設定保留.
# 兩種檔案裡都有身分標記「LPFWID1:ESP32C3-lineplane|版本|MINI 或 OLED|」(fw_update.cpp FW_ID_MARK);
# 沒寫種類的舊檔當普通版(和板子 fw_update r7 同規則).
# 版本清單讀公開韌體專案的 GitHub Releases(標籤 v版本). 完整燒錄檔 2026.10.07.1 起才有;更早的版本只有韌體更新檔,
# 下載時接在最新完整燒錄檔的前 64KB(開機程式,分割表,boot_app0;兩種板子相同,平台版本從 2026-09-13 起沒換)後面組成完整燒錄檔.
# 這個檔不碰視窗與序列埠,可以單獨測試(test_fw_image.py).
# ============================================================================
import hashlib
import json
import re
import urllib.error
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
RELEASES_API = f"https://api.github.com/repos/{FW_REPO}/releases?per_page=100"
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


def verify_image(data, offset=0):
    """ESP 映像檔自我校驗(和 esptool image_info 同規則):各段資料的 XOR 檢查碼(初值 0xEF,放在對齊 16 位元組的位置),
    表頭第 23 位元組 = 1 時後面還有前面全部內容的 SHA-256. 回 (通過, 映像檔長度或錯誤原因)."""
    if len(data) < offset + 24 or data[offset] != ESP_IMAGE_MAGIC:
        return False, "開頭不是 ESP 映像檔"
    pos, ck = offset + 24, 0xEF
    for _ in range(data[offset + 1]):
        if pos + 8 > len(data):
            return False, "檔案不完整(段落表頭被截斷)"
        ln = int.from_bytes(data[pos + 4: pos + 8], "little")
        pos += 8
        if pos + ln > len(data):
            return False, "檔案不完整(段落資料被截斷)"
        x = 0
        for b in data[pos: pos + ln]:
            x ^= b
        ck ^= x
        pos += ln
    pos += 15 - (pos % 16)
    if pos >= len(data) or data[pos] != ck:
        return False, "檢查碼不對(檔案損壞或不完整)"
    end = pos + 1
    if data[offset + 23] == 1:
        if hashlib.sha256(data[offset:end]).digest() != data[end:end + 32]:
            return False, "SHA-256 不對(檔案損壞或被改過)"
        end += 32
    return True, end - offset


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
        for off, what in ((0, "開機程式"), (APP_OFFSET, "韌體")):
            ok, why = verify_image(data, off)
            if not ok:
                r["problems"].append(f"{what}{why}")
    elif data[0] == ESP_IMAGE_MAGIC:
        r["kind"] = "app"
        if image_chip_id(data, 0) != CHIP_ID_C3:
            r["problems"].append("這個檔案不是給 ESP32-C3 的")
        if len(data) > APP_MAX:
            r["problems"].append(f"韌體 {len(data)} 位元組,超過韌體區 {APP_MAX} 位元組")
        ok, why = verify_image(data, 0)
        if not ok:
            r["problems"].append(f"韌體{why}")
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


def _get_json(url):
    return json.loads(_get(url).decode("utf-8"))


def list_releases():
    """韌體版本清單,新的在前:[{version, date, notes, assets: {檔名: {url, digest}}, latest}].
    讀 GitHub Releases;讀不到(沒網路,API 次數用完)時退回只列兩份 manifest 的最新版,assets 用命名規則推算(guessed)."""
    try:
        rels = _get_json(RELEASES_API)
        if not isinstance(rels, list):
            raise ValueError(f"Releases 回應格式不對:{str(rels)[:100]}")
        out = []
        for r in rels:
            ver = (r.get("tag_name") or "").lstrip("v")
            if r.get("draft") or not VER_RE.match(ver):
                continue
            assets = {a["name"]: {"url": a["browser_download_url"], "digest": a.get("digest")} for a in r.get("assets", [])}
            out.append({"version": ver, "date": (r.get("published_at") or "")[:10], "notes": (r.get("body") or "").strip(),
                        "assets": assets, "guessed": False})
        if not out:
            raise ValueError("Releases 是空的")
    except (OSError, ValueError, KeyError, urllib.error.URLError) as e:
        out, err = [], e
        for board in VARIANTS:
            try:
                man = _get_json(RAW_BASE + VARIANTS[board][0])
            except (OSError, ValueError):
                continue
            ver = man.get("version", "")
            if VER_RE.match(ver) and not any(x["version"] == ver for x in out):
                out.append({"version": ver, "date": "", "notes": man.get("notes", ""), "assets": {}, "guessed": True})
        if not out:
            raise ValueError(f"讀不到版本清單:{err}")
    out.sort(key=lambda x: ver_key(x["version"]), reverse=True)
    for i, x in enumerate(out):
        x["latest"] = i == 0
    return out


def asset_names(ver, board):
    suffix = VARIANTS[board][1]
    return f"lineplane-full-{ver}{suffix}.bin", f"firmware-{ver}{suffix}.bin"


def release_offers(rel, board):
    """這個版本這種板子能下載什麼:(有完整燒錄檔, 有韌體更新檔). 推算的清單當作都有(下載時才知道)."""
    if rel["guessed"]:
        return True, True
    full, app = asset_names(rel["version"], board)
    return full in rel["assets"], app in rel["assets"]


def _asset(rel, name):
    a = rel["assets"].get(name)
    return (a["url"], a.get("digest")) if a else (f"{RELEASE_BASE}v{rel['version']}/{name}", None)


def _check_digest(data, digest, name):
    if digest and digest.startswith("sha256:") and hashlib.sha256(data).hexdigest() != digest[7:].lower():
        raise ValueError(f"{name} 的 SHA-256 和 GitHub 上記錄的不同(下載不完整),請重新下載")


def boot_area(releases, progress=None):
    """最新完整燒錄檔的前 64KB(開機程式 + 分割表 + boot_app0). 只抓前 64KB(HTTP Range),伺服器不支援時整個下載再切."""
    for rel in releases:
        for board in VARIANTS:
            full, _ = asset_names(rel["version"], board)
            if rel["guessed"] or full in rel["assets"]:
                url, _ = _asset(rel, full)
                req = urllib.request.Request(url, headers={"User-Agent": "LineplaneFlasher", "Range": f"bytes=0-{APP_OFFSET - 1}"})
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        head = resp.read()[:APP_OFFSET]
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        continue
                    raise
                ok, why = verify_image(head, 0)
                if (len(head) == APP_OFFSET and ok and head[PARTITION_OFFSET:PARTITION_OFFSET + 2] == PART_MAGIC
                        and any(p[1] == 0 and p[3] == APP_OFFSET for p in partitions(head))):
                    return head, rel["version"]
                raise ValueError(f"{full} 的開機區檢查不通過:{why if not ok else '分割表不對'}")
    raise ValueError("找不到任何完整燒錄檔,無法組合")


def download_version(rel, board, keep_settings, releases, progress=None, log=None):
    """下載指定版本. 回 (檔名, 內容).
    keep_settings:只下載韌體更新檔(燒 0x10000,保留設定). 否則下載完整燒錄檔;這版沒有就用 boot_area 組合.
    驗證:映像檔自我校驗,身分標記的版本與種類,有 GitHub 記錄的 SHA-256 時也比對. 失敗丟 ValueError."""
    ver = rel["version"]
    full_name, app_name = asset_names(ver, board)
    has_full, has_app = release_offers(rel, board)
    data = name = None
    if not keep_settings and has_full:
        url, digest = _asset(rel, full_name)
        try:
            data, name = _get(url, timeout=60, progress=progress), full_name
            _check_digest(data, digest, full_name)
        except urllib.error.HTTPError as e:
            if e.code != 404 or not rel["guessed"]:
                raise
            data = None   # 推算的清單:這版其實沒有完整燒錄檔,改用組合
    if data is None:
        if not has_app:
            raise ValueError(f"{ver} 沒有{board_name(board)}的韌體檔(帶螢幕板 2026.09.25.1 起才有)")
        url, digest = _asset(rel, app_name)
        app = _get(url, timeout=60, progress=progress)
        _check_digest(app, digest, app_name)
        if keep_settings:
            data, name = app, app_name
        else:
            head, from_ver = boot_area(releases)
            if log:
                log(f"{ver} 沒有完整燒錄檔:用 {from_ver} 完整燒錄檔的開機程式與分割表,接上 {app_name} 組成完整燒錄檔")
            data, name = head + app, full_name
    a = analyze(data)
    if a["problems"]:
        raise ValueError(f"下載的 {name} 檢查不通過:" + ";".join(a["problems"]))
    if a["kind"] != ("app" if keep_settings else "full"):
        raise ValueError(f"下載的 {name} 種類不對")
    if (a["version"], a["board"]) != (ver, board):
        raise ValueError(f"下載的檔案身分是 {a['version']} {a['board']},應該是 {ver} {board}")
    return name, data
