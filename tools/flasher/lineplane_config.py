# 版本流水號: r16 (2026-11-04) 即時姿態(GG:設定器也要有網頁那樣的飛機圖,不用一直進網頁就知道姿態對不對):水平標定區加側視/後視飛機圖,
#   每 0.2 秒讀 /api/status(USB 或 WiFi),顯示控制使用與修正前的機頭/滾轉,安裝方位與修正值;燒錄等工作進行中自動暫停;標定成功自動開啟;APP_VERSION 2.5.0
# 舊: r15 (2026-11-04) 設定頁加「水平標定」區(GG:設定器也要能標定水平):確認飛機擺平 → POST /api/level(韌體 2026.11.04.1 起)
#   → 顯示兩個修正值 → 問要不要儲存;APP_VERSION 2.4.0
# 舊: r14 (2026-11-03) 燒錄後檢查的 WiFi 項目等到連上或退回熱點為止(最多 45 秒)再顯示結果與網址(GG:更新後顯示「連線中」以為沒連上;
#   原本只問一次 net,板子還在掃描);設定了家用 WiFi 卻退到熱點用黃字提醒;完成對話框寫 WiFi 結果;APP_VERSION 2.3.2
# 舊: r13 (2026-11-03) 三個分頁「① 燒錄與板子訊息 ② 設定 ③ 備份」(GG:備份拆出去);區塊改成自製 _section(灰邊框 + 淺藍標題色帶,
#   GG:ttk.LabelFrame 的框線太淡,連線方式/WiFi 設定分不出來);連線方式在 ②③ 都有(共用變數);APP_VERSION 2.3.1
# 舊: r12 (2026-11-03) WiFi 設定區 + 板子訊息中文化(GG:使用者用手機熱點怎樣都連不上;快捷指令對終端使用者沒意義,回應要中文):
#   設定與備份頁新增「WiFi 設定」(USB 線):讀板上設定,選「板子自己開熱點(熱點名稱固定開頭 + 可改後綴,密碼)/ 連家用 WiFi 或手機熱點(名稱可搜尋附近,密碼)」,
#   按「套用到板子並測試連線」→ 寫入 → 重開 → 等 WiFi 就緒 → 連上就自動保持(固定)並用大字顯示網址(IP 與 lineplane.local);連不上問要不要改回原設定.
#   板子訊息區:快捷鈕改「板子狀態 / 重新開機」,板子回的英文訊息翻成中文(可勾「顯示原始訊息」),送指令列收進「進階」;APP_VERSION 2.3.0
# 舊: r11 (2026-11-02) 燒錄頁重新設計(GG:使用者不該知道普通/full 檔):選版本 + 燒錄方式「更新(保留設定)/全新燒錄(清空)」,
#   按開始燒錄自動下載對應檔案;兩種都先自動備份板上設定(只存檔,不寫回;更新方式設定本來就不動);空白板子選更新時自動改全新燒錄;
#   拿掉帶螢幕板選項;「選電腦裡的檔案」收進進階;APP_VERSION 2.2.0
# 舊: r10 (2026-11-02) 監看區至少 12 行(GG);APP_VERSION 2.1.1
# 舊: r9 (2026-11-02) 預設保留板上設定(GG:燒完設定不見);燒完整燒錄檔時自動備份板上設定,燒完檢查後自動寫回(含 WiFi:套用後重開機再保持);APP_VERSION 2.1.0
# 舊: r8 (2026-11-02) 高 DPI(GG:第一次打開只看到一半):視窗開啟時依內容需要的大小與螢幕自動調整,放不下就最大化;折行寬度依 DPI 縮放;APP_VERSION 2.0.5
# 舊: r7 (2026-11-02) 板子訊息併入燒錄頁(GG):兩個分頁「燒錄與板子訊息」「設定與備份」;APP_VERSION 2.0.4
# 舊: r6 (2026-11-02) 版本說明去掉 Markdown 粗體符號(GG:說明要給終端使用者看);APP_VERSION 2.0.3
# 舊: r5 (2026-11-02) 連續燒多片(GG:自動偵測只有第一片會跳出):監看守著的埠不見了(換板子)就停掉監看改選新板子;APP_VERSION 2.0.2
# 舊: r4 (2026-11-02) 分頁改成自製大按鈕(TabBar,GG:ttk 的分頁框太不明顯);APP_VERSION 2.0.1
# 舊: r3 (2026-11-02) 改名「線控飛機設定器」LineplaneConfig.exe,APP_VERSION 2.0.0(GG:燒錄器改寫成設定器):
#   兩個分頁(燒錄與板子訊息 / 設定與備份);USB 線開板子那一份設定網頁(board_link.py 本機轉送,需韌體 2026.11.02.2 以上);
#   WiFi 也能開;匯出/匯入板上全部設定備份(USB 或 WiFi);燒完整燒錄檔前先問要不要匯出備份
# 舊: r2 (2026-10-29) 韌體版本讓使用者選(GG:不要只下載最新版):版本清單,版本說明,保留設定選項;APP_VERSION 1.1.0
# 舊: r1 (2026-10-21) 初版:免安裝燒錄工具(GG:給不想裝開發環境的使用者)
# ============================================================================
# 線控飛機設定器(燒錄 + 設定 + 備份 + 監看). 打包成單一 exe(PyInstaller,見 build_exe.bat 與 .github/workflows/flasher.yml).
#  - 序列埠:自動偵測 ESP32-C3 原生 USB(VID 303A),也可以手動選.
#  - 設定:電腦上開一個小伺服器(board_link.LocalProxy),瀏覽器開它就是板子那一份網頁,請求透過 USB 線轉給板子;
#    或直接用 WiFi 開 http://lineplane.local. 備份匯出/匯入兩種連線都能用.
#  - 韌體檔:從公開韌體專案的版本清單選一版下載(普通版/帶螢幕板,下載後驗證),或選本機 .bin.
#    預設下載完整燒錄檔(全新板子可用);勾「保留板上設定」只下載韌體更新檔.
#  - 燒錄:用 esptool(當成函式庫呼叫,不另外安裝). 完整燒錄檔從 0x0 燒(可先清除整片);
#    韌體更新檔燒 0x10000 並把 otadata 寫成 boot_app0(設定保留,和 PlatformIO USB 燒錄相同,不待確認).
#  - 檢查:esptool 寫完逐段校驗檢查碼;重新開機後送序列指令 fw / mpu / net,確認版本,感測器與 WiFi.
#  - 序列監看(燒錄頁下方):板子回報的訊息翻成中文顯示(translate_line;勾「顯示原始訊息」看英文原文),「板子狀態」送 fw/net/fs/mpu,
#    「重新開機」送 reboot;「進階」才有送指令列(help 列出全部).
#  - WiFi 設定(設定頁,只走 USB):GET /api/wifi 讀 → POST /api/wifi 寫(板子存成試用)→ POST /api/reboot → 等板子回來 → 序列指令 net
#    看 wifi=sta|ap|connecting → 符合要的模式就 POST /api/wifi/keep 固定,大字顯示網址;要連家用 WiFi 卻退到熱點 = 連不上,問要不要改回原設定.
# 序列埠一律 dtr=False, rts=False 再開(C3 原生 USB 把 DTR/RTS 切換當成重置).
# 只用 Python 內建 tkinter + esptool + pyserial. 開發測試:python lineplane_config.py
# ============================================================================
import contextlib
import io
import json
import math
import os
import queue
import re
import sys
import tempfile
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

import serial
import serial.tools.list_ports

import board_link
import fw_image

APP_VERSION = "2.5.0"
TITLE = f"線控飛機設定器 v{APP_VERSION}"
USB_API_MIN_FW = "2026.11.02.2"   # USB 設定通道從這版韌體開始
BAUD_FLASH = 921600            # 原生 USB 不看鮑率;USB 轉序列晶片的板子才有差
BAUD_MONITOR = 115200
ESPRESSIF_VID = 0x303A
USB_UART_VIDS = {0x1A86: "CH340", 0x10C4: "CP210x", 0x0403: "FTDI"}
MAX_LOG_LINES = 5000

# windowed exe 沒有主控台,sys.stdout 是 None:任何 print 都會出錯,先接到空的地方
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def data_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    d = os.path.join(base, "LineplaneConfig")
    os.makedirs(d, exist_ok=True)
    return d


def load_prefs():
    try:
        with open(os.path.join(data_dir(), "settings.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_prefs(p):
    try:
        with open(os.path.join(data_dir(), "settings.json"), "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def list_ports():
    """[(裝置, 顯示文字, 分數)],分數高的排前面:ESP32-C3 原生 USB 2,USB 轉序列晶片 1,其他 0."""
    out = []
    for p in serial.tools.list_ports.comports():
        if p.vid == ESPRESSIF_VID:
            score, kind = 2, "ESP32-C3 原生 USB"
        elif p.vid in USB_UART_VIDS:
            score, kind = 1, USB_UART_VIDS[p.vid]
        else:
            score, kind = 0, p.description or "序列埠"
        out.append((p.device, f"{p.device}  —  {kind}", score))
    out.sort(key=lambda x: (-x[2], x[0]))
    return out


def open_serial(port):
    s = serial.Serial()
    s.port = port
    s.baudrate = BAUD_MONITOR
    s.timeout = 0.1
    s.dtr = False   # 開之前設好:開啟時不切 DTR/RTS,板子不會重開
    s.rts = False
    s.open()
    return s


def friendly_error(text):
    t = text.lower()
    if "could not open port" in t or "access is denied" in t or "permissionerror" in t or "拒絕存取" in text:
        return "序列埠打不開:可能被其他程式佔用(Arduino IDE,其他監看視窗),或板子剛被拔掉. 關掉其他程式後再試."
    if "failed to connect" in t or "no serial data received" in t or "wrong boot mode" in t:
        return "連不上板子. 請按住板子上的 BOOT 鍵,拔掉再插上 USB,放開 BOOT 後再按一次「開始燒錄」."
    if "wrong --chip" in t or "this chip is" in t:
        return "接上的板子不是 ESP32-C3:" + text
    return text


# ---------------- 板子訊息翻譯(GG 2026-11-03:終端使用者看不懂英文訊息) ----------------
# 板子序列埠印的固定格式訊息 → 中文. 沒對到的照原文顯示;開機 ROM 的雜訊(ESP-ROM:,load:,entry …)藏起來.
CMD_NAMES = {"fw": "查詢韌體版本", "net": "查詢 WiFi 狀態", "fs": "查詢飛行狀態", "mpu": "查詢感測器", "reboot": "重新開機",
             "t": "切換即時資料", "help": "列出全部指令"}
FLIGHT_NAMES = {"arming": "解鎖中", "standby": "待機", "wait_still": "等待放穩", "countdown": "倒數中", "takeoff": "起飛",
                "flying": "飛行中", "landing": "降落中", "done": "飛行結束"}
NET_RE = re.compile(r"^wifi=(\w+) ip=(\S*) rssi=(-?\d+) host=(\S+) ssid=(.*) txp=(\d+)dBm$")


def parse_net(line):
    """序列指令 net 的回應 → dict(wifi, ip, rssi, host, ssid, txp);不是 net 的回應回 None."""
    m = NET_RE.match(line)
    if not m:
        return None
    wifi, ip, rssi, host, ssid, txp = m.groups()
    return {"wifi": wifi, "ip": ip, "rssi": int(rssi), "host": host, "ssid": ssid, "txp": int(txp)}


def _tr_fw(m):
    ver, busy, pend, remain, rb, rbfrom, _check, err, remote, _size, prog = m.groups()
    parts = [f"韌體版本 {ver}"]
    if busy == "1":
        parts.append(f"更新下載中 {prog}%")
    if pend == "1":
        parts.append(f"新韌體待確認(剩 {remain} 秒;用 WiFi 開網頁會自動確認,沒確認會退回舊版)")
    if rb == "1":
        parts.append(f"上次更新到 {rbfrom} 沒有確認,已退回這版" if rbfrom else "上次更新沒有確認,已退回這版")
    if remote:
        parts.append(f"網站上的版本 {remote}")
    if err:
        parts.append(f"更新錯誤 {err}")
    return ",".join(parts)


def _tr_net(m):
    wifi, ip, rssi, host, ssid, txp = m.groups()
    if wifi == "ap":
        return f"WiFi:板子自己開熱點,位址 http://{ip}(手機連板子的熱點後開這個網址);發射功率 {txp} dBm"
    if wifi == "sta":
        return f"WiFi:已連上「{ssid}」,位址 http://{ip} 或 http://{host}(Android 請用 IP);訊號 {rssi} dBm,發射功率 {txp} dBm"
    return f"WiFi:正在連「{ssid}」…(連不上會自動改開熱點)"


def _tr_fs(m):
    state, secs, cd, t, out = m.group(1), m.group(2), m.group(3), m.group(4), m.group(7)
    text = f"飛行狀態:{FLIGHT_NAMES.get(state, state)}(已 {float(secs):.0f} 秒)"
    if state == "countdown":
        text += f",倒數剩 {float(cd):.0f} 秒"
    if state in ("takeoff", "flying", "landing"):
        text += f",油門 {float(out):.0f}%(飛行 {float(t):.0f} 秒)"
    return text


def _tr_rst(m):
    why = m.group(1)
    kind = "上電" if "POWERON" in why else ("燒錄工具重置" if "USB_UART" in why else "軟體重開")
    return f"板子重新開機({kind})"


TRANSLATE = [
    (re.compile(r"^version=(\S+) busy=(\d) pending=(\d) remain=(-?\d+) rolledBack=(\d)\((.*?)\) check=(\d) err=(\S*) remote=(\S*) size=(\d+) prog=(\d+)"), _tr_fw),
    (NET_RE, _tr_net),
    (re.compile(r"^state=(\w+) ([\d.]+)s cd=([\d.-]+) t=([\d.-]+) base=([\d.-]+) comp=([\d.-]+) out=([\d.-]+)"), _tr_fs),
    (re.compile(r"^ERR MPU in use"), lambda m: "感測器 MPU6050:正常(控制迴圈使用中)"),
    (re.compile(r"^MPU OK"), lambda m: "感測器 MPU6050:正常"),
    (re.compile(r"^ERR MPU"), lambda m: "感測器 MPU6050:找不到(檢查 SDA→GPIO5,SCL→GPIO6,VCC,GND 接線)"),
    (re.compile(r"^board (.+), arm switch GPIO(\d+)"), lambda m: f"板子開機:{m.group(1)},安全開關接 GPIO{m.group(2)}"),
    (re.compile(r"^FW version (\S+) I2C SDA=(\d+) SCL=(\d+)"), lambda m: f"韌體 {m.group(1)},感測器接 GPIO{m.group(2)}/GPIO{m.group(3)}"),
    (re.compile(r"^ESC protocol (\S+) (\d+)Hz"), lambda m: f"電變訊號 {m.group(1)} {m.group(2)}Hz"),
    (re.compile(r"^ESC calibration: output (\d+)us for ([\d.]+)s"), lambda m: f"電變校正:輸出 {m.group(1)} µs 持續 {m.group(2)} 秒"),
    (re.compile(r"^ESC calibration pending"), lambda m: "電變校正已排定(下次拔電再接電時執行)"),
    (re.compile(r"^READY"), lambda m: "板子開機完成"),
    (re.compile(r"^rst:0x[0-9a-f]+ \((\w+)\)"), _tr_rst),
    (re.compile(r"^STA scanning for (.*)"), lambda m: f"WiFi:搜尋「{m.group(1)}」…"),
    (re.compile(r"^STA best node RSSI=(-?\d+)dBm"), lambda m: f"WiFi:找到訊號 {m.group(1)} dBm 的節點,連線中"),
    (re.compile(r"^STA -> generic connect"), lambda m: "WiFi:指定節點連不上,改用一般方式連線"),
    (re.compile(r"^STA connected IP=(\S+) RSSI=(-?\d+)"), lambda m: f"WiFi:已連上家用 WiFi / 手機熱點,位址 http://{m.group(1)}(訊號 {m.group(2)} dBm)"),
    (re.compile(r"^STA ssid not found -> AP"), lambda m: "WiFi:附近找不到設定的 WiFi 名稱(是不是 5GHz?或名稱打錯),改開板子自己的熱點"),
    (re.compile(r"^STA timeout -> AP"), lambda m: "WiFi:等太久連不上(多半是密碼錯),改開板子自己的熱點"),
    (re.compile(r"^STA lost -> reconnecting"), lambda m: "WiFi:家用 WiFi 斷線,重新連線中"),
    (re.compile(r"^STA lost too long -> AP"), lambda m: "WiFi:斷線太久,改開板子自己的熱點"),
    (re.compile(r"^AP SSID=(.*) IP=(\S+)"), lambda m: f"WiFi:已開熱點「{m.group(1)}」,手機連這個熱點後開 http://{m.group(2)}"),
    (re.compile(r"^mDNS http://(\S+)"), lambda m: f"網址 http://{m.group(1)} 可用(電腦與 iPhone;Android 請用 IP)"),
    (re.compile(r"^mDNS start failed"), lambda m: "名稱網址(lineplane.local)啟動失敗,請用 IP"),
    (re.compile(r"^WiFi settings confirmed"), lambda m: "WiFi 設定已確認,固定使用"),
    (re.compile(r"^WiFi settings kept for now"), lambda m: "目前的 WiFi 設定先保留;新設定重開後仍要再確認"),
    (re.compile(r"^WiFi settings not confirmed"), lambda m: "WiFi 新設定 3 分鐘內沒有確認,已改回上一次的設定"),
    (re.compile(r"^WiFi rescue"), lambda m: "連續開關電 3 次:WiFi 設定已回出廠(板子自己開熱點 HappySuperGG_Plane,密碼 12345678)"),
    (re.compile(r"^WiFi tx power not confirmed -> back to (\d+)dBm"), lambda m: f"發射功率沒有確認,退回 {m.group(1)} dBm"),
    (re.compile(r"^WiFi scan: (\d+) found, (\d+) listed"), lambda m: f"WiFi 搜尋完成:找到 {m.group(1)} 個,列出 {m.group(2)} 個"),
    (re.compile(r"^OK saved, type 'reboot' to connect"), lambda m: "WiFi 設定已儲存,重新開機後連線"),
    (re.compile(r"^OK txp (\d+)dBm"), lambda m: f"發射功率 {m.group(1)} dBm 已生效並儲存"),
    (re.compile(r"^OTA start"), lambda m: "無線韌體更新開始"),
    (re.compile(r"^OTA done"), lambda m: "無線韌體更新完成,重新開機"),
    (re.compile(r"^OTA refused"), lambda m: "無線韌體更新被拒(板子不在待機)"),
    (re.compile(r"^WEB OTA start"), lambda m: "網頁韌體上傳開始"),
    (re.compile(r"^I2C bus was stuck"), lambda m: "感測器匯流排開機時卡住,已解除"),
    (re.compile(r"^backup codec ok"), lambda m: "設定備份編碼表正常"),
    (re.compile(r"^flight log: flash (\d+) sectors \((\d+) samples, ([\d.]+) min\)"), lambda m: f"飛行紀錄區:可存 {m.group(2)} 筆(約 {m.group(3)} 分鐘)"),
    (re.compile(r"^ERR buzzer"), lambda m: "蜂鳴器 PWM 無法使用(無源蜂鳴器不會響)"),
    (re.compile(r"^commands: "), lambda m: "可用的序列指令:" + m.string[10:]),
]
HIDE_RE = re.compile(r"^(ESP-ROM:|Build:|SPIWP:|mode:|load:0x|entry 0x|configsip|clk_drv|Saved PC:|FW id LPFWID)")


def translate_line(line):
    """板子的一行訊息 → 中文;沒對到回原文;開機 ROM 雜訊回 None(不顯示)."""
    for rx, fn in TRANSLATE:
        m = rx.match(line)
        if m:
            return fn(m)
    if HIDE_RE.match(line):
        return None
    return line


class _LineWriter(io.TextIOBase):
    """esptool 的 print 輸出切成一行一行交給 cb(\r 也當換行)."""

    def __init__(self, cb):
        self.cb = cb
        self.buf = ""

    def write(self, s):
        self.buf += s
        parts = re.split(r"[\r\n]", self.buf)
        self.buf = parts.pop()
        for line in parts:
            if line.strip():
                self.cb(line.rstrip())
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return False


class Monitor:
    """序列監看:背景讀取,一行一行交給 on_line;斷線後(板子重開,拔插)自動重連.
    收到的位元組全部先經過 bridge(USB 設定通道):@A 回應配給等待中的請求,其他整行才交給 on_line."""

    def __init__(self, on_line, on_state):
        self.on_line = on_line
        self.on_state = on_state
        self.port = None
        self.ser = None
        self.want = False
        self.lock = threading.Lock()
        self.thread = None
        self.bridge = board_link.SerialBridge(self.send_raw, on_line)

    def start(self, port):
        self.stop()
        self.port = port
        self.want = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.want = False
        t = self.thread
        if t and t.is_alive() and t is not threading.current_thread():
            t.join(timeout=2)
        self.thread = None
        self._close()

    def _close(self):
        with self.lock:
            if self.ser:
                with contextlib.suppress(Exception):
                    self.ser.close()
            self.ser = None

    def connected(self):
        return self.ser is not None

    def send(self, text):
        return self.send_raw((text + "\n").encode("utf-8"))

    def send_raw(self, data):
        with self.lock:
            if not self.ser:
                return False
            try:
                self.ser.write(data)
                return True
            except Exception:
                return False

    def wait_connected(self, timeout):
        t0 = time.time()
        while not self.connected() and time.time() - t0 < timeout:
            time.sleep(0.1)
        return self.connected()

    def _run(self):
        announced = False
        while self.want:
            if not self.ser:
                try:
                    s = open_serial(self.port)
                except Exception as e:
                    if not announced:
                        self.on_state(False, f"等待 {self.port} …({e.__class__.__name__})")
                        announced = True
                    time.sleep(0.5)
                    continue
                with self.lock:
                    self.ser = s
                announced = False
                self.bridge.reset()
                self.on_state(True, f"已連線 {self.port}")
            try:
                b = self.ser.read(4096)
            except Exception:
                self._close()
                self.bridge.reset()
                self.on_state(False, f"{self.port} 中斷,等待重新連線 …")
                continue
            if b:
                self.bridge.feed(b)
        self._close()
        self.bridge.reset()
        self.on_state(False, "監看已停止")


class TabBar(ttk.Frame):
    """分頁列:自己畫的大按鈕(ttk.Notebook 在 Windows 的分頁框太淡,GG 看不出來). 選中的藍底白字加底線,其他灰底.
    介面對齊 Notebook 的 select/index,切換時呼叫 on_change."""

    SEL_BG, SEL_FG, BG, FG = "#1f5fbf", "#ffffff", "#e4e7ec", "#333333"

    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.buttons = []
        self.frames = []
        self.cur = -1
        self.bar = tk.Frame(self, background="#c9ced6")
        self.bar.pack(fill="x")
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)

    def add(self, frame, text):
        i = len(self.frames)
        fam = "Microsoft JhengHei UI" if sys.platform == "win32" else "TkDefaultFont"
        b = tk.Button(self.bar, text=text, font=(fam, 13, "bold"), relief="flat", bd=0, cursor="hand2", padx=22, pady=9,
                      activebackground=self.SEL_BG, activeforeground=self.SEL_FG, command=lambda i=i: self.select(i))
        b.pack(side="left", padx=(0, 2))
        self.buttons.append(b)
        self.frames.append(frame)
        frame.grid(in_=self.body, row=0, column=0, sticky="nsew")
        frame.grid_remove()
        if self.cur < 0:
            self.select(0)

    def select(self, i=None):
        if i is None:
            return self.cur
        i = int(i)
        if not 0 <= i < len(self.frames):
            return
        for j, (b, f) in enumerate(zip(self.buttons, self.frames)):
            sel = j == i
            b.configure(background=self.SEL_BG if sel else self.BG, foreground=self.SEL_FG if sel else self.FG)
            if sel:
                f.grid()
            else:
                f.grid_remove()
        changed = i != self.cur
        self.cur = i
        if changed and self.on_change:
            self.on_change(i)

    def index(self, i):
        return int(i)


class App:
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.prefs = load_prefs()
        self.busy = False            # 燒錄或檢查中
        self.ports = []              # [(裝置, 顯示文字, 分數)]
        self.listeners = []          # 檢查流程用:收板子訊息的佇列
        self.image = None            # (路徑, 內容, 分析結果)
        self.releases = []           # fw_image.list_releases() 的結果
        self.shown = []              # 版本下拉選單目前列出的 release(和選單順序相同)
        self.monitor = Monitor(lambda line: self.q.put(("board", line)),
                               lambda ok, msg: self.q.put(("mon_state", (ok, msg))))
        self.proxy = board_link.LocalProxy(self.monitor.bridge, os.path.join(data_dir(), "pages"),
                                           log=lambda m: self.q.put(("tool", m)))
        self._build()
        self.root.after(0, self._fit_window)
        self._scan_ports(force=True)
        self.root.after(1500, self._port_loop)
        self._load_releases()
        self._mode_changed()
        self.root.after(50, self._poll)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- 畫面 ----------------
    def _build(self):
        r = self.root
        r.title(TITLE)
        r.minsize(760, 620)
        # 高 DPI(Windows 125%~200%):字會跟著放大,折行寬度(像素)要一起放大,不然版面變很高
        try:
            self.dpi = max(1.0, r.winfo_fpixels("1i") / 96.0)
        except Exception:
            self.dpi = 1.0
        W = lambda px: int(px * self.dpi)   # noqa: E731
        pad = {"padx": 8, "pady": 4}
        main = ttk.Frame(r, padding=8)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        # 序列埠(三個分頁共用)
        f1 = self._section(main, "開發板序列埠(USB 線)", 0)
        f1.columnconfigure(1, weight=1)
        self.auto_port = tk.BooleanVar(value=True)
        ttk.Checkbutton(f1, text="自動偵測", variable=self.auto_port, command=lambda: self._scan_ports(force=True)).grid(row=0, column=0, sticky="w")
        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(f1, textvariable=self.port_var, state="readonly")
        self.port_cb.grid(row=0, column=1, sticky="ew", padx=6)
        self.port_cb.bind("<<ComboboxSelected>>", lambda e: self.auto_port.set(False))
        ttk.Button(f1, text="重新整理", command=lambda: self._scan_ports(force=True)).grid(row=0, column=2)
        self.port_hint = ttk.Label(f1, text="", foreground="#555")
        self.port_hint.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        self.nb = TabBar(main, on_change=lambda i: self._save_tab())
        self.nb.grid(row=1, column=0, sticky="nsew", **pad)
        tab_flash = ttk.Frame(self.nb.body, padding=(4, 8, 4, 4))
        tab_cfg = ttk.Frame(self.nb.body, padding=(4, 8, 4, 4))
        tab_bk = ttk.Frame(self.nb.body, padding=(4, 8, 4, 4))
        self.nb.add(tab_flash, text="① 燒錄與板子訊息")
        self.nb.add(tab_cfg, text="② 設定")
        self.nb.add(tab_bk, text="③ 備份")
        for t in (tab_flash, tab_cfg, tab_bk):
            t.columnconfigure(0, weight=1)
        tab_flash.rowconfigure(2, weight=1)   # 板子訊息區吃掉剩下的高度

        # 燒錄分頁 1. 韌體檔
        f2 = self._section(tab_flash, "1. 韌體檔", 0)
        f2.columnconfigure(1, weight=1)
        self.board_var = tk.StringVar(value="MINI")   # 帶螢幕板已不維護(GG 2026-10-29),設定器只燒普通版
        ttk.Label(f2, text="韌體版本").grid(row=0, column=0, sticky="w")
        self.ver_var = tk.StringVar()
        self.ver_cb = ttk.Combobox(f2, textvariable=self.ver_var, state="readonly")
        self.ver_cb.grid(row=0, column=1, sticky="ew", padx=6)
        self.ver_cb.bind("<<ComboboxSelected>>", lambda e: self._version_changed())
        self.reload_btn = ttk.Button(f2, text="重新整理", command=self._load_releases)
        self.reload_btn.grid(row=0, column=2)
        self.notes = ttk.Label(f2, text="讀取版本清單中 …", foreground="#555", wraplength=W(700), justify="left")
        self.notes.grid(row=1, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        ttk.Label(f2, text="燒錄方式").grid(row=2, column=0, sticky="w", pady=(8, 0))
        mode_row = ttk.Frame(f2)
        mode_row.grid(row=2, column=1, columnspan=2, sticky="w", padx=6, pady=(8, 0))
        self.mode_var = tk.StringVar(value="keep")
        ttk.Radiobutton(mode_row, text="更新:保留板上設定(建議)", value="keep", variable=self.mode_var, command=self._mode_changed).pack(side="left")
        ttk.Radiobutton(mode_row, text="全新燒錄:清空設定,回出廠值", value="new", variable=self.mode_var, command=self._mode_changed).pack(side="left", padx=(16, 0))
        self.mode_hint = ttk.Label(f2, text="", foreground="#555", wraplength=W(700), justify="left")
        self.mode_hint.grid(row=3, column=1, columnspan=2, sticky="w", padx=6, pady=(2, 0))
        self.erase_var = tk.BooleanVar(value=True)
        self.erase_cb = ttk.Checkbutton(f2, text="燒錄前先清除整片(全新燒錄才有作用;建議勾選)", variable=self.erase_var)
        self.erase_cb.grid(row=4, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        # 進階:自己選檔案(平常收起來,使用者不必知道普通/完整燒錄檔)
        self.adv_btn = ttk.Button(f2, text="進階 ▸", width=8, command=self._toggle_adv)
        self.adv_btn.grid(row=5, column=0, sticky="w", pady=(8, 0))
        self.adv = ttk.Frame(f2)
        self.adv.grid(row=6, column=0, columnspan=3, sticky="ew")
        self.adv.columnconfigure(1, weight=1)
        self.adv.grid_remove()
        ttk.Label(self.adv, text="要燒的檔案").grid(row=0, column=0, sticky="w")
        self.file_var = tk.StringVar()
        e = ttk.Entry(self.adv, textvariable=self.file_var)
        e.grid(row=0, column=1, sticky="ew", padx=6)
        e.bind("<Return>", lambda ev: self._load_file(self.file_var.get().strip().strip('"')))
        ttk.Button(self.adv, text="選電腦裡的檔案…", command=self._browse).grid(row=0, column=2)
        ttk.Button(self.adv, text="改回自動下載", command=self._clear_file).grid(row=0, column=3, padx=(4, 0))
        self.file_info = ttk.Label(self.adv, text="沒有指定檔案:按「開始燒錄」會依上面選的版本與方式自動下載. 這裡可以改燒自己下載的 .bin.",
                                   foreground="#555", wraplength=W(700), justify="left")
        self.file_info.grid(row=1, column=1, columnspan=3, sticky="w", padx=6, pady=(4, 0))

        # 燒錄分頁 2. 燒錄與檢查
        f3 = self._section(tab_flash, "2. 燒錄與檢查", 1)
        f3.columnconfigure(1, weight=1)
        self.flash_btn = ttk.Button(f3, text="開始燒錄", command=self._start_flash, style="Big.TButton")
        self.flash_btn.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))
        self.prog = ttk.Progressbar(f3, maximum=100)
        self.prog.grid(row=0, column=1, sticky="ew")
        self.stage = ttk.Label(f3, text="等待開始")
        self.stage.grid(row=1, column=1, sticky="w")
        self.check_btn = ttk.Button(f3, text="只做檢查", command=self._start_check_only)
        self.check_btn.grid(row=0, column=2, rowspan=2, sticky="ns", padx=(10, 0))
        self.auto_check = tk.BooleanVar(value=True)
        opt = ttk.Frame(f3)
        opt.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        ttk.Checkbutton(opt, text="燒錄完自動檢查", variable=self.auto_check).pack(side="left")
        self.bk_flash_btn = ttk.Button(opt, text="匯出板上設定備份…", command=lambda: self._backup_export())
        self.bk_flash_btn.pack(side="left", padx=(16, 4))
        ttk.Label(opt, text="(燒錄前會自動備份板上設定存成檔案)", foreground="#555").pack(side="left")
        chk = ttk.Frame(f3)
        chk.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        self.checks = {}
        chk.columnconfigure(1, weight=1)
        chk.columnconfigure(3, weight=1)
        for i, (key, name) in enumerate([("chip", "晶片"), ("verify", "寫入校驗"), ("boot", "開機與版本"),
                                         ("mpu", "感測器 MPU6050"), ("wifi", "WiFi")]):
            ttk.Label(chk, text=name + ":").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=(0 if i % 2 == 0 else 16, 0))
            lab = ttk.Label(chk, text="—", foreground="#777", wraplength=W(330), justify="left")
            lab.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", padx=6)
            self.checks[key] = lab

        # 設定分頁(連線方式在設定頁與備份頁都有,共用同一組變數)
        self.link_var = tk.StringVar(value=self.prefs.get("link", "usb"))
        self.host_var = tk.StringVar(value=self.prefs.get("host", "lineplane.local"))
        self._conn_section(tab_cfg, 0)

        fs = self._section(tab_cfg, "設定板子(和手機看到的網頁完全相同)", 1)
        fs.columnconfigure(1, weight=1)
        self.cfg_btn = ttk.Button(fs, text="開啟設定網頁", command=self._open_config, style="Big.TButton")
        self.cfg_btn.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))
        self.cfg_state = ttk.Label(fs, text="按下後會用電腦的瀏覽器打開設定網頁.", wraplength=W(620), justify="left")
        self.cfg_state.grid(row=0, column=1, sticky="w")
        ttk.Label(fs, text="USB 線:網頁透過這個程式轉送到板子,程式關掉網頁就斷線. 韌體更新請用「燒錄」頁(勾保留板上設定).\n"
                           "WiFi:直接開板子的網頁,和手機一樣.", foreground="#555", wraplength=W(620), justify="left").grid(row=1, column=1, sticky="w", pady=(4, 0))

        # 水平標定(GG 2026-11-03:好幾片 MPU 放平讀值不是 0,設定器也要能標定;板子網頁的安裝頁也有同一顆按鈕)
        fl = self._section(tab_cfg, "水平標定(把飛機現在的姿勢當成水平)", 2)
        fl.columnconfigure(1, weight=1)
        self.level_btn = ttk.Button(fl, text="水平標定", command=self._level_calib, style="Big.TButton")
        self.level_btn.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))
        self.level_state = ttk.Label(fl, text="把飛機擺成平飛姿勢(用你平常調機的水平基準),放穩不要碰,再按左邊的按鈕.", wraplength=W(620), justify="left")
        self.level_state.grid(row=0, column=1, sticky="w")
        ttk.Label(fl, text="板子會把當下量到的機頭與滾轉角度當成 0°,填進「角度修正」與「滾轉修正」,問過你再儲存. 每片感測器的零點都不一樣,"
                           "裝機後做一次;換感測器或重新安裝後再做. 需要韌體 2026.11.04.1 以上.",
                  foreground="#555", wraplength=W(620), justify="left").grid(row=1, column=1, sticky="w", pady=(4, 0))
        # 即時姿態(GG 2026-11-04:和網頁安裝頁同一套側視/後視圖,不用開網頁就能看姿態對不對)
        att = ttk.Frame(fl)
        att.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        abar = ttk.Frame(att)
        abar.pack(fill="x")
        self.att_btn = ttk.Button(abar, text="開始即時姿態", command=self._att_toggle)
        self.att_btn.pack(side="left")
        self.att_state = ttk.Label(abar, text="檢查方式:抬機頭,側視圖的機頭也要抬起;抬左翼,後視圖的左翼也要抬起. 反了就是感測器安裝方位選錯(在設定網頁的安裝頁改).",
                                   foreground="#555", wraplength=W(560), justify="left")
        self.att_state.pack(side="left", padx=8)
        views = ttk.Frame(att)
        views.pack(anchor="w", pady=(6, 0))
        self.att_cw = W(300)
        self.att_ch = int(self.att_cw * 0.625)
        cv_opt = {"width": self.att_cw, "height": self.att_ch, "background": "#f7f9fc", "highlightthickness": 1, "highlightbackground": "#c5ccd6"}
        self.att_side = tk.Canvas(views, **cv_opt)
        self.att_side.pack(side="left")
        self.att_rear = tk.Canvas(views, **cv_opt)
        self.att_rear.pack(side="left", padx=(8, 0))
        afam = "Microsoft JhengHei UI" if sys.platform == "win32" else "TkDefaultFont"
        self.att_font = afam
        self.att_read = tk.Label(att, text="", font=(afam, 13, "bold"), anchor="w", justify="left")
        self.att_read.pack(fill="x", pady=(6, 0))
        self.att_sub = ttk.Label(att, text="", foreground="#555", wraplength=W(620), justify="left")
        self.att_sub.pack(fill="x")
        self.att_on = False
        self.att_gen = 0
        self._att_draw(None)

        # WiFi 設定(GG 2026-11-03:使用者用手機熱點怎樣都連不上,要能在設定器改;只走 USB 線,改完板子重開會斷 WiFi)
        fw = self._section(tab_cfg, "WiFi 設定(用 USB 線設定板子怎麼連網)", 3)
        fw.columnconfigure(1, weight=1)
        top = ttk.Frame(fw)
        top.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.wifi_read_btn = ttk.Button(top, text="讀取板上設定", command=self._wifi_read)
        self.wifi_read_btn.pack(side="left")
        self.wifi_state = ttk.Label(top, text="接上 USB 線後按「讀取板上設定」,或直接改好按下面的套用.", foreground="#555", wraplength=W(600), justify="left")
        self.wifi_state.pack(side="left", padx=8)
        self.wmode = tk.StringVar(value="ap")
        ttk.Radiobutton(fw, text="板子自己開熱點:手機直接連板子的 WiFi(出廠方式,不需要其他網路)", value="ap", variable=self.wmode,
                        command=self._wifi_mode_changed).grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Radiobutton(fw, text="板子連到家用 WiFi 或手機熱點:手機和板子連同一個網路", value="sta", variable=self.wmode,
                        command=self._wifi_mode_changed).grid(row=2, column=0, columnspan=3, sticky="w")
        self.wsta = []   # 連家用 WiFi 才有用的欄位(熱點模式時變灰)
        lab = ttk.Label(fw, text="WiFi 名稱")
        lab.grid(row=3, column=0, sticky="w", padx=(24, 0))
        self.wssid = tk.StringVar()
        self.wssid_cb = ttk.Combobox(fw, textvariable=self.wssid)
        self.wssid_cb.grid(row=3, column=1, sticky="ew", padx=6)
        self.wssid_cb.bind("<<ComboboxSelected>>", lambda e: self._wifi_ssid_picked())
        self.scan_items = {}   # 下拉文字 → (ssid, open)
        self.wifi_scan_btn = ttk.Button(fw, text="搜尋附近 WiFi", command=self._wifi_scan)
        self.wifi_scan_btn.grid(row=3, column=2, sticky="w")
        lab2 = ttk.Label(fw, text="WiFi 密碼")
        lab2.grid(row=4, column=0, sticky="w", padx=(24, 0), pady=(4, 0))
        self.wpw = tk.StringVar()
        self.wpw_e = ttk.Entry(fw, textvariable=self.wpw, show="•")
        self.wpw_e.grid(row=4, column=1, sticky="ew", padx=6, pady=(4, 0))
        self.wpw_show = tk.BooleanVar(value=False)
        pwc = ttk.Checkbutton(fw, text="顯示", variable=self.wpw_show, command=lambda: self.wpw_e.configure(show="" if self.wpw_show.get() else "•"))
        pwc.grid(row=4, column=2, sticky="w", pady=(4, 0))
        hint = ttk.Label(fw, text="手機熱點要開 2.4GHz 板子才看得到:iPhone 在「個人熱點」打開「最大化相容性」;Android 在熱點設定把頻段選 2.4GHz.\n"
                                  "名稱與密碼分大小寫;開放網路密碼留空. 連上後手機開網頁用下面顯示的 IP(iPhone 與電腦也可以用 lineplane.local).",
                         foreground="#555", wraplength=W(680), justify="left")
        hint.grid(row=5, column=0, columnspan=3, sticky="w", padx=(24, 0), pady=(2, 0))
        self.wsta = [lab, self.wssid_cb, self.wifi_scan_btn, lab2, self.wpw_e, pwc, hint]
        ttk.Label(fw, text="板子的熱點(連不上上面的 WiFi 時也會自動開這個):", foreground="#333").grid(row=6, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Label(fw, text="熱點名稱").grid(row=7, column=0, sticky="w", padx=(24, 0))
        apn = ttk.Frame(fw)
        apn.grid(row=7, column=1, columnspan=2, sticky="ew", padx=6)
        self.ap_prefix = "HappySuperGG_Plane"
        self.ap_prefix_lab = ttk.Label(apn, text=self.ap_prefix, font=("Consolas", 10))
        self.ap_prefix_lab.pack(side="left")
        self.wsfx = tk.StringVar()
        self.wsfx.trace_add("write", lambda *a: self._wifi_ap_preview())
        ttk.Entry(apn, textvariable=self.wsfx, width=16).pack(side="left")
        self.ap_preview = ttk.Label(apn, text="", foreground="#555")
        self.ap_preview.pack(side="left", padx=8)
        ttk.Label(fw, text="熱點密碼").grid(row=8, column=0, sticky="w", padx=(24, 0), pady=(4, 0))
        self.wappw = tk.StringVar()
        self.wappw_e = ttk.Entry(fw, textvariable=self.wappw, show="•")
        self.wappw_e.grid(row=8, column=1, sticky="ew", padx=6, pady=(4, 0))
        self.wappw_show = tk.BooleanVar(value=False)
        ttk.Checkbutton(fw, text="顯示", variable=self.wappw_show,
                        command=lambda: self.wappw_e.configure(show="" if self.wappw_show.get() else "•")).grid(row=8, column=2, sticky="w", pady=(4, 0))
        ttk.Label(fw, text="固定開頭後面可以接數字或名字(最多 14 個英數字),同場好幾架飛機才分得出來. 密碼 8~63 個英數字,出廠 12345678.",
                  foreground="#555", wraplength=W(680), justify="left").grid(row=9, column=0, columnspan=3, sticky="w", padx=(24, 0), pady=(2, 0))
        self.wifi_apply_btn = ttk.Button(fw, text="套用到板子並測試連線", command=self._wifi_apply, style="Big.TButton")
        self.wifi_apply_btn.grid(row=10, column=0, columnspan=3, sticky="w", pady=(8, 0))
        bigfam = "Microsoft JhengHei UI" if sys.platform == "win32" else "TkDefaultFont"
        self.wifi_big = tk.Label(fw, text="", font=(bigfam, 15, "bold"), foreground="#1a7f37", justify="left", anchor="w", wraplength=W(700))
        self.wifi_big.grid(row=11, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        self.wifi_big.grid_remove()
        self._wifi_mode_changed()
        self._wifi_ap_preview()

        # 備份分頁(GG 2026-11-03:從設定頁拆出來)
        self._conn_section(tab_bk, 0)
        fb = self._section(tab_bk, "板上設定備份(全部 6 組飛行風格 + 起飛降落與安全 / 安裝 / 電變 / WiFi)", 1)
        fb.columnconfigure(2, weight=1)
        self.bk_out_btn = ttk.Button(fb, text="匯出板上設定備份…", command=lambda: self._backup_export())
        self.bk_out_btn.grid(row=0, column=0, sticky="w")
        self.bk_in_btn = ttk.Button(fb, text="匯入備份到板子…", command=self._backup_import)
        self.bk_in_btn.grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.bk_state = ttk.Label(fb, text="", wraplength=W(600), justify="left")
        self.bk_state.grid(row=0, column=2, sticky="w", padx=8)
        ttk.Label(fb, text="匯出存成文字檔(裡面是板子網頁「備份」頁用的設定備份碼). 匯入會先檢查,顯示內容後才套用並儲存;\n"
                           "板上有未儲存的變更時會先問要不要儲存. 含 WiFi 的備份套用後 WiFi 設定為試用,重新開機後 3 分鐘內要在網頁按「保持」.\n"
                           "燒錄頁的「開始燒錄」也會先自動備份一份到電腦(%LOCALAPPDATA%\\LineplaneConfig\\backups).",
                  foreground="#555", wraplength=W(700), justify="left").grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # 燒錄分頁 3. 板子訊息(序列監看)
        f4 = self._section(tab_flash, "3. 板子回報訊息(序列監看)", 2, fill="nsew")
        f4.columnconfigure(0, weight=1)
        f4.rowconfigure(1, weight=1)
        bar = ttk.Frame(f4)
        bar.grid(row=0, column=0, sticky="ew")
        self.mon_btn = ttk.Button(bar, text="開始監看", command=self._toggle_monitor)
        self.mon_btn.pack(side="left")
        ttk.Button(bar, text="清除", command=lambda: self.log.delete("1.0", "end")).pack(side="left", padx=4)
        ttk.Button(bar, text="存成文字檔…", command=self._save_log).pack(side="left")
        self.mon_state = ttk.Label(bar, text="未連線", foreground="#777")
        self.mon_state.pack(side="left", padx=10)
        self.autoscroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="自動捲動", variable=self.autoscroll).pack(side="right")
        txt = ttk.Frame(f4)
        txt.grid(row=1, column=0, sticky="nsew", pady=4)
        txt.columnconfigure(0, weight=1)
        txt.rowconfigure(0, weight=1)
        mono = ("Consolas", 10) if sys.platform == "win32" else ("Monospace", 10)
        self.log = tk.Text(txt, height=12, wrap="word", font=mono, background="#111", foreground="#ddd", insertbackground="#ddd")
        self.log.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(txt, command=self.log.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=sb.set)
        self.log.tag_configure("tool", foreground="#7fb8ff")
        self.log.tag_configure("err", foreground="#ff7b7b")
        self.log.tag_configure("ok", foreground="#7ee787")
        self.log.tag_configure("sent", foreground="#e3b341")
        # 快捷動作(GG 2026-11-03:fw/net/fs/t/help 對終端使用者沒意義):板子狀態 = 送 fw/net/fs/mpu,回應翻成中文;送指令列收進進階
        quick = ttk.Frame(f4)
        quick.grid(row=2, column=0, sticky="ew", pady=(2, 0))
        self.status_btn = ttk.Button(quick, text="板子狀態", command=self._board_status)
        self.status_btn.pack(side="left")
        self.reboot_btn = ttk.Button(quick, text="重新開機", command=self._reboot_board)
        self.reboot_btn.pack(side="left", padx=(4, 0))
        self.cmd_adv_btn = ttk.Button(quick, text="進階 ▸", width=8, command=self._toggle_cmd_adv)
        self.cmd_adv_btn.pack(side="right")
        self.raw_var = tk.BooleanVar(value=bool(self.prefs.get("raw", False)))
        ttk.Checkbutton(quick, text="顯示原始英文訊息", variable=self.raw_var, command=self._save_link).pack(side="right", padx=(0, 10))
        self.cmd_row = ttk.Frame(f4)
        self.cmd_row.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        self.cmd_row.columnconfigure(1, weight=1)
        self.cmd_row.grid_remove()
        ttk.Label(self.cmd_row, text="送指令").grid(row=0, column=0)
        self.cmd_var = tk.StringVar()
        ce = ttk.Entry(self.cmd_row, textvariable=self.cmd_var)
        ce.grid(row=0, column=1, sticky="ew", padx=6)
        ce.bind("<Return>", lambda ev: self._send_cmd())
        ttk.Button(self.cmd_row, text="送出", command=self._send_cmd).grid(row=0, column=2)
        for label, c in [("fw", "fw"), ("net", "net"), ("fs", "fs"), ("t", "t"), ("help", "help")]:
            ttk.Button(self.cmd_row, text=label, width=5, command=lambda c=c: self._send_cmd(c)).grid(row=0, column=3 + ["fw", "net", "fs", "t", "help"].index(c), padx=(4, 0))

        self.status = ttk.Label(r, text="", relief="sunken", anchor="w", padding=(6, 2))
        self.status.pack(side="bottom", fill="x")
        self._log(f"{TITLE}. 接上開發板後會自動偵測序列埠. 燒錄與測試前請拆下螺旋槳.", "tool")
        self.nb.select({"flash": 0, "cfg": 1, "bk": 2}.get(self.prefs.get("tab", "flash"), 0))

    def _section(self, parent, title, row, fill="ew"):
        """有明顯邊框與標題色帶的區塊(GG 2026-11-03:ttk.LabelFrame 的框線太淡,區塊分不出來). 回內容框(用 grid 排)."""
        outer = tk.Frame(parent, highlightbackground="#9aa4b2", highlightthickness=1, background="#f0f0f0")
        outer.grid(row=row, column=0, sticky=fill, padx=8, pady=5)
        fam = "Microsoft JhengHei UI" if sys.platform == "win32" else "TkDefaultFont"
        tk.Label(outer, text=title, font=(fam, 11, "bold"), background="#dde6f3", foreground="#1f3a68", anchor="w", padx=8, pady=4).pack(fill="x")
        body = ttk.Frame(outer, padding=8)
        body.pack(fill="both", expand=True)
        return body

    def _conn_section(self, parent, row):
        """連線方式(USB 線 / WiFi 位址),設定頁與備份頁各一份,綁同一組變數."""
        fc = self._section(parent, "連線方式", row)
        fc.columnconfigure(1, weight=1)
        ttk.Radiobutton(fc, text="USB 線(上面選的序列埠;韌體要 " + USB_API_MIN_FW + " 以上)", value="usb", variable=self.link_var,
                        command=self._save_link).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(fc, text="WiFi,板子位址:", value="wifi", variable=self.link_var, command=self._save_link).grid(row=1, column=0, sticky="w")
        he = ttk.Entry(fc, textvariable=self.host_var)
        he.grid(row=1, column=1, sticky="ew", padx=6)
        he.bind("<FocusOut>", lambda e: self._save_link())
        ttk.Label(fc, text="連家用 WiFi 用 lineplane.local(或板子的 IP);電腦連板子熱點時用 192.168.4.1", foreground="#555").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))
        return fc

    def _fit_window(self):
        """開啟時依內容需要的大小與螢幕決定視窗大小(高 DPI 下內容比固定尺寸大,板子訊息區會被擠到看不到);放不下就最大化."""
        r = self.root
        r.update_idletasks()
        sw, sh = r.winfo_screenwidth(), r.winfo_screenheight()
        need_w, need_h = r.winfo_reqwidth() + 16, r.winfo_reqheight() + 16
        # 沒顯示的分頁(設定頁有 WiFi 設定區)可能比目前這頁高:每一頁都要放得下
        shown = self.nb.frames[self.nb.cur].winfo_reqheight()
        need_h += max(0, max(f.winfo_reqheight() for f in self.nb.frames) - shown)
        w, h = min(sw - 40, max(int(880 * self.dpi), need_w)), min(sh - 90, max(620, need_h))
        r.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 2 - 20)}")
        if need_h > sh - 90 and sys.platform == "win32":
            with contextlib.suppress(Exception):
                r.state("zoomed")

    # ---------------- 共用 ----------------
    def _log(self, text, tag=None):
        self.log.insert("end", text + "\n", tag or ())
        n = int(self.log.index("end-1c").split(".")[0])
        if n > MAX_LOG_LINES:
            self.log.delete("1.0", f"{n - MAX_LOG_LINES}.0")
        if self.autoscroll.get():
            self.log.see("end")

    def _set_check(self, key, state, text):
        color = {"ok": "#1a7f37", "bad": "#cf222e", "run": "#9a6700", "warn": "#9a6700", "": "#777"}[state]
        mark = {"ok": "✔ ", "bad": "✖ ", "run": "… ", "warn": "! ", "": ""}[state]
        self.checks[key].configure(text=mark + text, foreground=color)

    def _set_busy(self, busy):
        self.busy = busy
        st = "disabled" if busy else "normal"
        for w in (self.flash_btn, self.check_btn, self.reload_btn, self.mon_btn, self.cfg_btn,
                  self.bk_out_btn, self.bk_in_btn, self.bk_flash_btn, self.wifi_read_btn, self.wifi_scan_btn, self.wifi_apply_btn,
                  self.status_btn, self.reboot_btn, self.level_btn):
            w.configure(state=st)
        self.port_cb.configure(state="disabled" if busy else "readonly")
        self.ver_cb.configure(state="disabled" if busy else "readonly")

    def _port(self):
        label = self.port_var.get()
        for dev, text, _ in self.ports:
            if text == label:
                return dev
        return None

    def _poll(self):
        try:
            while True:
                kind, val = self.q.get_nowait()
                if kind == "board":
                    self._on_board_line(val)
                elif kind == "tool":
                    self._log(val, "tool")
                elif kind == "esptool":
                    self._log(val, "err" if re.search(r"error|fatal|failed", val, re.I) else None)
                elif kind == "err":
                    self._log(val, "err")
                elif kind == "okmsg":
                    self._log(val, "ok")
                elif kind == "progress":
                    if val is None:
                        if self.prog.cget("mode") != "indeterminate":
                            self.prog.configure(mode="indeterminate")
                            self.prog.start(15)
                    else:
                        if self.prog.cget("mode") != "determinate":
                            self.prog.stop()
                            self.prog.configure(mode="determinate")
                        self.prog["value"] = val
                elif kind == "stage":
                    self.stage.configure(text=val)
                elif kind == "check":
                    self._set_check(*val)
                elif kind == "mon_state":
                    ok, msg = val
                    self.mon_state.configure(text=msg, foreground="#1a7f37" if ok else "#777")
                    self.mon_btn.configure(text="停止監看" if self.monitor.want else "開始監看")
                elif kind == "status":
                    self.status.configure(text=val)
                elif kind == "done":
                    self._set_busy(False)
                    self.mon_btn.configure(text="停止監看" if self.monitor.want else "開始監看")
                elif kind == "releases":
                    self.releases = val
                    self._fill_versions()
                elif kind == "releases_err":
                    self.notes.configure(text=f"讀不到版本清單:{val}\n請確認電腦能上網後按「重新整理」;也可以選電腦裡的檔案.", foreground="#cf222e")
                elif kind == "dialog":
                    title, msg, err = val
                    (messagebox.showerror if err else messagebox.showinfo)(title, msg, parent=self.root)
                elif kind == "ask":   # 背景執行緒要問使用者:(標題, 訊息, 結果容器[Event, 答案])
                    title, msg, box = val
                    box[1] = messagebox.askyesno(title, msg, parent=self.root)
                    box[0].set()
                elif kind == "cfg_state":
                    self.cfg_state.configure(text=val[0], foreground=val[1])
                elif kind == "bk_state":
                    self.bk_state.configure(text=val[0], foreground=val[1])
                elif kind == "wifi_state":
                    self.wifi_state.configure(text=val[0], foreground=val[1])
                elif kind == "level_state":
                    self.level_state.configure(text=val[0], foreground=val[1])
                elif kind == "att":
                    if self.att_on:
                        self._att_draw(val)
                elif kind == "att_state":
                    if self.att_on:
                        self.att_state.configure(text=val[0], foreground=val[1])
                elif kind == "att_stop":
                    self.att_on = False
                    self.att_btn.configure(text="開始即時姿態")
                    self.att_state.configure(text=val, foreground="#cf222e")
                    self._att_draw(None)
                elif kind == "att_auto":   # 水平標定成功:自動打開即時姿態讓使用者看結果
                    if not self.att_on:
                        self._att_toggle()
                elif kind == "wifi_big":   # (文字, 顏色);空字串 = 藏起來
                    if val[0]:
                        self.wifi_big.configure(text=val[0], foreground=val[1])
                        self.wifi_big.grid()
                    else:
                        self.wifi_big.grid_remove()
                elif kind == "wifi_fields":
                    self._wifi_fill(val)
                elif kind == "scan_list":
                    self._wifi_scan_fill(val)
                elif kind == "open_url":
                    webbrowser.open(val)
        except queue.Empty:
            pass
        self.root.after(50, self._poll)

    def _on_board_line(self, line):
        tag = "err" if line.startswith("ERR") and "in use" not in line else None
        shown = line if self.raw_var.get() else translate_line(line)
        if shown is not None:
            self._log(shown, tag)
        for lq in list(self.listeners):
            lq.put(line)
        if "invalid header" in line:
            self.q.put(("status", "這塊板子還沒有韌體(空白板):請選完整燒錄檔 lineplane-full-*.bin 燒錄"))

    # ---------------- 序列埠 ----------------
    def _port_loop(self):
        if not self.busy:   # 燒錄與檢查中不換序列埠(板子重開時會短暫消失)
            self._scan_ports()
        self.root.after(1500, self._port_loop)

    def _scan_ports(self, force=False):
        try:
            ports = list_ports()
        except Exception:
            ports = self.ports
        if not force and [p[:2] for p in ports] == [p[:2] for p in self.ports]:
            return
        cur = self._port()
        self.ports = ports
        self.port_cb.configure(values=[p[1] for p in ports])
        devs = [p[0] for p in ports]
        # 監看守著的埠不見了(燒完換下一片板子):停掉監看,讓自動偵測選新板子(原本監看開著就不換埠,第二片要手動選)
        if self.monitor.want and self.monitor.port not in devs and not self.busy:
            self.monitor.stop()
            self.mon_btn.configure(text="開始監看")
            self._log(f"{self.monitor.port} 已拔除,停止監看;接上下一片會自動偵測", "tool")
        if self.auto_port.get() and not self.monitor.want:
            best = [p for p in ports if p[2] == 2] or [p for p in ports if p[2] == 1]
            self.port_var.set(best[0][1] if best else "")
        elif cur is None or cur not in [p[0] for p in ports]:
            self.port_var.set("")
        else:
            self.port_var.set(next(p[1] for p in ports if p[0] == cur))
        c3 = [p for p in ports if p[2] == 2]
        if not ports:
            hint = "找不到任何序列埠:請用「可以傳資料」的 USB 線接上開發板(只能充電的線不行)."
        elif not c3:
            hint = "沒有偵測到 ESP32-C3 原生 USB 序列埠,請手動選擇. 板子沒反應時:按住 BOOT 鍵再插 USB."
        elif len(c3) > 1:
            hint = f"偵測到 {len(c3)} 片 ESP32-C3,請確認選的是要燒的那一片(只接一片最保險)."
        else:
            hint = f"已偵測到 ESP32-C3:{c3[0][0]}"
        self.port_hint.configure(text=hint)

    # ---------------- 韌體檔 ----------------
    def _browse(self):
        init = os.path.dirname(self.file_var.get()) if self.file_var.get() else os.path.expanduser("~")
        path = filedialog.askopenfilename(parent=self.root, title="選擇韌體檔", initialdir=init,
                                          filetypes=[("韌體檔", "*.bin"), ("全部檔案", "*.*")])
        if path:
            self._load_file(path)

    def _load_file(self, path, quiet=False):
        self.file_var.set(path)
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError as e:
            self.image = None
            self.file_info.configure(text=f"讀不到檔案:{e}", foreground="#cf222e")
            return
        a = fw_image.analyze(data)
        self.image = (path, data, a)
        kind = {"full": "完整燒錄檔(從 0x0 燒整片,設定會回出廠值)",
                "app": "韌體更新檔(燒在 0x10000,設定保留)", "bad": "無法使用"}[a["kind"]]
        lines = [f"類型:{kind}",
                 f"版本:{a['version'] or '不明'}   板子種類:{fw_image.board_name(a['board']) if a['board'] else '不明'}   大小:{len(data):,} 位元組"]
        lines += ["✖ " + p for p in a["problems"]]
        lines += ["! " + w for w in a["warnings"]]
        self.file_info.configure(text="\n".join(lines), foreground="#cf222e" if a["problems"] else ("#9a6700" if a["warnings"] else "#1a7f37"))
        # 自己選的檔案決定燒錄方式:完整燒錄檔 = 全新燒錄,韌體更新檔 = 更新
        if a["kind"] in ("full", "app"):
            self.mode_var.set("new" if a["kind"] == "full" else "keep")
            self._mode_changed()
        if not quiet:
            self._log(f"選擇韌體檔:{path}({kind},版本 {a['version'] or '不明'})", "tool")

    def _mode_changed(self):
        keep = self.mode_var.get() == "keep"
        self.mode_hint.configure(text=("只換程式,板上設定(飛行參數,WiFi)完全不動. 燒錄前仍會自動備份一份存檔當保險."
                                       if keep else "整片重寫,板上設定全部回出廠值. 燒錄前會自動備份板上設定存成檔案(不會自動寫回;要的話到「備份」頁匯入). 全新空白板子用這個."))
        self.erase_cb.configure(state="normal" if not keep else "disabled")
        self._show_notes()

    def _version_changed(self):
        self._show_notes()

    def _toggle_adv(self):
        if self.adv.winfo_viewable():
            self.adv.grid_remove()
            self.adv_btn.configure(text="進階 ▸")
        else:
            self.adv.grid()
            self.adv_btn.configure(text="進階 ▾")

    def _clear_file(self):
        self.image = None
        self.file_var.set("")
        self.file_info.configure(text="沒有指定檔案:按「開始燒錄」會依上面選的版本與方式自動下載.", foreground="#555")

    def _load_releases(self):
        self.notes.configure(text="讀取版本清單中 …", foreground="#555")

        def job():
            try:
                self.q.put(("releases", fw_image.list_releases()))
            except Exception as e:
                self.q.put(("releases_err", str(e)))

        threading.Thread(target=job, daemon=True).start()

    def _fill_versions(self):
        """列出有韌體檔的版本."""
        board = self.board_var.get()
        old = self._selected_release()
        self.shown = [r for r in self.releases if fw_image.release_offers(r, board)[1] or fw_image.release_offers(r, board)[0]]
        labels = []
        for r in self.shown:
            tags = [t for t in ("最新" if r["latest"] else "", r["date"]) if t]
            labels.append(r["version"] + (f"({','.join(tags)})" if tags else ""))
        self.ver_cb.configure(values=labels)
        keep = [i for i, r in enumerate(self.shown) if old and r["version"] == old["version"]]
        if labels:
            self.ver_cb.current(keep[0] if keep else 0)
        else:
            self.ver_var.set("")
        self._show_notes()

    def _selected_release(self):
        i = self.ver_cb.current()
        return self.shown[i] if 0 <= i < len(self.shown) else None

    def _show_notes(self):
        r = self._selected_release()
        if not r:
            if self.releases:
                self.notes.configure(text=f"沒有{fw_image.board_name(self.board_var.get())}可以下載的版本", foreground="#cf222e")
            return
        board = self.board_var.get()
        has_full, has_app = fw_image.release_offers(r, board)
        body = r["notes"].split("\n---")[0].strip()   # Release 說明後段是「怎麼更新」的固定文字
        body = re.sub(r"\*\*(.+?)\*\*", r"\1", body)   # Markdown 粗體符號拿掉(這裡是純文字)
        lines = [x.strip() for x in body.splitlines() if x.strip()]
        text = "\n".join(lines[:5]) + (" …" if len(lines) > 5 else "")
        if len(text) > 400:
            text = text[:400] + " …"
        extra = []
        if self.mode_var.get() == "keep":
            if not has_app:
                extra.append("! 這版不能用「更新」方式,請選全新燒錄")
            elif not r["latest"]:
                extra.append("! 換成較舊的版本時,新版存的設定舊版可能讀不懂而回出廠值")
        elif not has_full:
            extra.append("")
        self.notes.configure(text="\n".join([text or "(這版沒有說明)"] + extra),
                             foreground="#9a6700" if any(x.startswith("!") for x in extra) else "#333")

    def _download_image(self, rel, keep):
        """在背景執行緒下載這版對應的檔案(keep → 韌體更新檔,否則完整燒錄檔),存到 LOCALAPPDATA. 回 (路徑, 內容, 分析結果);失敗丟例外."""
        q = self.q
        ver = rel["version"]
        q.put(("stage", f"下載 {ver} …"))

        def prog(got, total):
            q.put(("progress", got * 100 / total if total else None))

        name, data = fw_image.download_version(rel, self.board_var.get(), keep, self.releases, progress=prog,
                                                log=lambda m: q.put(("tool", m)))
        path = os.path.join(data_dir(), "firmware", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        q.put(("okmsg", f"已下載並驗證 {name}({len(data):,} 位元組,檢查碼正確)"))
        q.put(("progress", 0))
        return path, data, fw_image.analyze(data)

    # ---------------- 燒錄 ----------------
    def _start_flash(self):
        """一鍵:確認 → (背景)下載對應檔案 → 偵測板子 → 自動備份 → 燒錄 → 檢查."""
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請先接上開發板,選擇序列埠.", parent=self.root)
            return
        keep = self.mode_var.get() == "keep"
        manual = self.image if (self.image and self.file_var.get().strip() == self.image[0]) else None
        rel = self._selected_release()
        if manual:
            _, _, a = manual
            if a["problems"]:
                messagebox.showerror("這個檔案不能燒", "\n".join(a["problems"]), parent=self.root)
                return
            src = f"檔案:{os.path.basename(manual[0])}(版本 {a['version'] or '不明'})"
        elif rel:
            if keep and not fw_image.release_offers(rel, self.board_var.get())[1]:
                messagebox.showerror("這版不能用更新方式", "這個版本沒有更新用的檔案,請改選「全新燒錄」.", parent=self.root)
                return
            src = f"版本:{rel['version']}(按確定後自動下載)"
        else:
            messagebox.showwarning("沒有版本", "版本清單還沒讀到:請確認電腦能上網後按「重新整理」,或在「進階」選電腦裡的檔案.", parent=self.root)
            return
        what = ("更新:只換程式,板上設定完全不動. 燒錄前會自動備份一份設定存檔." if keep else
                "全新燒錄:" + ("先清除整片再" if self.erase_var.get() else "") + "整片重寫,板上設定全部回出廠值.\n燒錄前會自動備份板上設定存成檔案(不會自動寫回).")
        if not messagebox.askokcancel("開始燒錄", f"序列埠:{port}\n{src}\n\n{what}\n\n請確認已拆下螺旋槳. 確定開始燒錄?", parent=self.root, icon="warning"):
            return
        self._set_busy(True)
        self.stage.configure(text="準備中 …")
        for k in self.checks:
            self._set_check(k, "", "—")
        threading.Thread(target=self._prepare_then_flash, args=(port, keep, manual, rel), daemon=True).start()

    def _board_alive(self, port):
        """板子有沒有在跑線控飛機韌體:先試 USB 設定通道,再試文字指令 fw. 回 ('api'|'text'|None, 版本或 None)."""
        if not self._usb_monitor_on(port, 3.0):
            return None, None
        fw = board_link.probe(self.monitor.bridge, 2.0)
        if fw:
            return "api", fw.get("ver")
        lq = queue.Queue()
        self.listeners.append(lq)
        try:
            end = time.time() + 3.0
            nxt = 0
            while time.time() < end:
                if time.time() >= nxt:
                    self.monitor.send("fw")
                    nxt = time.time() + 1.0
                try:
                    line = lq.get(timeout=0.1)
                except queue.Empty:
                    continue
                m = re.match(r"version=(\S+)", line)
                if m:
                    return "text", m.group(1)
        finally:
            with contextlib.suppress(ValueError):
                self.listeners.remove(lq)
        return None, None

    def _prepare_then_flash(self, port, keep, manual, rel):
        """背景:偵測板子(空白板子選更新 → 問要不要改全新燒錄)→ 下載檔案 → 自動備份 → 交回主執行緒燒錄."""
        q = self.q
        try:
            q.put(("stage", "偵測板子 …"))
            link, ver = self._board_alive(port)
            if keep and not link:
                if manual:
                    raise board_link.BoardError("板子沒有回應(可能是空白板子),不能用更新方式燒這個檔案. 請到 Releases 下載完整燒錄檔(lineplane-full-*.bin)或改用自動下載.")
                if not self._ask("板子沒有回應", "板子沒有回應,可能是全新的空白板子(或不是線控飛機韌體).\n\n"
                                 "空白板子不能用「更新」方式. 要改用「全新燒錄」(整片重寫,設定為出廠值)嗎?"):
                    raise board_link.BoardError("已取消")
                keep = False
                self.root.after(0, lambda: (self.mode_var.set("new"), self._mode_changed()))
                q.put(("tool", "板子沒有回應:改用全新燒錄"))
            if link == "api":
                # 兩種方式都先備份一份存檔(更新方式設定不會動,只是保險;全新燒錄會清掉,靠這份手動匯入)
                q.put(("stage", "燒錄前先備份板上設定 …"))
                try:
                    code, fw = board_link.backup_export(self.monitor.bridge, log=lambda m: q.put(("tool", m)),
                                                        ask_save=lambda: self._ask("板上有未儲存的變更", "板上有還沒儲存的設定變更,備份碼只能從已儲存的設定產生.\n\n要先儲存板上的變更再備份嗎?"))
                    d = os.path.join(data_dir(), "backups")
                    os.makedirs(d, exist_ok=True)
                    path = os.path.join(d, time.strftime("lineplane_backup_%Y%m%d_%H%M%S.txt"))
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(board_link.backup_file_text(code, fw, f"USB {port}(燒錄前自動備份)"))
                    q.put(("okmsg", f"燒錄前已自動備份板上設定:{path}"))
                    q.put(("bk_state", (f"燒錄前自動備份:{path}", "#1a7f37")))
                except (board_link.BoardError, OSError, ValueError) as e:
                    q.put(("err", f"燒錄前自動備份失敗:{e}"))
                    if not keep and not self._ask("自動備份失敗", f"{e}\n\n全新燒錄會清掉板上設定. 不備份直接燒嗎?"):
                        raise board_link.BoardError("已取消")
            elif link == "text" and not keep:
                q.put(("tool", f"板子韌體 {ver} 沒有 USB 設定通道,無法自動備份(要備份請先用 WiFi 開網頁的備份頁)"))
                if not self._ask("無法自動備份", f"板子韌體 {ver} 太舊,無法透過 USB 備份設定.\n全新燒錄會清掉板上設定. 直接燒嗎?"):
                    raise board_link.BoardError("已取消")
            if manual:
                path, data, a = manual
            else:
                path, data, a = self._download_image(rel, keep)
                if a["problems"]:
                    raise board_link.BoardError("下載的檔案檢查不通過:" + ";".join(a["problems"]))
            if keep and a["kind"] != "app" or not keep and a["kind"] != "full":
                raise board_link.BoardError("檔案種類和燒錄方式不符(程式錯誤,請回報)")
            self.root.after(0, lambda: self._start_flash_go(port, data, a))
        except Exception as e:
            q.put(("err", f"沒有燒錄:{e}"))
            q.put(("stage", "已取消" if str(e) == "已取消" else "沒有燒錄"))
            q.put(("progress", 0))
            if str(e) != "已取消":
                q.put(("dialog", ("沒有燒錄", str(e), True)))
            q.put(("done", None))

    def _start_flash_go(self, port, data, a):
        self.monitor.stop()   # esptool 要用這個序列埠
        for k in self.checks:
            self._set_check(k, "", "—")
        self._set_busy(True)
        self.prog["value"] = 0
        threading.Thread(target=self._flash_job, args=(port, data, a, self.erase_var.get() and a["kind"] == "full", self.auto_check.get()),
                         daemon=True).start()

    def _flash_job(self, port, data, a, erase, check_after):
        q = self.q
        tmpdir = tempfile.mkdtemp(prefix="lpflash-")
        try:
            if a["kind"] == "full":
                parts = [(0x0, data)]
            else:
                parts = [(fw_image.OTADATA_OFFSET, fw_image.boot_app0()), (fw_image.APP_OFFSET, data)]
            files = []
            for addr, blob in parts:
                p = os.path.join(tmpdir, f"part_{addr:06x}.bin")
                with open(p, "wb") as f:
                    f.write(blob)
                files += [hex(addr), p]
            sizes = [len(b) for _, b in parts]   # esptool 依位址由小到大寫,parts 已照順序
            args = ["--chip", "esp32c3", "--port", port, "--baud", str(BAUD_FLASH), "--before", "default_reset",
                    "--after", "hard_reset", "write_flash", "-z", "--flash_mode", "keep", "--flash_freq", "keep",
                    "--flash_size", "keep"]
            if erase:
                args.append("--erase-all")
            args += files
            state = {"idx": 0, "verified": 0, "chip": None}

            def on_line(line):
                q.put(("esptool", line))
                m = re.search(r"Writing at 0x[0-9a-f]+\.\.\. \((\d+) ?%\)", line)
                if m:
                    i = min(state["idx"], len(sizes) - 1)
                    done = sum(sizes[:i]) + int(m.group(1)) / 100 * sizes[i]
                    q.put(("progress", done * 100 / sum(sizes)))
                    q.put(("stage", f"寫入中 {done * 100 / sum(sizes):.0f}%"))
                elif line.startswith("Chip is "):
                    state["chip"] = line[8:]
                    ok = "ESP32-C3" in line
                    q.put(("check", ("chip", "ok" if ok else "bad", line[8:])))
                elif line.startswith("Connecting"):
                    q.put(("stage", "連線到板子 …"))
                elif line.startswith("Erasing flash (this"):   # --erase-all 清除整片
                    q.put(("stage", "清除整片中(約 10~30 秒)…"))
                    q.put(("progress", None))
                elif line.startswith("Wrote "):
                    state["idx"] += 1
                elif line.startswith("Hash of data verified"):
                    state["verified"] += 1
                elif line.startswith("Hard resetting"):
                    q.put(("stage", "重新開機 …"))

            q.put(("tool", f"開始燒錄:{port},{'先清除整片,' if erase else ''}共 {sum(sizes):,} 位元組"))
            q.put(("stage", "連線到板子 …"))
            q.put(("check", ("chip", "run", "連線中")))
            err = self._run_esptool(args, on_line)
            if err:
                q.put(("progress", 0))
                q.put(("stage", "燒錄失敗"))
                if not state["chip"]:
                    q.put(("check", ("chip", "bad", "連不上")))
                q.put(("check", ("verify", "bad", "沒有完成")))
                fe = friendly_error(err)
                q.put(("esptool", err))
                q.put(("err", "燒錄失敗:" + fe))
                q.put(("dialog", ("燒錄失敗", fe, True)))
                return
            if state["verified"] == len(parts):
                q.put(("check", ("verify", "ok", f"{len(parts)} 段資料檢查碼全部相符")))
            else:
                q.put(("check", ("verify", "warn", f"esptool 只回報 {state['verified']}/{len(parts)} 段校驗")))
            q.put(("progress", 100))
            q.put(("okmsg", "燒錄完成,板子重新開機中."))
            q.put(("stage", "燒錄完成"))
            if check_after:
                self._check_job(port, a.get("version"), after_flash=True)
            else:
                q.put(("dialog", ("燒錄完成", "燒錄完成,板子已重新開機.", False)))
        finally:
            with contextlib.suppress(Exception):
                for f in os.listdir(tmpdir):
                    os.remove(os.path.join(tmpdir, f))
                os.rmdir(tmpdir)
            q.put(("done", None))

    def _run_esptool(self, args, on_line):
        """在這個執行緒呼叫 esptool.main;回錯誤訊息(成功回 None). esptool 的輸出用 print,暫時接到 on_line."""
        import esptool
        w = _LineWriter(on_line)
        try:
            with contextlib.redirect_stdout(w), contextlib.redirect_stderr(w):
                esptool.main(args)
            return None
        except SystemExit as e:
            return None if not e.code else f"esptool 結束代碼 {e.code}"
        except Exception as e:
            return f"{e.__class__.__name__}: {e}"
        finally:
            w.write("\n")

    # ---------------- 檢查 ----------------
    def _start_check_only(self):
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請先接上開發板,選擇序列埠.", parent=self.root)
            return
        expect = self.image[2].get("version") if self.image else None
        for k in ("boot", "mpu", "wifi"):
            self._set_check(k, "", "—")
        self._set_busy(True)

        def job():
            try:
                self._check_job(port, expect, after_flash=False)
            finally:
                self.q.put(("done", None))

        threading.Thread(target=job, daemon=True).start()

    def _check_job(self, port, expect_ver, after_flash):
        """開監看,送 fw / mpu / net,看板子回報. 在背景執行緒跑."""
        q = self.q
        lq = queue.Queue()
        self.listeners.append(lq)
        try:
            q.put(("stage", "等待板子開機 …" if after_flash else "檢查中 …"))
            q.put(("check", ("boot", "run", "等待板子回應")))
            if after_flash:
                time.sleep(1.5)   # 重開後原生 USB 重新列舉
            if not (self.monitor.want and self.monitor.port == port):
                self.monitor.start(port)
            t0 = time.time()
            while not self.monitor.connected() and time.time() - t0 < 10:
                time.sleep(0.1)
            if not self.monitor.connected():
                q.put(("check", ("boot", "bad", f"打不開 {port}")))
                q.put(("dialog", ("檢查失敗", f"重新開機後打不開 {port}. 拔掉 USB 再接上,按「只做檢查」.", True)))
                return

            def ask(cmd, pred, timeout, retry=1.5):
                """送指令直到收到符合 pred 的一行(回該行),逾時回 None. 開機中送的指令可能被丟掉,所以重送."""
                end = time.time() + timeout
                nxt = 0
                while time.time() < end:
                    if time.time() >= nxt:
                        self.monitor.send(cmd)
                        q.put(("tool", f"> {CMD_NAMES.get(cmd, cmd)}({cmd})"))
                        nxt = time.time() + retry
                    try:
                        line = lq.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    if pred(line):
                        return line
                return None

            boot_seen = []

            def fw_pred(line):
                if line.startswith("board ") or "invalid header" in line:
                    boot_seen.append(line)
                return line.startswith("version=")

            line = ask("fw", fw_pred, 12 if after_flash else 6)
            if not line:
                if any("invalid header" in b for b in boot_seen):
                    msg = "板子沒有可開機的韌體(invalid header):全新板子要用完整燒錄檔 lineplane-full-*.bin"
                else:
                    msg = "板子沒有回應 fw 指令:可能不是線控飛機韌體,或板子沒開機. 試試拔掉 USB 再接上,再按「只做檢查」"
                q.put(("check", ("boot", "bad", msg)))
                q.put(("dialog", ("檢查失敗", msg, True)))
                return
            m = re.match(r"version=(\S+)", line)
            ver = m.group(1) if m else "?"
            pend = re.search(r"pending=(\d)", line)
            board = next((b[6:].split(",")[0] for b in boot_seen if b.startswith("board ")), None)
            extra = f",板子 {board}" if board else ""
            if expect_ver and ver != expect_ver:
                q.put(("check", ("boot", "bad", f"板子回報 {ver},和檔案 {expect_ver} 不同{extra}")))
            else:
                q.put(("check", ("boot", "ok", f"已開機,韌體 {ver}{extra}" + (",待確認(開網頁會自動確認)" if pend and pend.group(1) == "1" else ""))))

            fails = [("韌體版本", not (expect_ver and ver != expect_ver))]
            line = ask("mpu", lambda s: "MPU" in s, 5)
            if line is None:
                q.put(("check", ("mpu", "warn", "沒有回應")))
            elif "in use" in line or line.startswith("MPU OK"):
                q.put(("check", ("mpu", "ok", "有連線")))
            else:
                q.put(("check", ("mpu", "bad", "找不到:檢查 SDA→GPIO5,SCL→GPIO6,VCC,GND 接線")))
                fails.append(("感測器", False))

            # WiFi:開機後先掃描再連家用 WiFi,要 5~30 秒;只問一次會停在「連線中」(GG 2026-11-03 更新後以為沒連上). 問到不是連線中為止,最多 45 秒.
            q.put(("stage", "等待 WiFi 連線 …"))
            kv, t_net = None, time.time()
            while time.time() - t_net < 45:
                line = ask("net", lambda s: s.startswith("wifi="), 5)
                kv = parse_net(line) if line else None
                if not kv or kv["wifi"] != "connecting":
                    break
                q.put(("check", ("wifi", "run", f"正在連「{kv['ssid']}」…(已 {time.time() - t_net:.0f} 秒;連不上會自動改開熱點)")))
                time.sleep(1)
            if kv is None:
                wifi_msg = "沒有回應"
                q.put(("check", ("wifi", "warn", wifi_msg)))
            elif kv["wifi"] == "sta":
                wifi_msg = f"已連上「{kv['ssid']}」,IP {kv['ip']}:手機(同一個網路)開 http://{kv['ip']},iPhone 與電腦也可以開 http://{kv['host']}"
                q.put(("check", ("wifi", "ok", wifi_msg)))
            elif kv["wifi"] == "ap" and kv["ssid"]:
                wifi_msg = f"設定了「{kv['ssid']}」但沒連上,板子改開自己的熱點(手機連板子熱點後開 http://{kv['ip']}). 密碼或 2.4GHz 請到「設定」頁 WiFi 設定重試"
                q.put(("check", ("wifi", "warn", wifi_msg)))
            elif kv["wifi"] == "ap":
                wifi_msg = f"板子自己開熱點:手機連板子的 WiFi 後開 http://{kv['ip']}"
                q.put(("check", ("wifi", "ok", wifi_msg)))
            else:
                wifi_msg = "等了 45 秒還在連線中,請稍後按「板子狀態」看結果"
                q.put(("check", ("wifi", "warn", wifi_msg)))
            restored = ""
            bad = [n for n, ok in fails if not ok]
            q.put(("stage", "檢查完成" if not bad else "檢查完成,有項目沒通過"))
            q.put(("okmsg", "檢查完成. 序列監看保持開著,可以繼續看板子回報的訊息."))
            if after_flash and not bad:
                q.put(("dialog", ("完成", f"燒錄與檢查完成,板子韌體 {ver}.{restored}\n\nWiFi:{wifi_msg}\n\n"
                                  "也可以到「設定」頁按「開啟設定網頁」用 USB 線設定.\n詳細步驟見專案 README 與使用說明書.", False)))
            elif after_flash:
                q.put(("dialog", ("燒錄完成,檢查有問題", f"燒錄完成,板子韌體 {ver},但這些項目沒通過:{','.join(bad)}.\n請看「燒錄與檢查」的說明.", True)))
        finally:
            with contextlib.suppress(ValueError):
                self.listeners.remove(lq)
            q.put(("mon_state", (self.monitor.connected(), f"已連線 {port}" if self.monitor.connected() else "未連線")))

    # ---------------- 設定網頁與備份 ----------------
    def _save_link(self):
        self.prefs["link"] = self.link_var.get()
        self.prefs["host"] = self.host_var.get().strip()
        self.prefs["raw"] = bool(self.raw_var.get())
        save_prefs(self.prefs)

    def _save_tab(self):
        self.prefs["tab"] = ["flash", "cfg", "bk"][self.nb.index(self.nb.select())]
        save_prefs(self.prefs)
        # 切到設定頁時順手把板上 WiFi 設定讀進來(有板子,沒在忙,而且還沒讀過)
        if self.prefs["tab"] == "cfg" and not self.busy and self._port() and not getattr(self, "wifi_loaded", False):
            self._wifi_read(quiet=True)

    def _usb_monitor_on(self, port, timeout=4.0):
        """確保監看開在這個序列埠並已連線(USB 設定通道掛在監看的讀取執行緒上). 可在背景執行緒呼叫."""
        if not (self.monitor.want and self.monitor.port == port):
            self.monitor.start(port)
            self.q.put(("mon_state", (False, f"連線 {port} …")))
        return self.monitor.wait_connected(timeout)

    def _usb_probe(self, port, timeout=2.0):
        """板子透過 USB 有沒有網頁 API. 回 /api/fw dict 或 None. 主執行緒呼叫(會等最多幾秒)."""
        if not self._usb_monitor_on(port, 3.0):
            return None
        return board_link.probe(self.monitor.bridge, timeout)

    def _board(self):
        """依連線方式回 (板子物件, 來源說明);USB 沒連上或沒有 API 時丟 BoardError. 可在背景執行緒呼叫."""
        if self.link_var.get() == "wifi":
            host = self.host_var.get().strip() or "lineplane.local"
            return board_link.HttpBoard(host), f"WiFi {host}"
        port = self._port()
        if not port:
            raise board_link.BoardError("沒有序列埠:請接上開發板,或改用 WiFi")
        if not self._usb_monitor_on(port):
            raise board_link.BoardError(f"打不開 {port}")
        if not board_link.probe(self.monitor.bridge, 2.5):
            raise board_link.BoardError(f"板子沒有回應 USB 設定通道:韌體要 {USB_API_MIN_FW} 以上,請先到「燒錄」頁更新(勾「保留板上設定」);或改用 WiFi")
        return self.monitor.bridge, f"USB {port}"

    def _ask(self, title, msg):
        """背景執行緒問使用者是/否."""
        box = [threading.Event(), False]
        self.q.put(("ask", (title, msg, box)))
        box[0].wait()
        return box[1]

    def _open_config(self):
        self._save_link()
        if self.link_var.get() == "wifi":
            host = self.host_var.get().strip() or "lineplane.local"
            url = "http://" + host + "/"
            self.cfg_state.configure(text=f"已用瀏覽器開 {url}(電腦要和板子在同一個 WiFi,或連板子的熱點)", foreground="#1a7f37")
            self._log(f"開設定網頁(WiFi):{url}", "tool")
            webbrowser.open(url)
            return
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請先接上開發板,選擇序列埠;或改用 WiFi.", parent=self.root)
            return
        self._set_busy(True)
        self.cfg_state.configure(text=f"連線 {port} …", foreground="#9a6700")

        def job():
            try:
                fw = None
                if self._usb_monitor_on(port):
                    fw = board_link.probe(self.monitor.bridge, 2.5)
                if not fw:
                    msg = (f"板子沒有回應 USB 設定通道.\n\n可能是韌體太舊(要 {USB_API_MIN_FW} 以上):請到「燒錄」頁選最新版,勾「保留板上設定」更新;"
                           "\n或板子沒開機 / 不是線控飛機韌體. 也可以改用 WiFi.")
                    self.q.put(("cfg_state", (msg, "#cf222e")))
                    self.q.put(("dialog", ("連不到板子", msg, True)))
                    return
                url = self.proxy.start()
                self.proxy.page()   # 先把網頁抓好(第一次約 230KB),瀏覽器開起來就有東西
                self.q.put(("cfg_state", (f"設定網頁已開在瀏覽器:{url}(板子韌體 {fw.get('ver')},{fw_image.board_name(fw.get('board'))})\n"
                                          "關掉這個程式或拔掉 USB 線,網頁就會斷線;重新整理網頁即可再連.", "#1a7f37")))
                self.q.put(("tool", f"開設定網頁(USB {port}):{url}"))
                self.q.put(("open_url", url))
            except board_link.BoardError as e:
                self.q.put(("cfg_state", (f"失敗:{e}", "#cf222e")))
                self.q.put(("dialog", ("開設定網頁失敗", str(e), True)))
            finally:
                self.q.put(("done", None))

        threading.Thread(target=job, daemon=True).start()

    def _backup_export(self, then=None):
        """匯出板上全部設定成檔案. then:成功後在主執行緒接著做的事(燒錄前備份用)."""
        self._save_link()
        path = filedialog.asksaveasfilename(parent=self.root, title="匯出板上設定備份", defaultextension=".txt",
                                            initialfile=time.strftime("lineplane_backup_%Y%m%d_%H%M%S.txt"),
                                            filetypes=[("設定備份", "*.txt")])
        if not path:
            return
        self._set_busy(True)
        self.bk_state.configure(text="讀取板上設定 …", foreground="#9a6700")

        def job():
            ok = False
            try:
                board, src = self._board()
                code, fw = board_link.backup_export(board, log=lambda m: self.q.put(("tool", m)),
                                                    ask_save=lambda: self._ask("板上有未儲存的變更", "板上有還沒儲存的設定變更,備份碼只能從已儲存的設定產生.\n\n要先儲存板上的變更再備份嗎?"))
                with open(path, "w", encoding="utf-8") as f:
                    f.write(board_link.backup_file_text(code, fw, src))
                msg = f"已匯出到 {path}(韌體 {fw.get('ver', '?')},{src})"
                self.q.put(("bk_state", (msg, "#1a7f37")))
                self.q.put(("okmsg", msg))
                ok = True
            except (board_link.BoardError, OSError, ValueError) as e:
                self.q.put(("bk_state", (f"匯出失敗:{e}", "#cf222e")))
                self.q.put(("err", f"匯出備份失敗:{e}"))
                self.q.put(("dialog", ("匯出備份失敗", str(e), True)))
            finally:
                self.q.put(("done", None))
                if ok and then:
                    self.root.after(0, then)

        threading.Thread(target=job, daemon=True).start()

    def _backup_import(self):
        self._save_link()
        path = filedialog.askopenfilename(parent=self.root, title="選擇設定備份檔", filetypes=[("設定備份", "*.txt"), ("全部檔案", "*.*")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8-sig") as f:
                code = board_link.backup_file_code(f.read())
        except (OSError, board_link.BoardError) as e:
            messagebox.showerror("讀不到備份", str(e), parent=self.root)
            return
        self._set_busy(True)
        self.bk_state.configure(text="檢查備份碼 …", foreground="#9a6700")

        def job():
            try:
                board, src = self._board()
                r = board_link.backup_check(board, code)
                if not r.get("ok"):
                    raise board_link.BoardError("板子不接受這個備份碼:" + str(r.get("code")) +
                                                (" (板上有未儲存的變更,請先在網頁儲存或放棄)" if r.get("code") == "bkdirty" else ""))
                names = [n for n in r.get("names", []) if n]
                secs = [n for bit, n in ((1, "起飛降落與安全"), (2, "安裝"), (4, "電變"), (8, "WiFi")) if int(r.get("sec", 0)) & bit]
                mask = int(r.get("mask", 0))
                profs = [f"第 {i + 1} 組" for i in range(6) if mask & (1 << i)]
                msg = (f"備份碼檢查通過(來源 {os.path.basename(path)}).\n\n飛行風格:{','.join(profs) or '無'}"
                       f"{'(' + ','.join(names) + ')' if names else ''}\n其他設定:{','.join(secs) or '無'}\n"
                       + ("\n注意:這份備份來自比板子新的韌體,部分項目可能被限制在板子的範圍內.\n" if r.get("newer") else "")
                       + f"\n套用到 {src} 的板子並儲存?板上同名項目會被覆蓋.")
                if not self._ask("匯入備份", msg):
                    self.q.put(("bk_state", ("已取消匯入", "#555")))
                    return
                ra, _ = board_link.backup_apply(board, code)
                note = " WiFi 設定已存成試用,重新開機後 3 分鐘內要在網頁按「保持」." if ra.get("wifisaved") else ""
                clamp = ra.get("clamp") or []
                if clamp:
                    note += f" 有 {len(clamp)} 項被限制在板子允許的範圍."
                self.q.put(("bk_state", (f"已套用並儲存({src}).{note}", "#1a7f37")))
                self.q.put(("okmsg", f"備份已匯入並儲存.{note}"))
                self.q.put(("dialog", ("匯入完成", f"設定已套用並儲存到板子.{note}", False)))
            except (board_link.BoardError, ValueError) as e:
                self.q.put(("bk_state", (f"匯入失敗:{e}", "#cf222e")))
                self.q.put(("err", f"匯入備份失敗:{e}"))
                self.q.put(("dialog", ("匯入備份失敗", str(e), True)))
            finally:
                self.q.put(("done", None))

        threading.Thread(target=job, daemon=True).start()

    # ---------------- 水平標定(GG 2026-11-03) ----------------
    def _level_calib(self):
        """確認飛機擺平 → 板子把當下當成水平(填角度修正與滾轉修正,不存檔)→ 顯示結果 → 問要不要儲存."""
        self._save_link()
        if not messagebox.askokcancel("水平標定", "請把飛機擺成平飛姿勢(用你平常調機的水平基準),放穩不要碰.\n\n按「確定」後板子會把現在的姿勢當成水平.",
                                      parent=self.root):
            return
        self._set_busy(True)
        self.level_state.configure(text="連線板子,讀取姿勢 …", foreground="#9a6700")

        def job():
            try:
                board, src = self._board()
                r = board_link.level_set(board)
                pt, rt = float(r.get("pt", 0)), float(r.get("rt", 0))
                msg = f"標定完成({src}):角度修正 {pt:+.1f}°,滾轉修正 {rt:+.1f}°."
                self.q.put(("tool", msg))
                if self._ask("儲存到板子?", msg + "\n\n要儲存到板子嗎?\n不儲存的話,板子重新開機就回到原本的值(也可以先開設定網頁看讀值再儲存)."):
                    board_link.save_settings(board)
                    self.q.put(("level_state", (msg + " 已儲存.", "#1a7f37")))
                    self.q.put(("okmsg", "水平標定已儲存."))
                else:
                    self.q.put(("level_state", (msg + " 還沒儲存:到設定網頁按儲存,或重新開機放棄.", "#9a6700")))
                self.q.put(("att_auto", None))
            except board_link.BoardError as e:
                self.q.put(("level_state", (f"水平標定失敗:{e}", "#cf222e")))
                self.q.put(("err", f"水平標定失敗:{e}"))
                self.q.put(("dialog", ("水平標定失敗", str(e), True)))
            finally:
                self.q.put(("done", None))

        threading.Thread(target=job, daemon=True).start()

    # ---------------- 即時姿態(GG 2026-11-04) ----------------
    AXES = ["晶片 +X", "晶片 −X", "晶片 +Y", "晶片 −Y", "晶片 +Z", "晶片 −Z"]   # 與 web_page.h 的 AXES 相同

    def _att_toggle(self):
        if self.att_on:
            self.att_on = False
            self.att_btn.configure(text="開始即時姿態")
            self.att_state.configure(text="已停止即時姿態.", foreground="#555")
            return
        self._save_link()
        self.att_on = True
        self.att_gen += 1
        self.att_btn.configure(text="停止即時姿態")
        self.att_state.configure(text="連線板子 …", foreground="#9a6700")
        threading.Thread(target=self._att_job, args=(self.att_gen,), daemon=True).start()

    def _att_job(self, gen):
        """背景:每 0.2 秒讀一次狀態. 燒錄,檢查,標定等工作進行中(busy)暫停,之後重新連線;連續 3 次失敗就停."""
        board, sh, fails = None, {}, 0
        while self.att_on and self.att_gen == gen:
            if self.busy:
                board = None
                time.sleep(0.3)
                continue
            try:
                if board is None:
                    board, src = self._board()
                    sh = board_link.get_settings(board).get("shared") or {}
                    self.q.put(("att_state", (f"即時姿態({src}),每秒更新 5 次. 抬機頭/抬左翼,看圖有沒有跟著動.", "#1a7f37")))
                    n = 0
                s = board_link.get_status(board)
                n += 1
                if n % 25 == 0:   # 每 5 秒重讀一次設定(使用者可能在網頁改了安裝方位或修正值)
                    sh = board_link.get_settings(board).get("shared") or sh
                s["_sh"] = sh
                self.q.put(("att", s))
                fails = 0
                time.sleep(0.2)
            except (board_link.BoardError, ValueError, KeyError, TypeError) as e:
                board = None
                fails += 1
                if fails >= 3:
                    if self.att_gen == gen:
                        self.q.put(("att_stop", f"讀不到板子的姿態,已停止:{e}"))
                    return
                time.sleep(1.0)

    def _att_pts(self, pts, ang):
        """圖上座標(和網頁 SVG 一樣:寬 320 高 200,原點在中心,y 朝下)旋轉 ang 度後換成畫布座標."""
        k = self.att_cw / 320.0
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        out = []
        for x, y in pts:
            out += [self.att_cw / 2 + (x * c - y * s) * k, self.att_ch / 2 + (x * s + y * c) * k]
        return out

    def _att_circle(self, cv, x, y, r, ang, **kw):
        k = self.att_cw / 320.0
        cx, cy = self._att_pts([(x, y)], ang)
        cv.create_oval(cx - r * k, cy - r * k, cx + r * k, cy + r * k, **kw)

    def _att_draw(self, s):
        ok = bool(s) and s.get("imu") == 1
        P = float(s.get("p", 0)) if ok else 0.0
        R = float(s.get("r", 0)) if ok else 0.0
        k = self.att_cw / 320.0
        small = (self.att_font, 9)
        bold = (self.att_font, 11, "bold")
        body_col = "#3d5a80" if ok else "#a7b0bc"

        # 側視(和網頁同一套):站在圓心看,左翼朝你,機頭在左;倒飛時機頭換邊且上下顛倒
        cv = self.att_side
        cv.delete("all")
        cv.create_line(0, self.att_ch / 2, self.att_cw, self.att_ch / 2, fill="#9aa4b2", dash=(4, 3))
        ang = (180 - P) if (ok and abs(R) > 90) else P
        cv.create_polygon(self._att_pts([(68, -4), (90, -30), (100, -30), (97, -3)], ang), fill=body_col, outline="")
        cv.create_polygon(self._att_pts([(-92, 0), (-90, -7), (-84, -9.5), (-72, -10), (58, -5), (96, -3), (96, 3), (58, 5),
                                         (-72, 10), (-84, 9.5), (-90, 7)], ang), fill=body_col, outline="")
        cv.create_polygon(self._att_pts([(-97, -28), (-94, -28), (-94, 28), (-97, 28)], ang), fill="#555", outline="")
        cv.create_line(*self._att_pts([(-44, 9), (-54, 30)], ang), fill=body_col, width=max(2, 3 * k))
        self._att_circle(cv, -54, 32, 6, ang, fill=body_col, outline="")
        cv.create_polygon(self._att_pts([(-21, -8), (5, -8), (5, 8), (-21, 8)], ang), fill="#e8912d", outline="")
        cv.create_text(*self._att_pts([(-112, -16)], ang), text="機頭", fill="#1f3a68", font=small)
        cv.create_text(6, 4, anchor="nw", text="側視(站在圓心看,左翼朝你)", fill="#555", font=small)
        cv.create_text(self.att_cw - 6, 4, anchor="ne", text="機頭朝上 = 正", fill="#777", font=small)
        cv.create_text(self.att_cw - 6, self.att_ch - 4, anchor="se", text=f"機頭 {P:+.1f}°" if ok else "感測器未就緒",
                       fill="#1f3a68" if ok else "#cf222e", font=bold)

        # 後視:站在機尾往機頭看,左翼在左;左翼抬起為正滾轉(畫面上順時針)
        cv = self.att_rear
        cv.delete("all")
        cv.create_line(0, self.att_ch / 2, self.att_cw, self.att_ch / 2, fill="#9aa4b2", dash=(4, 3))
        cv.create_line(*self._att_pts([(-128, -1), (-160, -6)], R), fill="#777", width=1)
        cv.create_line(*self._att_pts([(-128, 1), (-160, 6)], R), fill="#777", width=1)
        cv.create_polygon(self._att_pts([(-128, -3), (128, -3), (128, 3), (-128, 3)], R), fill=body_col, outline="")
        cv.create_polygon(self._att_pts([(-2.5, -50), (2.5, -50), (2.5, -14), (-2.5, -14)], R), fill=body_col, outline="")
        cv.create_polygon(self._att_pts([(-42, -38), (42, -38), (42, -34), (-42, -34)], R), fill=body_col, outline="")
        for sx in (-1, 1):
            cv.create_line(*self._att_pts([(8 * sx, 12), (30 * sx, 40)], R), fill=body_col, width=max(2, 3 * k))
            self._att_circle(cv, 30 * sx, 43, 6, R, fill=body_col, outline="")
        self._att_circle(cv, 0, 0, 15, R, fill=body_col, outline="")
        cv.create_polygon(self._att_pts([(-13, -8), (13, -8), (13, 8), (-13, 8)], R), fill="#e8912d", outline="")
        cv.create_text(*self._att_pts([(-100, -14)], R), text="左翼", fill="#1f3a68", font=small)
        cv.create_text(6, 4, anchor="nw", text="後視(站在機尾往機頭看)", fill="#555", font=small)
        cv.create_text(self.att_cw - 6, 4, anchor="ne", text="左翼抬起 = 正", fill="#777", font=small)
        cv.create_text(6, self.att_ch - 4, anchor="sw", text="← 引線,往操控手", fill="#777", font=small)
        cv.create_text(self.att_cw - 6, self.att_ch - 4, anchor="se", text=f"滾轉 {R:+.1f}°" if ok else "",
                       fill="#1f3a68", font=bold)

        if not s:
            self.att_read.configure(text="")
            self.att_sub.configure(text="")
            return
        if not ok:
            self.att_read.configure(text="感測器未就緒(沒有回應或故障)", foreground="#cf222e")
            self.att_sub.configure(text="")
            return
        level = abs(P) <= 1.5 and abs(R) <= 1.5
        self.att_read.configure(text=f"控制使用:機頭 {P:+.1f}°   滾轉 {R:+.1f}°" + ("     ✓ 接近水平" if level else ""),
                                foreground="#1a7f37" if level else "#1f3a68")
        sh = s.get("_sh") or {}
        parts = [f"晶片原始(修正前):機頭 {float(s.get('rp', 0)):+.1f}°,滾轉 {float(s.get('rr', s.get('r', 0))):+.1f}°"]
        if "pitchTrim" in sh:
            parts.append(f"角度修正 {float(sh['pitchTrim']):+.1f}°,滾轉修正 {float(sh.get('rollTrim', 0)):+.1f}°")
        if "noseAxis" in sh and "upAxis" in sh:
            try:
                parts.append(f"安裝方位:{self.AXES[int(sh['noseAxis'])]} 朝機頭,{self.AXES[int(sh['upAxis'])]} 朝機背")
            except (IndexError, ValueError):
                pass
        parts.append("靜止" if s.get("st") else "移動中")
        self.att_sub.configure(text=" · ".join(parts))

    # ---------------- WiFi 設定(GG 2026-11-03) ----------------
    def _wifi_mode_changed(self):
        st = "normal" if self.wmode.get() == "sta" else "disabled"
        for w in self.wsta:
            w.configure(state=st)

    def _wifi_ap_preview(self):
        s = self.wsfx.get()
        n = len(s.encode("utf-8"))
        over = n > 14 or s != s.strip()
        self.ap_preview.configure(text=f"→ {self.ap_prefix}{s}({n}/14{',太長' if n > 14 else ''}{',頭尾不能空白' if s != s.strip() else ''})",
                                  foreground="#cf222e" if over else "#555")

    def _wifi_ssid_picked(self):
        label = self.wssid.get()
        if label in self.scan_items:
            ssid, is_open = self.scan_items[label]
            changed = ssid != getattr(self, "wifi_cur_ssid", None)
            self.wssid.set(ssid)
            if changed:
                self.wpw.set("")   # 換了不同的網路,舊密碼一定不對
                if not is_open:
                    self.wpw_e.focus_set()
            self.wifi_state.configure(text=f"已選「{ssid}」" + ("(開放網路,密碼留空)" if is_open else ",請輸入密碼") + ",再按「套用到板子並測試連線」.",
                                      foreground="#333")

    def _wifi_scan_fill(self, items):
        bars = lambda r: "▂▄▆█" if r >= -55 else "▂▄▆" if r >= -67 else "▂▄" if r >= -78 else "▂"   # noqa: E731
        self.scan_items = {}
        labels = []
        for ssid, rssi, _ch, is_open in items:
            label = f"{ssid}    {bars(rssi)} {rssi} dBm{'  開放' if is_open else ''}"
            self.scan_items[label] = (ssid, bool(is_open))
            labels.append(label)
        self.wssid_cb.configure(values=labels)
        if labels:
            with contextlib.suppress(Exception):
                self.wssid_cb.tk.call("ttk::combobox::Post", self.wssid_cb)   # 直接把下拉清單打開讓使用者點
            self.wifi_state.configure(text=f"找到 {len(labels)} 個 2.4GHz WiFi,從「WiFi 名稱」的下拉選單點一個.", foreground="#1a7f37")
        else:
            self.wifi_state.configure(text="附近找不到 2.4GHz 的 WiFi. 手機熱點請開 2.4GHz(iPhone 開「最大化相容性」)再搜尋一次.", foreground="#cf222e")

    def _wifi_fill(self, w):
        """GET /api/wifi 的結果填進欄位."""
        self.wifi_loaded = True
        self.wifi_cur = w
        self.wifi_cur_ssid = w.get("ssid", "")
        self.ap_prefix = w.get("apprefix") or self.ap_prefix
        self.ap_prefix_lab.configure(text=self.ap_prefix)
        self.wmode.set("ap" if (w.get("forceap") or not w.get("ssid")) else "sta")
        self.wssid.set(w.get("ssid", ""))
        self.wpw.set(w.get("pw", ""))
        self.wsfx.set(w.get("apsfx", ""))
        self.wappw.set(w.get("appw") or "12345678")
        self._wifi_mode_changed()

    def _wifi_board(self, port):
        """背景:確保 USB 監看開著且板子有 API,回 bridge."""
        if not self._usb_monitor_on(port, 3.0):
            raise board_link.BoardError(f"打不開 {port}")
        if not board_link.probe(self.monitor.bridge, 2.5):
            raise board_link.BoardError(f"板子沒有回應 USB 設定通道:韌體要 {USB_API_MIN_FW} 以上,請先到「燒錄」頁更新(保留板上設定)")
        return self.monitor.bridge

    def _wifi_read(self, quiet=False):
        port = self._port()
        if not port:
            if not quiet:
                messagebox.showwarning("沒有序列埠", "請用 USB 線接上開發板. WiFi 設定只能透過 USB 線改.", parent=self.root)
            return
        self._set_busy(True)
        self.wifi_state.configure(text=f"讀取 {port} 板上的 WiFi 設定 …", foreground="#9a6700")

        def job():
            try:
                w = board_link.wifi_get(self._wifi_board(port))
                self.q.put(("wifi_fields", w))
                now = w.get("apnow") or w.get("apssid")
                mode = "板子自己開熱點" if (w.get("forceap") or not w.get("ssid")) else f"連到「{w.get('ssid')}」(連不上時開熱點)"
                self.q.put(("wifi_state", (f"已讀取板上設定:{mode};熱點名稱 {now}. 改好後按「套用到板子並測試連線」.", "#1a7f37")))
            except board_link.BoardError as e:
                self.q.put(("wifi_state", (f"讀不到板上設定:{e}", "#cf222e" if not quiet else "#555")))
            finally:
                self.q.put(("done", None))

        threading.Thread(target=job, daemon=True).start()

    def _wifi_scan(self):
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請用 USB 線接上開發板.", parent=self.root)
            return
        self._set_busy(True)
        self.wifi_state.configure(text="板子搜尋附近的 WiFi,約 3~10 秒 …", foreground="#9a6700")

        def job():
            try:
                items = board_link.wifi_scan(self._wifi_board(port))
                self.q.put(("scan_list", items))
            except board_link.BoardError as e:
                self.q.put(("wifi_state", (f"搜尋失敗:{e}", "#cf222e")))
            finally:
                self.q.put(("done", None))

        threading.Thread(target=job, daemon=True).start()

    def _wifi_apply(self):
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請用 USB 線接上開發板. WiFi 設定只能透過 USB 線改(改完板子要重開,WiFi 會斷).", parent=self.root)
            return
        sta = self.wmode.get() == "sta"
        ssid, pw, sfx, appw = self.wssid.get().strip(), self.wpw.get(), self.wsfx.get(), self.wappw.get()
        errs = []
        if sta and not ssid:
            errs.append("請輸入 WiFi 名稱(或按「搜尋附近 WiFi」從清單點一個)")
        if sta and len(ssid.encode("utf-8")) > 32:
            errs.append("WiFi 名稱太長")
        if sta and 0 < len(pw) < 8:
            errs.append("WiFi 密碼至少 8 碼(開放網路請留空)")
        if len(sfx.encode("utf-8")) > 14:
            errs.append("熱點名稱後面接的字太長:最多 14 個英數字(中文一字算 3 個)")
        if sfx != sfx.strip():
            errs.append("熱點名稱後面接的字頭尾不能是空白")
        if not 8 <= len(appw) <= 63 or appw != appw.strip() or any(not 0x20 <= ord(c) <= 0x7E for c in appw):
            errs.append("熱點密碼要 8~63 個英文,數字或鍵盤符號(不能有中文或頭尾空白)")
        if errs:
            messagebox.showwarning("還不能套用", "\n".join(errs), parent=self.root)
            return
        apname = self.ap_prefix + sfx
        what = (f"板子會連到 WiFi「{ssid}」(密碼 {'(無)' if not pw else '已填'}),連不上時改開自己的熱點「{apname}」." if sta
                else f"板子自己開熱點「{apname}」,密碼 {appw}.")
        if not messagebox.askokcancel("套用 WiFi 設定", f"{what}\n\n按確定後板子會重新開機並測試連線,約 10~40 秒,請不要拔 USB 線.",
                                      parent=self.root):
            return
        new = {"ssid": ssid, "pw": pw, "forceap": 0 if sta else 1, "apsfx": sfx, "appw": appw}
        self._set_busy(True)
        self.wifi_big.grid_remove()
        threading.Thread(target=self._wifi_apply_job, args=(port, new), daemon=True).start()

    def _wait_reboot(self, timeout):
        """重開後等板子印出開機完成(READY)再回應 API. 只靠 API 有回應不夠:太早問可能問到還沒重開的舊程式.
        回 True = 看到開機完成;沒看到但 API 有回應也回 True(訊息被 USB 重新列舉吃掉);都沒有回 False."""
        lq = queue.Queue()
        self.listeners.append(lq)
        try:
            end = time.time() + timeout
            ready = False
            while time.time() < end and not ready:
                try:
                    ready = lq.get(timeout=0.2).startswith("READY")
                except queue.Empty:
                    pass
        finally:
            with contextlib.suppress(ValueError):
                self.listeners.remove(lq)
        end = time.time() + 8
        while time.time() < end:
            if self.monitor.connected() and board_link.probe(self.monitor.bridge, 1.5):
                return True
            time.sleep(0.3)
        return False

    def _serial_query(self, cmd, pred, timeout, retry=1.5):
        """送文字指令直到收到符合 pred 的一行(回該行),逾時回 None. 背景執行緒用."""
        lq = queue.Queue()
        self.listeners.append(lq)
        try:
            end = time.time() + timeout
            nxt = 0
            while time.time() < end:
                if time.time() >= nxt:
                    self.monitor.send(cmd)
                    nxt = time.time() + retry
                try:
                    line = lq.get(timeout=0.1)
                except queue.Empty:
                    continue
                if pred(line):
                    return line
            return None
        finally:
            with contextlib.suppress(ValueError):
                self.listeners.remove(lq)

    def _wifi_apply_job(self, port, new, reverting=False):
        """背景:寫入 WiFi 設定(板子存成試用)→ 重開 → 等 WiFi 就緒 → 是要的模式就保持(固定)並大字顯示網址.
        要連家用 WiFi 卻退到熱點 = 連不上:問要不要改回原本的設定(用同一個流程套回去). reverting = 正在改回,不再問."""
        q = self.q

        def say(text, color="#9a6700"):
            q.put(("wifi_state", (text, color)))
            q.put(("tool", text))

        try:
            board = self._wifi_board(port)
            cur = board_link.wifi_get(board)
            cfg = {"ssid": new["ssid"], "pw": new["pw"], "host": cur.get("host", "lineplane"), "tmo": cur.get("tmo", 30),
                   "forceap": new["forceap"], "txp": cur.get("txp", 5), "apsfx": new["apsfx"], "appw": new["appw"]}
            prefix = cur.get("apprefix") or self.ap_prefix
            apname = prefix + new["apsfx"]
            host = cfg["host"] + ".local"
            say("寫入 WiFi 設定到板子 …")
            board_link.wifi_set(board, cfg)
            say("已寫入,板子重新開機中 …")
            board_link.reboot(board)
            say("等待板子開機 …")
            if not self._wait_reboot(25):
                raise board_link.BoardError("板子重開後沒有回應. 拔掉 USB 再接上,按「讀取板上設定」看目前狀態")
            want_ap = new["forceap"] == 1 or not new["ssid"]   # 板子沒有 WiFi 名稱時自己也會開熱點
            tmo = int(cfg["tmo"])
            deadline = time.time() + tmo + 20
            kv = None
            while time.time() < deadline:
                line = self._serial_query("net", lambda s: s.startswith("wifi="), 4)
                kv = parse_net(line) if line else None
                if kv and kv["wifi"] != "connecting":
                    break
                if kv:
                    say(f"板子正在連「{new['ssid']}」…(最多等 {tmo} 秒)")
                time.sleep(1)
            if not kv or kv["wifi"] == "connecting":
                raise board_link.BoardError("等太久板子的 WiFi 還沒就緒. 稍後按「讀取板上設定」或「板子狀態」看結果;新設定沒確認的話板子 3 分鐘後會自己改回原設定")
            back = "已改回原本的 WiFi 設定. " if reverting else ""
            if not want_ap and kv["wifi"] == "sta":
                board_link.wifi_keep(board)
                big = (f"✔ {back}板子已連上「{new['ssid']}」,設定已固定.\n手機(同一個網路)用瀏覽器開: http://{kv['ip']}\n"
                       f"iPhone 與電腦也可以開: http://{host}")
                q.put(("wifi_big", (big, "#1a7f37")))
                say(f"完成:板子已連上「{new['ssid']}」,位址 http://{kv['ip']}(訊號 {kv['rssi']} dBm)", "#1a7f37")
                q.put(("dialog", ("WiFi 設定完成", f"板子已連上「{new['ssid']}」.\n\n手機連同一個網路,用瀏覽器開 http://{kv['ip']}\n(iPhone 與電腦也可以用 http://{host})", False)))
            elif want_ap and kv["wifi"] == "ap":
                board_link.wifi_keep(board)
                big = f"✔ {back}板子的熱點已開,設定已固定.\n手機連 WiFi「{apname}」(密碼 {new['appw']})\n再用瀏覽器開: http://{kv['ip']}"
                q.put(("wifi_big", (big, "#1a7f37")))
                say(f"完成:板子自己開熱點「{apname}」,位址 http://{kv['ip']}", "#1a7f37")
                q.put(("dialog", ("WiFi 設定完成", f"板子自己開熱點「{apname}」,密碼 {new['appw']}.\n\n手機連這個 WiFi 後用瀏覽器開 http://{kv['ip']}", False)))
            else:
                # 要連家用 WiFi 卻開了熱點:連不上. 常見原因寫清楚(手機熱點 5GHz 看不到,密碼錯)
                big = (f"✖ 連不上「{new['ssid']}」,板子改開了自己的熱點「{apname}」.\n"
                       "請檢查:密碼是否正確(分大小寫);手機熱點是否為 2.4GHz(iPhone 開「最大化相容性」,Android 頻段選 2.4GHz);手機熱點有沒有開著.")
                q.put(("wifi_big", (big, "#cf222e")))
                say(f"連不上「{new['ssid']}」,板子退到熱點「{apname}」", "#cf222e")
                if not reverting and self._ask("連不上 WiFi", f"板子連不上「{new['ssid']}」,目前開著自己的熱點「{apname}」.\n\n"
                                                           "要改回原本的 WiFi 設定嗎?(板子會再重新開機一次)\n選「否」的話板子會留在熱點模式,3 分鐘後自動改回原設定."):
                    old = {"ssid": cur.get("ssid", ""), "pw": cur.get("pw", ""), "forceap": int(cur.get("forceap") or 0),
                           "apsfx": cur.get("apsfx", ""), "appw": cur.get("appw") or "12345678"}
                    say("改回原本的 WiFi 設定 …")
                    self._wifi_apply_job(port, old, reverting=True)
                    return
            self.q.put(("wifi_fields", board_link.wifi_get(board)))
        except board_link.BoardError as e:
            say(f"WiFi 設定失敗:{e}", "#cf222e")
            q.put(("err", f"WiFi 設定失敗:{e}"))
            q.put(("dialog", ("WiFi 設定失敗", str(e), True)))
        finally:
            if not reverting:
                q.put(("done", None))

    # ---------------- 監看 ----------------
    def _toggle_cmd_adv(self):
        if self.cmd_row.winfo_viewable():
            self.cmd_row.grid_remove()
            self.cmd_adv_btn.configure(text="進階 ▸")
        else:
            self.cmd_row.grid()
            self.cmd_adv_btn.configure(text="進階 ▾")

    def _board_status(self):
        """板子狀態:依序送 fw / net / fs / mpu,回應由 translate_line 翻成中文顯示."""
        if not self.monitor.connected():
            if not self._port():
                messagebox.showwarning("沒有序列埠", "請先接上開發板.", parent=self.root)
                return
            self.monitor.start(self._port())
            self.mon_btn.configure(text="停止監看")
            self.root.after(800, self._board_status)
            return
        for i, c in enumerate(("fw", "net", "fs", "mpu")):
            self.root.after(i * 400, lambda c=c: self._send_cmd(c))

    def _reboot_board(self):
        if not messagebox.askokcancel("重新開機", "讓板子重新開機?(馬達運轉或起飛程序中請不要按)", parent=self.root):
            return
        self._send_cmd("reboot")

    def _toggle_monitor(self):
        if self.monitor.want:
            self.monitor.stop()
            self.mon_btn.configure(text="開始監看")
            return
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請先接上開發板,選擇序列埠.", parent=self.root)
            return
        self.monitor.start(port)
        self.mon_btn.configure(text="停止監看")
        self._log(f"開始監看 {port}({BAUD_MONITOR} bps)", "tool")

    def _send_cmd(self, cmd=None):
        text = (cmd if cmd is not None else self.cmd_var.get()).strip()
        if not text:
            return
        if not self.monitor.connected():
            if self.busy or not self._port():
                self._log("監看沒有連線,送不出去", "err")
                return
            self.monitor.start(self._port())
            self.mon_btn.configure(text="停止監看")
            self.root.after(800, lambda: self._send_cmd(text))
            return
        if self.monitor.send(text):
            name = CMD_NAMES.get(text.lower())
            self._log(f"> {name}({text})" if name and not self.raw_var.get() else f"> {text}", "sent")
        else:
            self._log("送出失敗(序列埠中斷?)", "err")
        if cmd is None:
            self.cmd_var.set("")

    def _save_log(self):
        path = filedialog.asksaveasfilename(parent=self.root, title="儲存訊息紀錄", defaultextension=".txt",
                                            initialfile=time.strftime("lineplane_log_%Y%m%d_%H%M%S.txt"),
                                            filetypes=[("文字檔", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log.get("1.0", "end"))

    def _on_close(self):
        if self.busy and not messagebox.askokcancel("燒錄中", "正在燒錄或下載,現在關閉可能讓板子燒到一半(可以重新燒錄救回). 確定關閉?", parent=self.root):
            return
        self.att_on = False
        self.monitor.want = False
        with contextlib.suppress(Exception):
            self.proxy.stop()
        self.root.destroy()


def setup_style(root):
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    from tkinter import font
    fam = "Microsoft JhengHei UI" if sys.platform == "win32" else None
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        with contextlib.suppress(Exception):
            f = font.nametofont(name)
            if fam:
                f.configure(family=fam)
            f.configure(size=10)
    style.configure("Big.TButton", font=(fam or "TkDefaultFont", 12, "bold"), padding=(16, 10))


def main():
    if sys.platform == "win32":
        with contextlib.suppress(Exception):
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)   # 高解析度螢幕字不模糊
    root = tk.Tk()
    setup_style(root)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
