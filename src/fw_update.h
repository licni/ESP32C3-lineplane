// 版本流水號: r4 (2026-09-14) 韌體身分標記 FW_ID_PREFIX + 上傳檔案掃描(fwIdScan*):網頁上傳找不到標記就不切換
// 舊: r3 (2026-09-14) 版本逐段比數字(fwVersionCompare),狀態加 remoteNewer;板子下載只裝比目前新的版本
// 舊: r2 (2026-09-14) 確認時限 WiFi 就緒後 300 → 60 秒,開機後上限 420 → 240 秒(GG)
// 舊: r1 (2026-09-14) 初版:更新鎖,新韌體確認與自動退回,板子自己下載更新(公開 GitHub 專案)
#pragma once
#include <Arduino.h>
#include "version.h"
// ============================================================================
// 韌體更新(GG 2026-09-14):板子送人後,對方在網頁「檢查更新」就能刷 GG 發布的新版.
//
// 三種更新方式共用這裡的保護:網頁上傳 firmware.bin,PlatformIO 無線燒錄,板子自己下載.
//  1. 只有待機可以開始(controlOtaAllowed);開始後到重開前「更新中」,拒絕起飛與手動輸出.
//  2. 新韌體第一次開機是「待確認」(ESP32 內建 rollback,framework 已開 CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE):
//     網頁打開後自動送確認 → 正式採用. WiFi 就緒後 FW_CONFIRM_WINDOW_S 秒內沒確認 → 自動退回舊版並重開.
//     確認前沒關機就重開或斷電,下次開機由開機程式直接退回舊版(ESP-IDF 行為).
//     待確認時不准起飛:飛行中觸發退回重開等於馬達停.
//  3. 下載:HTTPS(內建根憑證包驗證伺服器),檔案大小與 SHA-256 都要符合 manifest 才切換開機分區.
//     下載中斷或檔案不對,開機分區不變,板子繼續用舊版.
// 退回後舊韌體開機時會看到「上次更新沒有完成確認,已退回」(NVS lpfw 記錄預期的開機分區).
// ============================================================================

// WiFi 就緒後幾秒內要確認. GG 2026-09-14:5 分鐘太久,正常人不會等,家用 WiFi 隨時可連,1 分鐘連不上就算失敗.
// 實測網頁開著時板子重開回來 1 秒內就自動確認;手機螢幕關掉或切 App 超過 1 分鐘才回來,會退回(安全,再更新一次即可).
const uint16_t FW_CONFIRM_WINDOW_S = 60;
// 不管 WiFi 有沒有就緒,開機後最久等這麼久:家用 WiFi 連不上最多 120 秒改開熱點,再加確認時限與餘裕.
const uint16_t FW_CONFIRM_HARD_LIMIT_S = 240;
const size_t FW_NOTES_MAX = 400;                // 更新說明最長位元組(UTF-8)

// 韌體身分標記(GG 2026-09-14):韌體裡有一段「LPFWID1:ESP32C3-lineplane|版本|」.
// 網頁上傳的檔案一邊寫入一邊找,寫完沒找到就放棄不切換:拿錯成別的 ESP32-C3 程式時,格式,晶片,檢查碼都對,
// 只靠 ESP-IDF 的驗證擋不下來;而且那種程式開機會自己確認,不會退回,還可能亂動電變訊號腳.
// 允許上傳比目前舊的版本(退回舊版). 2026.09.14.16 和更早發布的版本沒有標記,不能用網頁上傳.
// 開頭大寫 L 在標記裡只出現一次,掃描比對失敗時不必回溯.
#define FW_ID_PREFIX "LPFWID1:ESP32C3-lineplane|"
void fwIdScanReset();
void fwIdScanFeed(const uint8_t *data, size_t len);
const char *fwIdScanVersion();   // 找到標記回檔案的版本字串,沒找到回 nullptr

enum FwCheckState : uint8_t {
  FWC_IDLE = 0,     // 還沒檢查
  FWC_CHECKING,     // 讀取 manifest 中
  FWC_CHECKED,      // 已讀到遠端版本(remoteNewer:網站版本比目前新,相同,或比較舊)
  FWC_DOWNLOADING,  // 下載並寫入中
  FWC_DONE,         // 寫入完成,即將重開機
  FWC_ERROR         // 失敗,原因在 err
};

// 事件 EV_FW 的 arg
enum FwEvent : uint8_t {
  FWE_CONFIRMED = 0,   // 新韌體已確認採用
  FWE_PENDING,         // 新韌體第一次開機,等待網頁確認
  FWE_ROLLED_BACK,     // 開機發現上次更新沒確認,已退回舊版
  FWE_STARTED,         // 開始更新. a = 來源(0 網頁上傳 / 1 無線燒錄 / 2 板子下載)
  FWE_FLASHED,         // 寫入完成,即將重開
  FWE_FAILED,          // 更新失敗(開機分區不變)
  FWE_TIMEOUT          // 待確認逾時,退回舊版並重開(重開後事件會清掉,實際看到的是下一次開機的 FWE_ROLLED_BACK)
};

enum FwSource : uint8_t { FWS_WEB_UPLOAD = 0, FWS_ARDUINO_OTA, FWS_DOWNLOAD };

struct FwStatus {
  uint8_t check;               // FwCheckState
  char err[20];                // 錯誤代碼(網頁查表)
  uint8_t progress;            // 下載進度 0~100
  bool busy;                   // 任何方式更新中
  bool pending;                // 新韌體待確認
  float confirmRemainS;        // 待確認剩餘秒數(-1 = 還沒開始計時或不在待確認)
  bool rolledBack;             // 這次開機是退回後的舊版
  char rolledBackFrom[24];     // 被退回的版本(網頁上傳/無線燒錄不知道版本時是空字串)
  char remoteVersion[24];
  int8_t remoteNewer;          // 1 = 網站版本比目前新(才可以安裝),0 = 相同,-1 = 網站版本比較舊(例如開發中的板子)
  uint32_t remoteSize;
  char notes[FW_NOTES_MAX + 1];
};

// setup() 裡,wifiBegin() 之前呼叫:判斷是不是待確認的新韌體,或上次更新被退回.
void fwUpdateBegin();
// loop() 呼叫:確認逾時退回,下載完成後重開.
void fwUpdateTick(uint32_t nowMs);
// 起飛擋住的原因:0 = 可以,1 = 更新中,2 = 新韌體待確認. 控制工作每拍讀(只讀 volatile 變數).
uint8_t fwUpdateBlockReason();
// 網頁上傳與無線燒錄:開始寫入時 fwUpdateStarted,寫完 fwUpdateFlashed(true),失敗 fwUpdateFlashed(false).
void fwUpdateStarted(FwSource src);
void fwUpdateFlashed(bool ok, const char *toVersion = "");
// 網頁確認新韌體. 不在待確認時也回 true.
bool fwUpdateConfirm();
// 開始檢查更新(背景讀 manifest). 回 nullptr = 已開始,否則錯誤代碼.
const char *fwUpdateCheckStart();
// 安裝檢查到的版本(背景下載). version 要和檢查到的一致,避免裝到別的版本;而且要比目前的版本新. 回 nullptr = 已開始.
const char *fwUpdateInstallStart(const char *version);
// 比較版本「年.月.日.序號」:a 比 b 新回 1,相同 0,比較舊 -1(逐段比數字,.10 比 .9 新).
int fwVersionCompare(const char *a, const char *b);
void fwUpdateGetStatus(FwStatus &out);
// 測試用(USB 序列指令 fwwin):這次開機的確認時限改成 sec 秒.
void fwUpdateTestSetWindow(uint16_t sec);
// 測試用(USB 序列指令 fwurl):暫時改讀別的 HTTPS 資料夾(例如公開專案的測試分支),空字串恢復正式來源. 不存檔.
bool fwUpdateTestSetBaseUrl(const char *url);
