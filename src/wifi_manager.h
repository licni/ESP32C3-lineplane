// 版本流水號: r3 (2026-09-14) 設定保護:試用確認與退回,連續開關電救援
// 舊: r2 (2026-09-13) 熱點名稱固定開頭 HappySuperGG_Plane + 可改後綴(最多 14 位元組);熱點密碼固定
// 舊: r1 (2026-09-13) 初版:STA 掃描挑最強節點,逾時退 AP,mDNS,ArduinoOTA,設定存 NVS
#pragma once
#include <Arduino.h>
// ============================================================================
// WiFi 連線,mDNS,ArduinoOTA. 只在 Arduino loop 呼叫.
// WiFi 設定用獨立的 NVS 鍵各存一筆,不放進飛行設定結構:飛行設定改版時 WiFi 不會跟著失效,
// 裝置也就不會莫名其妙退回熱點.
// ============================================================================

// --- 自身熱點(AP) -----------------------------------------------------------
// 開機時連不上家用 WiFi(或使用者選擇一律用熱點)就開這個熱點,手機直接連進來調整.
// 名稱開頭是 GG 的個人署名,固定;使用者只能在後面接字(GG 2026-09-13:例如 HappySuperGG_Plane3,同場多架飛機分得出來).
// 密碼一律固定不能改(GG:避免使用者輸入錯誤或忘記,連不上就救不回來). 密碼依 WPA2 規定至少 8 碼.
const char *const WIFI_AP_SSID = "HappySuperGG_Plane";     // 固定開頭
const uint8_t WIFI_AP_PREFIX_LEN = 18;
const uint8_t WIFI_AP_SUFFIX_MAX_BYTES = 32 - WIFI_AP_PREFIX_LEN;   // SSID 上限 32 位元組,後綴最多 14
const char *const WIFI_AP_PASSWORD = "12345678";
// ArduinoOTA 密碼(PlatformIO 無線燒錄用),與熱點密碼相同,好記.
const char *const OTA_PASSWORD = "12345678";
const char *const DEFAULT_MDNS_HOST = "lineplane";

const uint8_t WIFI_SSID_BUFFER = 33;    // SSID 最長 32 位元組 + 結尾
const uint8_t WIFI_PASS_BUFFER = 64;    // WPA2 密碼最長 63 位元組 + 結尾
const uint8_t MDNS_HOST_BUFFER = 32;
const uint8_t WIFI_STA_TIMEOUT_MIN_S = 10;
const uint8_t WIFI_STA_TIMEOUT_MAX_S = 120;
const uint8_t WIFI_STA_TIMEOUT_DEFAULT_S = 30;
// SuperMini 的 PCB 天線匹配很差,功率開大時功放會壓垮自己的接收端,症狀是「連得上但一忙就停頓」.
// 參考專案實測 5dBm 以上開始不良,預設壓到 5dBm.
const uint8_t WIFI_TX_POWER_MIN_DBM = 2;
const uint8_t WIFI_TX_POWER_MAX_DBM = 20;
const uint8_t WIFI_TX_POWER_DEFAULT_DBM = 5;

struct WifiConfig {
  char ssid[WIFI_SSID_BUFFER];
  char password[WIFI_PASS_BUFFER];
  char host[MDNS_HOST_BUFFER];
  uint8_t staTimeoutSec;
  bool forceAp;
  uint8_t txPowerDbm;
  char apSuffix[WIFI_AP_SUFFIX_MAX_BYTES + 1];   // 熱點名稱接在固定開頭後面的字(可空白)
};

enum WifiState : uint8_t { WIFI_STATE_CONNECTING = 0, WIFI_STATE_STA, WIFI_STATE_AP };

void wifiBegin();
void wifiTick();
const WifiConfig &wifiConfig();
// 驗證並存檔. 回傳 nullptr 表示成功,否則是錯誤代碼字串(網頁查表顯示).
// trial = true(網頁):存檔並標記試用,重開機後 WiFi 就緒 3 分鐘內沒有 wifiKeep() 就退回上一次的設定.
// trial = false(USB 序列指令):直接生效,清掉試用.
const char *wifiSaveConfig(const WifiConfig &cfg, bool trial = false);
// 發射功率即時生效(不存檔,取消試用). 開機與 USB 指令用.
void wifiApplyTxPower(uint8_t dbm);
// 網頁拉桿:試用發射功率,15 秒內沒有 wifiKeep() 就退回試用前的值. 超出範圍回 false.
bool wifiTryTxPower(uint8_t dbm);
// 網頁「保持」:確認目前的發射功率與重開後試用中的 WiFi 設定.
void wifiKeep();
// 試用狀態:發射功率試用剩餘秒數(0 = 沒有),設定試用中,設定試用剩餘秒數(-1 = 還沒開始計時或沒有)
void wifiTrialStatus(float &txpRemainS, bool &bootPending, float &bootRemainS);
uint8_t wifiLiveTxPower();
// 測試用:下一次軟體重開也算一次「上電」(連續開關電救援的計數)
void wifiRescueTestArm();
// 測試用:讓家用 WiFi 斷線. blockReconnect = true 時不重連(驗證斷線太久改開熱點)
void wifiTestDropSta(bool blockReconnect);
WifiState wifiState();
String wifiIpText();
int32_t wifiRssi();
uint16_t wifiStaCountdownSeconds();
bool wifiHostIsValid(const char *name);
// 熱點名稱後綴:最多 14 位元組,不可有控制字元,頭尾不可是空白,UTF-8 不可截在半個字. 回傳 nullptr 表示可用.
const char *wifiApSuffixError(const char *suffix);
// 完整熱點名稱(固定開頭 + 後綴). saved = true 取存檔值(下次開機用),false 取目前正在廣播的名稱.
String wifiApSsid(bool saved);
