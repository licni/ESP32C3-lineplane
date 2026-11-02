# 版本流水號: r7 (2026-11-02) 板子訊息併入燒錄頁(GG):兩個分頁「燒錄與板子訊息」「設定與備份」;APP_VERSION 2.0.4
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
#  - 序列監看(燒錄頁下方):顯示板子回報的訊息,可以送指令(help 列出全部).
# 序列埠一律 dtr=False, rts=False 再開(C3 原生 USB 把 DTR/RTS 切換當成重置).
# 只用 Python 內建 tkinter + esptool + pyserial. 開發測試:python lineplane_config.py
# ============================================================================
import contextlib
import io
import json
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

APP_VERSION = "2.0.4"
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
        self._scan_ports(force=True)
        self.root.after(1500, self._port_loop)
        self._load_releases()
        path = self.prefs.get("file")
        if path and os.path.isfile(path):
            self._load_file(path, quiet=True)
        self.root.after(50, self._poll)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- 畫面 ----------------
    def _build(self):
        r = self.root
        r.title(TITLE)
        r.minsize(760, 620)
        # 預設高度依螢幕:燒錄頁下方有板子訊息區,太矮會被擠掉;小筆電(768)就用剩下的高度
        try:
            sh = r.winfo_screenheight()
            r.geometry(f"880x{min(980, max(620, sh - 90))}")
        except Exception:
            pass
        pad = {"padx": 8, "pady": 4}
        main = ttk.Frame(r, padding=8)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        # 序列埠(兩個分頁共用)
        f1 = ttk.LabelFrame(main, text=" 開發板序列埠(USB 線) ", padding=6)
        f1.grid(row=0, column=0, sticky="ew", **pad)
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
        self.nb.add(tab_flash, text="① 燒錄與板子訊息")
        self.nb.add(tab_cfg, text="② 設定與備份")
        tab_flash.columnconfigure(0, weight=1)
        tab_cfg.columnconfigure(0, weight=1)
        tab_flash.rowconfigure(2, weight=1)   # 板子訊息區吃掉剩下的高度

        # 燒錄分頁 1. 韌體檔
        f2 = ttk.LabelFrame(tab_flash, text=" 1. 韌體檔 ", padding=6)
        f2.grid(row=0, column=0, sticky="ew", **pad)
        f2.columnconfigure(1, weight=1)
        ttk.Label(f2, text="板子種類").grid(row=0, column=0, sticky="w")
        row = ttk.Frame(f2)
        row.grid(row=0, column=1, columnspan=2, sticky="w", padx=6)
        self.board_var = tk.StringVar(value=self.prefs.get("board", "MINI"))
        for code, name in fw_image.BOARDS.items():
            ttk.Radiobutton(row, text=name + ("(0.42 吋 OLED)" if code == "OLED" else ""), value=code, variable=self.board_var,
                            command=self._fill_versions).pack(side="left", padx=(0, 12))
        ttk.Label(f2, text="韌體版本").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.ver_var = tk.StringVar()
        self.ver_cb = ttk.Combobox(f2, textvariable=self.ver_var, state="readonly")
        self.ver_cb.grid(row=1, column=1, sticky="ew", padx=6, pady=(6, 0))
        self.ver_cb.bind("<<ComboboxSelected>>", lambda e: self._show_notes())
        vb = ttk.Frame(f2)
        vb.grid(row=1, column=2, pady=(6, 0))
        self.reload_btn = ttk.Button(vb, text="重新整理", command=self._load_releases)
        self.reload_btn.pack(side="left")
        self.dl_btn = ttk.Button(vb, text="下載這個版本", command=self._download)
        self.dl_btn.pack(side="left", padx=(4, 0))
        self.notes = ttk.Label(f2, text="讀取版本清單中 …", foreground="#555", wraplength=700, justify="left")
        self.notes.grid(row=2, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        self.keep_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(f2, text="保留板上設定(只換韌體;已經燒過、正常使用中的板子才能勾)", variable=self.keep_var,
                        command=self._show_notes).grid(row=3, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        ttk.Separator(f2).grid(row=4, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Label(f2, text="要燒的檔案").grid(row=5, column=0, sticky="w")
        self.file_var = tk.StringVar()
        e = ttk.Entry(f2, textvariable=self.file_var)
        e.grid(row=5, column=1, sticky="ew", padx=6)
        e.bind("<Return>", lambda ev: self._load_file(self.file_var.get().strip().strip('"')))
        ttk.Button(f2, text="選電腦裡的檔案…", command=self._browse).grid(row=5, column=2)
        self.file_info = ttk.Label(f2, text="尚未選擇檔案:先選版本按「下載這個版本」,或選電腦裡的 .bin", foreground="#555", wraplength=700, justify="left")
        self.file_info.grid(row=6, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        self.erase_var = tk.BooleanVar(value=True)
        self.erase_cb = ttk.Checkbutton(f2, text="燒錄前先清除整片(全新板子建議勾選)", variable=self.erase_var)
        self.erase_cb.grid(row=7, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))

        # 燒錄分頁 2. 燒錄與檢查
        f3 = ttk.LabelFrame(tab_flash, text=" 2. 燒錄與檢查 ", padding=6)
        f3.grid(row=1, column=0, sticky="ew", **pad)
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
        ttk.Label(opt, text="(完整燒錄檔會清掉板上設定;燒錄前會先問要不要備份)", foreground="#555").pack(side="left")
        chk = ttk.Frame(f3)
        chk.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        self.checks = {}
        chk.columnconfigure(1, weight=1)
        chk.columnconfigure(3, weight=1)
        for i, (key, name) in enumerate([("chip", "晶片"), ("verify", "寫入校驗"), ("boot", "開機與版本"),
                                         ("mpu", "感測器 MPU6050"), ("wifi", "WiFi")]):
            ttk.Label(chk, text=name + ":").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=(0 if i % 2 == 0 else 16, 0))
            lab = ttk.Label(chk, text="—", foreground="#777", wraplength=330, justify="left")
            lab.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", padx=6)
            self.checks[key] = lab

        # 設定與備份分頁
        fc = ttk.LabelFrame(tab_cfg, text=" 連線方式 ", padding=6)
        fc.grid(row=0, column=0, sticky="ew", **pad)
        fc.columnconfigure(1, weight=1)
        self.link_var = tk.StringVar(value=self.prefs.get("link", "usb"))
        ttk.Radiobutton(fc, text="USB 線(上面選的序列埠;韌體要 " + USB_API_MIN_FW + " 以上)", value="usb", variable=self.link_var,
                        command=self._save_link).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(fc, text="WiFi,板子位址:", value="wifi", variable=self.link_var, command=self._save_link).grid(row=1, column=0, sticky="w")
        self.host_var = tk.StringVar(value=self.prefs.get("host", "lineplane.local"))
        he = ttk.Entry(fc, textvariable=self.host_var)
        he.grid(row=1, column=1, sticky="ew", padx=6)
        he.bind("<FocusOut>", lambda e: self._save_link())
        ttk.Label(fc, text="連家用 WiFi 用 lineplane.local(或板子的 IP);電腦連板子熱點時用 192.168.4.1", foreground="#555").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))

        fs = ttk.LabelFrame(tab_cfg, text=" 設定板子(和手機看到的網頁完全相同) ", padding=6)
        fs.grid(row=1, column=0, sticky="ew", **pad)
        fs.columnconfigure(1, weight=1)
        self.cfg_btn = ttk.Button(fs, text="開啟設定網頁", command=self._open_config, style="Big.TButton")
        self.cfg_btn.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))
        self.cfg_state = ttk.Label(fs, text="按下後會用電腦的瀏覽器打開設定網頁.", wraplength=620, justify="left")
        self.cfg_state.grid(row=0, column=1, sticky="w")
        ttk.Label(fs, text="USB 線:網頁透過這個程式轉送到板子,程式關掉網頁就斷線. 韌體更新請用「燒錄」頁(勾保留板上設定).\n"
                           "WiFi:直接開板子的網頁,和手機一樣.", foreground="#555", wraplength=620, justify="left").grid(row=1, column=1, sticky="w", pady=(4, 0))

        fb = ttk.LabelFrame(tab_cfg, text=" 板上設定備份(全部 6 組飛行風格 + 起飛降落與安全 / 安裝 / 電變 / WiFi) ", padding=6)
        fb.grid(row=2, column=0, sticky="ew", **pad)
        fb.columnconfigure(2, weight=1)
        self.bk_out_btn = ttk.Button(fb, text="匯出板上設定備份…", command=lambda: self._backup_export())
        self.bk_out_btn.grid(row=0, column=0, sticky="w")
        self.bk_in_btn = ttk.Button(fb, text="匯入備份到板子…", command=self._backup_import)
        self.bk_in_btn.grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.bk_state = ttk.Label(fb, text="", wraplength=600, justify="left")
        self.bk_state.grid(row=0, column=2, sticky="w", padx=8)
        ttk.Label(fb, text="匯出存成文字檔(裡面是板子網頁「備份」頁用的設定備份碼). 匯入會先檢查,顯示內容後才套用並儲存;\n"
                           "板上有未儲存的變更時會先問要不要儲存. 含 WiFi 的備份套用後 WiFi 設定為試用,重新開機後 3 分鐘內要在網頁按「保持」.",
                  foreground="#555", wraplength=700, justify="left").grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # 燒錄分頁 3. 板子訊息(序列監看)
        f4 = ttk.LabelFrame(tab_flash, text=" 3. 板子回報訊息(序列監看) ", padding=6)
        f4.grid(row=2, column=0, sticky="nsew", **pad)
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
        self.log = tk.Text(txt, height=6, wrap="word", font=mono, background="#111", foreground="#ddd", insertbackground="#ddd")
        self.log.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(txt, command=self.log.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=sb.set)
        self.log.tag_configure("tool", foreground="#7fb8ff")
        self.log.tag_configure("err", foreground="#ff7b7b")
        self.log.tag_configure("ok", foreground="#7ee787")
        self.log.tag_configure("sent", foreground="#e3b341")
        cmd = ttk.Frame(f4)
        cmd.grid(row=2, column=0, sticky="ew")
        cmd.columnconfigure(1, weight=1)
        ttk.Label(cmd, text="送指令").grid(row=0, column=0)
        self.cmd_var = tk.StringVar()
        ce = ttk.Entry(cmd, textvariable=self.cmd_var)
        ce.grid(row=0, column=1, sticky="ew", padx=6)
        ce.bind("<Return>", lambda ev: self._send_cmd())
        ttk.Button(cmd, text="送出", command=self._send_cmd).grid(row=0, column=2)
        quick = ttk.Frame(f4)
        quick.grid(row=3, column=0, sticky="w", pady=(4, 0))
        for label, c in [("版本 fw", "fw"), ("網路 net", "net"), ("飛行狀態 fs", "fs"), ("即時資料開關 t", "t"), ("全部指令 help", "help")]:
            ttk.Button(quick, text=label, command=lambda c=c: self._send_cmd(c)).pack(side="left", padx=(0, 4))

        self.status = ttk.Label(r, text="", relief="sunken", anchor="w", padding=(6, 2))
        self.status.pack(side="bottom", fill="x")
        self._log(f"{TITLE}. 接上開發板後會自動偵測序列埠. 燒錄與測試前請拆下螺旋槳.", "tool")
        self.nb.select({"flash": 0, "cfg": 1}.get(self.prefs.get("tab", "flash"), 0))

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
        for w in (self.flash_btn, self.check_btn, self.dl_btn, self.reload_btn, self.mon_btn, self.cfg_btn,
                  self.bk_out_btn, self.bk_in_btn, self.bk_flash_btn):
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
                elif kind == "file":
                    self._load_file(val)
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
                elif kind == "open_url":
                    webbrowser.open(val)
        except queue.Empty:
            pass
        self.root.after(50, self._poll)

    def _on_board_line(self, line):
        tag = "err" if line.startswith("ERR") and "in use" not in line else None
        self._log(line, tag)
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
        self.erase_cb.configure(state="normal" if a["kind"] == "full" else "disabled")
        if a["board"] in fw_image.BOARDS and a["board"] != self.board_var.get():
            self.board_var.set(a["board"])
            self._fill_versions()
        self.prefs["file"] = path
        save_prefs(self.prefs)
        if not quiet:
            self._log(f"選擇韌體檔:{path}({kind},版本 {a['version'] or '不明'})", "tool")

    def _load_releases(self):
        self.notes.configure(text="讀取版本清單中 …", foreground="#555")

        def job():
            try:
                self.q.put(("releases", fw_image.list_releases()))
            except Exception as e:
                self.q.put(("releases_err", str(e)))

        threading.Thread(target=job, daemon=True).start()

    def _fill_versions(self):
        """依板子種類列出有韌體檔的版本(帶螢幕板 2026.09.25.1 起才有)."""
        board = self.board_var.get()
        self.prefs["board"] = board
        save_prefs(self.prefs)
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
        if self.keep_var.get():
            if not has_app:
                extra.append("! 這版沒有韌體更新檔,不能保留設定,請取消勾選")
            elif not r["latest"]:
                extra.append("! 換成較舊的版本時,新版存的設定舊版可能讀不懂而回出廠值")
        elif not has_full:
            extra.append("這版沒有完整燒錄檔:下載時會用最新完整燒錄檔的開機程式與分割表組合,一樣可以燒全新板子.")
        self.notes.configure(text="\n".join([text or "(這版沒有說明)"] + extra),
                             foreground="#9a6700" if any(x.startswith("!") for x in extra) else "#333")

    def _download(self):
        r = self._selected_release()
        if not r:
            messagebox.showwarning("沒有版本", "版本清單還沒讀到,請確認電腦能上網後按「重新整理」.", parent=self.root)
            return
        self._set_busy(True)
        threading.Thread(target=self._download_job, args=(r, self.board_var.get(), self.keep_var.get()), daemon=True).start()

    def _download_job(self, rel, board, keep):
        q = self.q
        ver = rel["version"]
        try:
            q.put(("stage", f"下載 {ver}({fw_image.board_name(board)})…"))

            def prog(got, total):
                q.put(("progress", got * 100 / total if total else None))

            name, data = fw_image.download_version(rel, board, keep, self.releases, progress=prog,
                                                    log=lambda m: q.put(("tool", m)))
            path = os.path.join(data_dir(), "firmware", name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            q.put(("okmsg", f"已下載並驗證 {name}({len(data):,} 位元組,檢查碼正確)"))
            q.put(("file", path))
            q.put(("progress", 100))
            q.put(("stage", f"已下載 {ver},可以開始燒錄"))
        except Exception as e:
            q.put(("err", f"下載失敗:{e}"))
            q.put(("progress", 0))
            q.put(("stage", "下載失敗"))
            q.put(("dialog", ("下載失敗", f"{e}\n\n請確認電腦能上網;也可以到 https://github.com/{fw_image.FW_REPO}/releases 手動下載後用「選電腦裡的檔案」.", True)))
        q.put(("done", None))

    # ---------------- 燒錄 ----------------
    def _start_flash(self):
        port = self._port()
        if not port:
            messagebox.showwarning("沒有序列埠", "請先接上開發板,選擇序列埠.", parent=self.root)
            return
        path = self.file_var.get().strip().strip('"')
        if not self.image or self.image[0] != path:
            self._load_file(path)
        if not self.image:
            messagebox.showwarning("沒有韌體檔", "請先選版本按「下載這個版本」,或選電腦裡的韌體檔.", parent=self.root)
            return
        _, data, a = self.image
        if a["problems"]:
            messagebox.showerror("這個檔案不能燒", "\n".join(a["problems"]), parent=self.root)
            return
        if a["kind"] == "full":
            what = ("會先清除整片快閃記憶體,再從 0x0 燒入完整燒錄檔." if self.erase_var.get() else "從 0x0 燒入完整燒錄檔.") + \
                   "\n板子上原本的設定(WiFi,飛行參數)會全部回出廠值."
        else:
            what = "燒入韌體更新檔(0x10000),板子上的設定保留.\n全新板子不能用這種檔案,要用 lineplane-full-*.bin."
        msg = (f"序列埠:{port}\n檔案:{os.path.basename(path)}\n版本:{a['version'] or '不明'}  板子種類:"
               f"{fw_image.board_name(a['board']) if a['board'] else '不明'}\n\n{what}\n\n請確認已拆下螺旋槳. 確定開始燒錄?")
        if a["warnings"] and not a["version"]:
            msg = "注意:" + a["warnings"][-1] + "\n\n" + msg
        if not messagebox.askokcancel("開始燒錄", msg, parent=self.root, icon="warning"):
            return
        if a["kind"] == "full":
            # 完整燒錄檔會清掉板上設定:板子有 USB 設定通道就問要不要先匯出備份(空白板或舊韌體問不到,直接燒)
            fw = self._usb_probe(port, 2.0)
            if fw:
                ans = messagebox.askyesnocancel("先備份板上設定?", f"板子目前韌體 {fw.get('ver')},板上設定燒錄後會全部清除.\n\n"
                                                "要先把板上全部設定匯出成備份檔嗎?(燒完可以在「設定與備份」頁匯入)\n\n是 = 先匯出再燒錄,否 = 直接燒錄",
                                                parent=self.root, icon="warning")
                if ans is None:
                    return
                if ans:
                    self._backup_export(then=lambda: self._start_flash_go(port, data, a))
                    return
        self._start_flash_go(port, data, a)

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
                        q.put(("tool", f"> {cmd}"))
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

            line = ask("net", lambda s: s.startswith("wifi="), 5)
            if line is None:
                q.put(("check", ("wifi", "warn", "沒有回應")))
            else:
                kv = dict(re.findall(r"(\w+)=(\S*)", line))
                mode = kv.get("wifi")
                if mode == "ap":
                    q.put(("check", ("wifi", "ok", f"熱點模式 {kv.get('ip')}(手機連熱點後開 http://192.168.4.1)")))
                elif mode == "sta":
                    q.put(("check", ("wifi", "ok", f"已連家用 WiFi,IP {kv.get('ip')},http://{kv.get('host')}")))
                else:
                    q.put(("check", ("wifi", "run", "連線中(開機後幾秒內會開熱點或連上家用 WiFi)")))
            bad = [n for n, ok in fails if not ok]
            q.put(("stage", "檢查完成" if not bad else "檢查完成,有項目沒通過"))
            q.put(("okmsg", "檢查完成. 序列監看保持開著,可以繼續看板子回報的訊息."))
            if after_flash and not bad:
                q.put(("dialog", ("完成", f"燒錄與檢查完成,板子韌體 {ver}.\n\n接下來可以到「設定與備份」頁按「開啟設定網頁」用 USB 線設定,"
                                  "或手機連板子的 WiFi 熱點開 http://192.168.4.1.\n詳細步驟見專案 README 與使用說明書.", False)))
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
        save_prefs(self.prefs)

    def _save_tab(self):
        self.prefs["tab"] = ["flash", "cfg"][self.nb.index(self.nb.select())]
        save_prefs(self.prefs)

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

    # ---------------- 監看 ----------------
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
            self._log(f"> {text}", "sent")
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
