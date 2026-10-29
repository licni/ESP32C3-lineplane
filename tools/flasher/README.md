# 線控飛機韌體燒錄工具(Windows,免安裝)

給**不想安裝程式開發環境**的使用者:下載一個 `LineplaneFlasher.exe`,接上 ESP32-C3 SuperMini 開發板,按一個按鈕就能燒錄線控飛機韌體,燒完自動檢查,還能看板子回報的訊息.

> [!WARNING]
> 燒錄與測試時一律**拆下螺旋槳**.

## 下載

**直接下載:<https://github.com/licni/ESP32C3-lineplane/releases/latest/download/LineplaneFlasher.exe>**
(永遠是最新版;各版本說明在 [Releases](https://github.com/licni/ESP32C3-lineplane/releases))

不用安裝,直接執行. 第一次打開時 Windows SmartScreen 可能提示「無法辨識的應用程式」(沒有付費簽章),按「其他資訊 → 仍要執行」.

## 使用步驟

1. **接上開發板**:用「可以傳資料」的 USB 線接電腦. 工具會自動偵測 ESP32-C3(原生 USB,VID 303A)並選好序列埠;
   接了好幾片時請確認選的是要燒的那一片. 偵測不到時:按住板子上的 **BOOT** 鍵,拔掉再插上 USB,放開 BOOT.
2. **選韌體**:
   - 選「普通版」或「帶螢幕板」(0.42 吋 OLED),在「韌體版本」選單挑一版(預設最新版,下面會顯示這版改了什麼),按「下載這個版本」.
     版本清單來自[公開韌體專案](https://github.com/licni/ESP32lineplane-firmware)的 Releases;帶螢幕板 2026.09.25.1 起才有.
   - 已經燒過,正常使用中的板子想換版本又不想重設:勾「保留板上設定」,只下載韌體更新檔.
     換成較舊的版本時,新版存的設定舊版可能讀不懂而回出廠值.
   - 也可以按「選電腦裡的檔案…」選自己下載的 `.bin`.
   - 下載的檔案與電腦裡的檔案都會做檢查:ESP 映像檔內建的檢查碼與 SHA-256,晶片種類,線控飛機身分標記的版本與板子種類.
3. 按 **開始燒錄**,確認視窗看清楚序列埠,版本,板子種類後按確定. 進度條顯示清除與寫入進度.
4. 燒完板子自動重新開機,工具接著**自動檢查**(可以取消勾選):

   | 項目 | 怎麼檢查 |
   |---|---|
   | 晶片 | esptool 連上後讀到的晶片型號要是 ESP32-C3 |
   | 寫入校驗 | 每一段寫完都比對板子上的檢查碼 |
   | 開機與版本 | 送序列指令 `fw`,板子回報的版本要和檔案相同 |
   | 感測器 MPU6050 | 送 `mpu`,沒接或接錯會提示檢查 GPIO5/6 接線 |
   | WiFi | 送 `net`,顯示熱點模式或家用 WiFi 的 IP |

5. 完成後手機連板子的 WiFi 熱點,開 `http://192.168.4.1` 設定. 詳細見[使用說明書](../../docs/使用說明書.md).

隨時可以按「只做檢查」檢查已經燒好的板子.

## 兩種韌體檔

工具會讀檔案內容自動判斷,顯示類型,版本,板子種類(檔案裡的身分標記 `LPFWID1:ESP32C3-lineplane|版本|種類|`).

| 檔案 | 用途 | 燒錄方式 | 板上設定 |
|---|---|---|---|
| `lineplane-full-版本.bin` / `-oled.bin`(Releases) | **全新開發板**第一次燒錄 | 從 0x0 燒整片(預設先清除整片) | 回出廠值 |
| `firmware-版本.bin` / `-oled.bin` | 已經燒過的板子用 USB 更新 | 韌體燒在 0x10000,otadata 寫成 boot_app0 | 保留 |

完整燒錄檔 2026.10.07.1 起才有. 選更早的版本時,工具用最新完整燒錄檔的前 64KB(開機程式,分割表,boot_app0;兩種板子相同)
接上那一版的韌體更新檔,組成完整燒錄檔,一樣可以燒全新板子.

已經在用,能連網頁的板子,建議照舊用網頁「系統 → 韌體更新 → 檢查更新」.
全新板子只能用完整燒錄檔:韌體更新檔沒有開機程式與分割表,燒了不會開機(檢查會顯示 invalid header 或沒有回應).

## 序列監看(板子回報的訊息)

下方黑底區域顯示板子從 USB 送出的文字(115200 bps),可以在「送指令」輸入序列指令,或用下面的快捷按鈕:

| 指令 | 內容 |
|---|---|
| `fw` | 韌體版本與更新狀態 |
| `net` | WiFi 狀態,IP,主機名 |
| `fs` | 飛行狀態機目前狀態 |
| `t` | 開關即時資料(姿態,加速度,電變輸出,每 0.2 秒一行) |
| `help` | 列出全部指令 |

板子重開或拔插 USB 時監看會自動重新連線. 「存成文字檔…」可以把訊息存下來回報問題.
工具開序列埠時不切換 DTR/RTS,所以打開監看**不會讓板子重開**.

## 開發者:自己打包

在 Windows 安裝 [Python](https://www.python.org/) 3.10 以上(python.org 安裝版內建 tkinter),執行:

```bat
tools\flasher\build_exe.bat
```

產出 `tools/flasher/dist/LineplaneFlasher.exe`. 不打包直接跑:`pip install -r requirements.txt` 後 `python lineplane_flasher.py`.

GitHub Actions(`.github/workflows/flasher.yml`)在 `tools/flasher/` 有變更時用 Windows 自動打包,exe 放在該次執行的 Artifacts;
在 main 分支打包完直接建立/更新 Release「燒錄工具 v版本」(標籤 `flasher-v版本`)並設為最新,上面的固定網址就會拿到新版.
發新版前先改 `lineplane_flasher.py` 的 `APP_VERSION`(版本沒改時重跑會覆蓋同一版的 exe).

| 檔案 | 內容 |
|---|---|
| `lineplane_flasher.py` | 視窗介面,燒錄流程(esptool 當函式庫呼叫),開機後檢查,序列監看 |
| `fw_image.py` | 韌體檔分析(類型,身分標記,晶片,分割表,映像檔校驗),boot_app0,版本清單,下載與組合 |
| `test_fw_image.py` | `fw_image` 單元測試(不需要網路與板子) |
| `requirements.txt` | 固定版本:esptool 4.12.0,pyserial 3.5,PyInstaller 6.11.1 |
| `build_exe.bat` | Windows 本機打包 |

版本清單與下載依賴公開韌體專案的命名(`tools/publish_firmware.py` 產生):Release 標籤 `v版本`,
韌體更新檔 `firmware-版本[-oled].bin`,完整燒錄檔 `lineplane-full-版本[-oled].bin`;讀不到 Releases(沒網路,GitHub API 次數用完)時
退回 `manifest.json` / `manifest-oled.json` 的最新版. 改發布工具的命名時要一起改 `fw_image.py`.
