# 線控飛機油門控制器 — Claude 工作記憶

電動線控特技機(F2B)的油門控制器. ESP32-C3 SuperMini + MPU6050 算機頭相對地平線的角度,
依飛行時間軸與角度曲線控制電變油門. WiFi 網頁調參,設定存 NVS,保留 OTA.
對話與註解一律台灣繁體中文;註解風格緊湊,標點用半形 "," ".".

## 先讀這兩份
- **docs/規格草案_2026-09-13.md**:已定案的完整規格(六輪討論的結果). 改規格要先和 GG 討論.
- **docs/開發紀錄.md**:分段進度,每段做了什麼,編譯結果,待實機確認事項. 換對話從這裡接續.
- 文件都在 docs/(2026-09-14 為了之後公開發布整理):安全審查,全功能測試報告,兩份查證紀錄;docs/images 是 README 用的網頁截圖.
  根目錄只放 README.md(公開用說明),CLAUDE.md,platformio.ini. 新文件一律放 docs/.

## 版本庫
- 兩個 GitHub 原始碼專案(GG 2026-09-14),本機身分只設在這個版本庫:SuperGG + GitHub noreply 信箱.
  - `origin` = https://github.com/licni/ESP32lineplane:**GG 的私人雲端備份**,一直保持私人,不要刪除也不要公開.
  - `public` = https://github.com/licni/ESP32C3-lineplane:**公開**的原始碼專案(GG 2026-09-14 公開). 推上去別人馬上看得到,推送前先做個資檢查.
  - GG 要求推送時兩邊都推同樣的提交(`git push origin main` 與 `git push public main`).
- **授權 GPL-3.0**(GG 2026-09-14,LICENSE 在根目錄). 2026-09-14 為了之後公開,提交歷史壓成單一提交並清除個資(家用 WiFi 名稱,區網 IP,本機路徑).
  **不要把個資寫進版本庫**:家用 WiFi 名稱/密碼,區網 IP,Email,本機完整路徑;測試腳本預設位址用 lineplane.local,實際 IP 用參數傳.
  **韌體檔也不能帶個資**:Arduino 核心會把原始檔完整路徑(含使用者名稱)編進韌體,platformio.ini 的 `extra_scripts = pre:tools/pio_strip_paths.py` 不可拿掉;發布前可搜尋韌體檔確認沒有 "Users/".
  2026-09-14 GG 刪除了舊的公開韌體專案(舊韌體檔含使用者名稱),用原名重建,只有 2026.09.14.11 起的乾淨紀錄,板子更新網址不變.
  firmware_release/ 是重建後重新 clone 的;以後重新 clone 要記得設本機身分(SuperGG + noreply),否則發布工具 commit 會失敗.
- `test_logs/`(測試紀錄與板上設定備份)與 Python 暫存不進版本庫. GG 要求時才提交/推送.

## 工作方式
- **目前是「只改程式碼」模式(GG 2026-09-14,優先於下面的檢查規則)**:在 GG 說【恢復全部檢查】之前,不跑回歸/全功能/瀏覽器測試,
  不改使用說明書,不做燒錄前後設定備份比對,不重拍截圖. 程式改完編譯並燒到開發板,只列出這次修改影響到的東西與建議 GG 自己檢查的項目.
- 分段實作,每段編譯通過就寫進 docs/開發紀錄.md,再請 GG 實機確認.
- **編譯,燒錄,OTA,序列監控全部由 Claude 用 PlatformIO 操作**. GG 不用 Arduino IDE.
  pio 路徑:`$env:USERPROFILE\.platformio\penv\Scripts\pio.exe`.
- GG 開發期間全程不裝螺旋槳,燒錄與測試時不需要提醒拆槳.
- 開發板在 **COM20**(GG 確認是測試用板,可直接燒). 出現別的 COM 埠時先讀序列輸出確認再燒.
  開發板的 MPU6050 接在 **GPIO5/6**(GG 2026-09-14 從 GPIO0/1 改線,和使用者的板子與參考專案相同).
  原本 GPIO5 ↔ GPIO4 的測試跳線已拔掉:序列指令 pwmcap(量電變脈寬)/escemu(模擬電變)韌體直接擋下(會搶走 I2C 腳位),
  用到它們的測試(t0,t2,t3,t5,t6,t9,rpm_emulator_test,gear_test_nosettings)要換一隻腳重新跳線並改 test_hooks/esc_output 腳位才能完整跑.
- 燒錄:USB `pio run -t upload --upload-port COM20`;無線 `pio run -e ota -t upload`(預設 lineplane.local;熱點模式加 `--upload-port 192.168.4.1`).
  **無線燒錄/網頁上傳/板子下載後,新韌體是「待確認」**(2026-09-14 起):開網頁會自動確認,或 `POST /api/fw/confirm`;
  WiFi 就緒後 **1 分鐘**沒確認會自動退回舊版(GG 2026-09-14 從 5 分鐘縮短),確認前不能起飛. USB 燒錄不會待確認.
  無線燒錄後要馬上確認(測試腳本裡燒完就 POST /api/fw/confirm).
- **開發階段只有一塊板子**(GG 2026-09-14):就是接在電腦上的開發板. 發布,改腳位,改設定時不用顧慮其他使用者更新會不會出問題.
- 發布韌體給使用者(板子「檢查更新」):先改 `src/version.h` 的 FW_VERSION(要比公開專案上的新:板子逐段比數字,只裝比較新的版本),再 `tools/publish_firmware.py --notes "說明"`,
  推到公開專案 licni/ESP32lineplane-firmware(本機複本 firmware_release/,不進主版本庫). 公開專案只放韌體檔,不放原始碼.
  首頁只放 README,CHANGELOG,manifest.json;韌體檔在 firmware/ 資料夾(GG:首頁不要越來越長). 每版一定寫修正說明.
  **每天只留當天最新一版**(GG 2026-09-14):同一天再發布時工具自動刪掉當天舊的 Release/tag/韌體檔,當天修改合併進最新版的 Release 與 CHANGELOG.
  --notes 是板子顯示的精簡版(≤400 位元組,寫當天合併重點),--day-notes-file 是當天所有修改的完整條列(自己整理,拿掉已被取代的內容). firmware/ 只留最近 3 天.
- **使用說明書** docs/使用說明書.md(GG 2026-09-14 要求,給拿到硬體的使用者):改參數範圍/出廠值,網頁畫面文字,操作流程時同步更新說明書,
  再跑 `tools/manual_check.py`(目錄,連結,參數數值對照 settings.cpp). 網頁版用 `tools/manual_page/build.py` 產生,發布在 GG 的 claude.ai 私人 Artifact「線控飛機油門控制器 使用說明書」.
- 開機安全:只有真的拔電再接電才會「上電後直接倒數」;軟體重開不會. 測試要模擬上電時先送序列指令 `powerontest`.
- **安全開關 GPIO21**(GG 2026-09-14 改):起飛程序(推飛機,網頁開始,上電自動倒數)照常開始,**按下安全開關才開始倒數**;
  起飛程序中按過一次就記住(開始當下按著也算,所以飛場應急短路照樣能飛),倒數中被碰到重新放穩不必再按. 沒按時燈慢閃等待,事件 28.
  **等待上限**(GG 2026-09-14,設定 armWait 出廠 3 分鐘,1~30):起飛程序開始後超過上限沒按就取消(上電自動倒數則這次通電不再倒數),按過就不再計時.
  開發板沒接開關:測試用序列指令 `armsw 1` 模擬一直按著(lp_test.protect() 已自動送;覆寫存 RTC,軟體重開保留,拔電清除),收尾 `armsw off`.
  測等待上限用 `armwait <秒>` 縮短(同樣存 RTC),收尾 `armwait off`.
- 硬體(GG 2026-09-14):板上降壓板支援 6~9V 的電變 BEC;收腳舵機從 BEC 分電,不經過控制器;USB 可以和電池同時接(二極體反接保護).
- 測網頁:電腦無線網卡有臨時設定檔 `HappySuperGG_Plane`,`netsh wlan connect name=HappySuperGG_Plane interface="Wi-Fi"`
  (電腦上網走有線,連熱點不影響). 板子已連家用 WiFi,平常用 lineplane.local.
- **序列埠工具一律 `dtr=False, rts=False` 再開,而且只開一次**:Windows 開 COM 會切 DTR/RTS,C3 原生 USB 當成重置,板子會重開.
- **GG 會在板子上調參數實測,板上設定是他的資料**. 會改設定的測試一律先 `board_backup.require_idle()` + `backup()`,結束 `restore()`
  並 `diff()` 比對;板子不在待機或有未儲存變更就不測. 絕不可「回預設並儲存」當收尾. 燒錄前先 `board_backup.py save`.
  **燒錄例外(GG 2026-09-14)**:板上有未儲存變更時照樣直接燒,不用問(目前板上都是測試資料);做法是先備份 RAM 值,燒完用 setmany 放回不儲存. 起飛程序/馬達運轉中仍不燒.
- **web_page.h 的 HTML/JS 修改用檔案編輯工具**,不要用 PowerShell 字串替換:引號跳脫與陣列串接多次靜默改壞內容(空字串變單引號,整張卡片消失).
- **設定備份碼**(2026-09-14,docs/設定備份碼設計_2026-09-14.md):新增參數或放寬參數範圍時,要在 src/settings_backup.cpp **開新世代**把欄位接在後面,
  不可改已定案世代的表(舊備份碼會解錯). 開機序列埠印 `backup codec ok` 才表示編碼表涵蓋全部參數.
- **設定結構改版要寫轉移**(settings.cpp 的 loadShared/loadProfile),不可讓使用者設定回預設. 改完燒錄後用 `board_backup.py diff` 驗證.
- 回歸測試:tools/settings_api_test.py(設定 API),tools/flight_sm_test.py(狀態機,板子放桌上),tools/web_load_test.py(網頁負載計時),
  tools/curve_ui_test.py(曲線圖拖曳,CDP;要用 penv 的 python,內建 websockets),
  tools/sim_attitude.py / sim_impact.py(姿態與觸地偵測模擬). 測試會改寫設定,結束時回預設.
- 設計取捨參考 GG 電腦上 arduino_save 資料夾裡的舊專案 `OpenActiveSuspension_ESP32C3_WiFi`(車頭搖晃程式)
  的 CLAUDE.md(硬體陷阱那段特別重要),但那份寫的「GG 用 Arduino IDE」「不做 OTA」不適用本專案.

## 已知的關鍵決策
- 控制迴圈是獨立的 FreeRTOS 工作(200Hz),**優先權 24 = 系統最高,高過 WiFi 驅動**. 優先權 5 時實測
  手機連上熱點會卡住控制 32ms. 網頁/WiFi/OTA 在 Arduino loop. 不可把 I2C 或電變寫入放回 loop,
  控制工作裡不可有忙等迴圈.
- WiFi 設定用獨立 NVS 命名空間 `lpwifi`,不放進飛行設定結構.
- 副廠 MPU6050 誤差大(開發板靜止讀 1.12g):任何判斷不要依賴「剛好 1g」.
- 姿態用向心力補償的 Mahony,飛行 Kp 0.3. 依據是 tools/sim_attitude.py 的模擬,改演算法先跑模擬.
- 電變訊號用 GPIO4(重置期間無毛刺). 分割表 min_spiffs(OTA 需要兩個插槽).
