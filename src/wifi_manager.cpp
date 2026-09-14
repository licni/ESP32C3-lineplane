// 版本流水號: r6 (2026-09-14) 起飛程序與飛行中暫停功率試用與設定試用的計時,退回延後到落地(安全審查 B5),事件 27
// 舊: r5 (2026-09-14) 無線燒錄等資料逾時 1 → 5 秒(低發射功率時中途卡住就放棄)
// 舊: r4 (2026-09-14) 無線燒錄(ArduinoOTA)接韌體更新保護:寫入中擋起飛,寫完記預期開機分區
// 舊: r3 (2026-09-14) 家用 WiFi 斷線重連,超過等待秒數改開熱點;設定保護:發射功率試用 15 秒,網頁儲存的設定重開後 3 分鐘內要確認否則退回;連續開關電 3 次回出廠
// 舊: r2 (2026-09-13) 熱點名稱後綴(NVS 鍵 apsfx,驗證長度/空白/UTF-8);熱點密碼固定
// 舊: r1 (2026-09-13) 初版:STA 掃描挑最強節點,逾時退 AP,mDNS,ArduinoOTA,設定存 NVS
#include "wifi_manager.h"
#include <WiFi.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <Preferences.h>
#include "control.h"
#include "event_log.h"
#include "fw_update.h"
#include "esp_system.h"

static const char *const PREF_NAMESPACE = "lpwifi";
static const IPAddress AP_IP(192, 168, 4, 1);
static const IPAddress AP_SUBNET(255, 255, 255, 0);
static const uint32_t SCAN_TIMEOUT_MS = 6000;

static WifiConfig config;
static WifiState state = WIFI_STATE_AP;
static uint32_t staStartMs = 0;
static uint32_t phaseEndMs = 0;
static bool servicesStarted = false;

// STA 連線的內部階段. 對外一律是「連線中」,顯示端不必多認一種狀態.
enum StaPhase : uint8_t { PHASE_SCAN = 0, PHASE_BSSID, PHASE_GENERIC };
static StaPhase phase = PHASE_SCAN;

bool wifiHostIsValid(const char *name) {
  // RFC1035 標籤:英數與連字號,不可頭尾為連字號.
  const size_t n = strlen(name);
  if (n == 0 || n >= MDNS_HOST_BUFFER || name[0] == '-' || name[n - 1] == '-') return false;
  for (size_t i = 0; i < n; ++i)
    if (!isalnum((unsigned char)name[i]) && name[i] != '-') return false;
  return true;
}

const char *wifiApSuffixError(const char *s) {
  const size_t n = strlen(s);
  if (n > WIFI_AP_SUFFIX_MAX_BYTES) return "apsfxlong";
  if (n && (s[0] == ' ' || s[n - 1] == ' ')) return "apsfxspace";   // 頭尾空白在手機上看不出來,容易連錯
  for (size_t i = 0; i < n;) {
    const uint8_t c = (uint8_t)s[i];
    if (c < 0x20 || c == 0x7F) return "apsfxbad";
    // UTF-8:確認多位元組字完整(中文一字 3 位元組)
    const size_t len = c < 0x80 ? 1 : (c >> 5) == 0x6 ? 2 : (c >> 4) == 0xE ? 3 : (c >> 3) == 0x1E ? 4 : 0;
    if (!len || i + len > n) return "apsfxbad";
    for (size_t k = 1; k < len; ++k)
      if (((uint8_t)s[i + k] >> 6) != 0x2) return "apsfxbad";
    i += len;
  }
  return nullptr;
}

static char activeApSsid[WIFI_SSID_BUFFER] = {0};

String wifiApSsid(bool saved) {
  if (!saved && activeApSsid[0]) return String(activeApSsid);
  return String(WIFI_AP_SSID) + config.apSuffix;
}

// --- 設定保護(GG 2026-09-14:裝進飛機後插不了 USB,WiFi 連不上板子就廢了) ---------------------------
// 1. 試用確認:網頁改發射功率 15 秒內沒按「保持」退回;網頁儲存 WiFi 設定並重開後,WiFi 就緒 3 分鐘內沒按「保持」,
//    改回上一次的設定(存在 NVS 的 b_ 開頭鍵)並重啟 WiFi(不重開板子).
// 2. 開關電救援:連續 3 次上電都在 5 秒內斷電 → WiFi 設定回出廠. 只算真的斷電上電(ESP_RST_POWERON).
static const uint32_t TXP_TRIAL_MS = 15000;
static const uint32_t BOOT_TRIAL_MS = 180000;
static const uint32_t RESCUE_WINDOW_MS = 5000;
static const uint8_t RESCUE_BOOTS = 3;
static const char *const CONFIG_KEYS[] = {"ssid", "pw", "host", "tmo", "forceap", "txp", "apsfx"};

static uint8_t liveTxp = 0;
static uint8_t txpPrev = 0;
static uint32_t txpTrialUntilMs = 0;
static bool bootTrial = false;
static uint32_t bootTrialStartMs = 0;   // WiFi 就緒(連上家用或開熱點)才開始計時
static bool bootCountPending = false;
static uint32_t staLostMs = 0;          // 家用 WiFi 斷線的時刻(0 = 沒斷)
static uint32_t staRetryMs = 0;
static bool staTestBlock = false;       // 測試用:斷線後不重連,驗證「斷線太久改開熱點」
static uint32_t lastTickMs = 0;         // 上一次 wifiTick(起飛程序與飛行中暫停試用計時用)
static bool deferLoggedTxp = false, deferLoggedBoot = false;

void wifiTestDropSta(bool blockReconnect) {
  staTestBlock = blockReconnect;
  if (blockReconnect) WiFi.setAutoReconnect(false);
  WiFi.disconnect();
}
static bool rescueChecked = false;

// prefix:"" = 目前設定,"b_" = 試用前的備份(NVS 鍵名最長 15 字,"b_forceap" 可以)
static void readConfigKeys(Preferences &prefs, WifiConfig &c, const char *prefix) {
  memset(&c, 0, sizeof(c));
  c.staTimeoutSec = WIFI_STA_TIMEOUT_DEFAULT_S;
  c.txPowerDbm = WIFI_TX_POWER_DEFAULT_DBM;
  strncpy(c.host, DEFAULT_MDNS_HOST, sizeof(c.host) - 1);
  char key[16];
  const auto k = [&](const char *name) { snprintf(key, sizeof(key), "%s%s", prefix, name); return key; };
  // 先 isKey 再讀:不存在的鍵直接 getString 會印一行 NOT_FOUND 紅字,那是預期情況不是錯誤.
  if (prefs.isKey(k("ssid"))) prefs.getString(key, c.ssid, sizeof(c.ssid));
  if (prefs.isKey(k("pw"))) prefs.getString(key, c.password, sizeof(c.password));
  if (prefs.isKey(k("host"))) {
    char host[MDNS_HOST_BUFFER] = {0};
    prefs.getString(key, host, sizeof(host));
    if (wifiHostIsValid(host)) strncpy(c.host, host, sizeof(c.host) - 1);
  }
  const uint8_t tmo = prefs.isKey(k("tmo")) ? prefs.getUChar(key, WIFI_STA_TIMEOUT_DEFAULT_S) : WIFI_STA_TIMEOUT_DEFAULT_S;
  if (tmo >= WIFI_STA_TIMEOUT_MIN_S && tmo <= WIFI_STA_TIMEOUT_MAX_S) c.staTimeoutSec = tmo;
  c.forceAp = prefs.isKey(k("forceap")) ? prefs.getBool(key, false) : false;
  const uint8_t txp = prefs.isKey(k("txp")) ? prefs.getUChar(key, WIFI_TX_POWER_DEFAULT_DBM) : WIFI_TX_POWER_DEFAULT_DBM;
  if (txp >= WIFI_TX_POWER_MIN_DBM && txp <= WIFI_TX_POWER_MAX_DBM) c.txPowerDbm = txp;
  if (prefs.isKey(k("apsfx"))) {
    char sfx[WIFI_SSID_BUFFER] = {0};
    prefs.getString(key, sfx, sizeof(sfx));
    if (!wifiApSuffixError(sfx)) strncpy(c.apSuffix, sfx, sizeof(c.apSuffix) - 1);   // 不合法就用固定開頭
  }
}

static bool writeConfigKeys(Preferences &prefs, const WifiConfig &c, const char *prefix) {
  char key[16];
  const auto k = [&](const char *name) { snprintf(key, sizeof(key), "%s%s", prefix, name); return key; };
  bool ok = prefs.putString(k("ssid"), c.ssid) == strlen(c.ssid);
  ok = (prefs.putString(k("pw"), c.password) == strlen(c.password)) && ok;
  ok = (prefs.putString(k("host"), c.host) == strlen(c.host)) && ok;
  ok = prefs.putUChar(k("tmo"), c.staTimeoutSec) && ok;
  ok = prefs.putBool(k("forceap"), c.forceAp) && ok;
  ok = prefs.putUChar(k("txp"), c.txPowerDbm) && ok;
  ok = (prefs.putString(k("apsfx"), c.apSuffix) == strlen(c.apSuffix)) && ok;
  return ok;
}

static void removeBackupKeys(Preferences &prefs) {
  char key[16];
  for (const char *name : CONFIG_KEYS) {
    snprintf(key, sizeof(key), "b_%s", name);
    if (prefs.isKey(key)) prefs.remove(key);
  }
  if (prefs.isKey("trial")) prefs.remove("trial");
}

static void loadConfig() {
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, true)) {   // 全新板子沒有這個命名空間,用預設值
    WifiConfig d;
    memset(&d, 0, sizeof(d));
    d.staTimeoutSec = WIFI_STA_TIMEOUT_DEFAULT_S;
    d.txPowerDbm = WIFI_TX_POWER_DEFAULT_DBM;
    strncpy(d.host, DEFAULT_MDNS_HOST, sizeof(d.host) - 1);
    config = d;
    bootTrial = false;
    return;
  }
  readConfigKeys(prefs, config, "");
  bootTrial = prefs.isKey("trial") && prefs.getBool("trial", false);
  prefs.end();
}

// 開機時呼叫一次:連續上電計數. 5 秒後 wifiTick 歸零.
static void rescueCheckAtBoot() {
  if (rescueChecked) return;
  rescueChecked = true;
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return;
  uint8_t count = prefs.isKey("bootcnt") ? prefs.getUChar("bootcnt", 0) : 0;
  // 測試用:序列指令 rescuetest 讓下一次軟體重開也算一次上電(USB 供電的桌上板子沒辦法真的斷電)
  const bool testBoot = prefs.isKey("bctest") && prefs.getBool("bctest", false);
  if (testBoot) prefs.remove("bctest");
  if (esp_reset_reason() == ESP_RST_POWERON || testBoot) {
    ++count;
    if (count >= RESCUE_BOOTS) {
      for (const char *name : CONFIG_KEYS)
        if (prefs.isKey(name)) prefs.remove(name);
      removeBackupKeys(prefs);
      count = 0;
      Serial.println(F("WiFi rescue: 3 quick power cycles -> WiFi settings reset to factory (AP)"));
      eventLog(EV_WIFI, 1);
    }
    prefs.putUChar("bootcnt", count);
    bootCountPending = count > 0;
  } else if (count) {
    prefs.putUChar("bootcnt", 0);   // 軟體重開/OTA 打斷計數
  }
  prefs.end();
}

const WifiConfig &wifiConfig() { return config; }

const char *wifiSaveConfig(const WifiConfig &cfg, bool trial) {
  if (strlen(cfg.password) > 0 && strlen(cfg.password) < 8) return "pwshort";
  if (cfg.staTimeoutSec < WIFI_STA_TIMEOUT_MIN_S || cfg.staTimeoutSec > WIFI_STA_TIMEOUT_MAX_S) return "tmo";
  if (cfg.txPowerDbm < WIFI_TX_POWER_MIN_DBM || cfg.txPowerDbm > WIFI_TX_POWER_MAX_DBM) return "txp";
  if (!wifiHostIsValid(cfg.host)) return "hostbad";
  if (const char *e = wifiApSuffixError(cfg.apSuffix)) return e;
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return "savefail";
  bool ok = true;
  if (trial) {
    // 備份「上一次確認過」的設定. 已經在試用中(改了還沒確認又改)就保留最早那份,不拿沒確認過的設定當備份.
    if (!(prefs.isKey("trial") && prefs.getBool("trial", false))) {
      WifiConfig prev;
      readConfigKeys(prefs, prev, "");
      ok = writeConfigKeys(prefs, prev, "b_") && ok;
    }
    ok = prefs.putBool("trial", true) && ok;
  } else {
    removeBackupKeys(prefs);   // USB 指令直接生效,不需要確認
    bootTrial = false;
    bootTrialStartMs = 0;
  }
  ok = writeConfigKeys(prefs, cfg, "") && ok;
  prefs.end();
  if (!ok) return "savefail";
  config = cfg;
  return nullptr;
}

static void applyTxPowerRaw(uint8_t dbm) {
  // 函式庫以 0.25dBm 為單位. 必須在 WiFi.mode() 之後呼叫,mode() 會把功率重設回預設.
  WiFi.setTxPower((wifi_power_t)(dbm * 4));
  liveTxp = dbm;
}

void wifiApplyTxPower(uint8_t dbm) {
  if (dbm < WIFI_TX_POWER_MIN_DBM || dbm > WIFI_TX_POWER_MAX_DBM) return;
  txpTrialUntilMs = 0;   // 直接指定(開機,USB 指令)就不是試用
  applyTxPowerRaw(dbm);
}

bool wifiTryTxPower(uint8_t dbm) {
  if (dbm < WIFI_TX_POWER_MIN_DBM || dbm > WIFI_TX_POWER_MAX_DBM) return false;
  if (!txpTrialUntilMs) txpPrev = liveTxp;   // 連續拖動時退回的是試用前最後確認的值
  applyTxPowerRaw(dbm);
  txpTrialUntilMs = (millis() + TXP_TRIAL_MS) | 1;
  return true;
}

void wifiKeep() {
  txpTrialUntilMs = 0;
  if (bootTrial) {
    Preferences prefs;
    if (prefs.begin(PREF_NAMESPACE, false)) {
      removeBackupKeys(prefs);
      prefs.end();
    }
    bootTrial = false;
    bootTrialStartMs = 0;
    Serial.println(F("WiFi settings confirmed"));
  }
}

void wifiTrialStatus(float &txpRemainS, bool &bootPending, float &bootRemainS) {
  const uint32_t now = millis();
  txpRemainS = txpTrialUntilMs && (int32_t)(txpTrialUntilMs - now) > 0 ? (txpTrialUntilMs - now) / 1000.0f : 0;
  bootPending = bootTrial;
  // 起點可能是 millis()|1 比現在大 1:相減前先確認不是負的(否則溢位成很大,剩餘顯示 0)
  const int32_t elapsed = bootTrialStartMs ? (int32_t)(now - bootTrialStartMs) : 0;
  bootRemainS = bootTrial && bootTrialStartMs ? max(0.0f, ((float)BOOT_TRIAL_MS - (float)max((int32_t)0, elapsed)) / 1000.0f) : -1;
}

uint8_t wifiLiveTxPower() { return liveTxp; }

void wifiRescueTestArm() {
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return;
  prefs.putBool("bctest", true);
  prefs.end();
}

static void wifiRestart();

static void startServices() {
  // mDNS 要綁在已經有位址的網卡上,所以在取得 IP(或 AP 啟動)之後才註冊.
  MDNS.end();
  if (MDNS.begin(config.host)) {
    MDNS.addService("http", "tcp", 80);
    Serial.printf("mDNS http://%s.local/\n", config.host);
  } else {
    Serial.println(F("mDNS start failed"));
  }
  if (!servicesStarted) {
    ArduinoOTA.setHostname(config.host);
    ArduinoOTA.setPassword(OTA_PASSWORD);
    // 等資料逾時 1 秒 → 5 秒:發射功率 2dBm 時實測燒錄中途卡住超過 1 秒就放棄(2026-09-14 fw_fail_test). 只在待機時會走到.
    ArduinoOTA.setTimeout(5000);
    // 開始寫快閃前再確認一次:只有待機狀態允許. 寫快閃期間快取關閉,控制迴圈會停住.
    ArduinoOTA.onStart([]() {
      if (!controlOtaAllowed()) {
        Serial.println(F("OTA refused: not idle"));
        ESP.restart();   // ArduinoOTA 沒有中止的 API;待機以外本來就不該走到這裡
      }
      Serial.println(F("OTA start"));
      fwUpdateStarted(FWS_ARDUINO_OTA);   // 寫入期間拒絕起飛與手動輸出
    });
    ArduinoOTA.onEnd([]() {
      Serial.println(F("OTA done, rebooting"));
      fwUpdateFlashed(true);   // 記下預期開機分區:新韌體沒確認被退回時,舊韌體會提示
    });
    ArduinoOTA.onError([](ota_error_t e) {
      Serial.printf("OTA error %u\n", (unsigned)e);
      fwUpdateFlashed(false);
    });
    ArduinoOTA.begin();
    servicesStarted = true;
  }
}

static void startAp() {
  MDNS.end();   // 從已連線的 STA 切到熱點(斷線太久)時,同 wifiRestart:切換網卡前先停 mDNS
  WiFi.mode(WIFI_AP);
  wifiApplyTxPower(config.txPowerDbm);
  WiFi.softAPConfig(AP_IP, AP_IP, AP_SUBNET);
  snprintf(activeApSsid, sizeof(activeApSsid), "%s%s", WIFI_AP_SSID, config.apSuffix);
  WiFi.softAP(activeApSsid, WIFI_AP_PASSWORD);   // 密碼固定
  state = WIFI_STATE_AP;
  if (bootTrial && !bootTrialStartMs) bootTrialStartMs = millis() | 1;   // 熱點開好,使用者可以連進來確認了
  startServices();
  Serial.printf("AP SSID=%s IP=%s\n", activeApSsid, WiFi.softAPIP().toString().c_str());
}

void wifiBegin() {
  rescueCheckAtBoot();
  loadConfig();
  if (config.forceAp || config.ssid[0] == '\0') {
    startAp();
    return;
  }
  WiFi.mode(WIFI_STA);
  wifiApplyTxPower(config.txPowerDbm);
  // 關閉 modem sleep:預設會在 beacon 之間關無線電,別的裝置送來的 ARP/TCP SYN 要等它醒來,
  // 瀏覽器常常連線逾時(參考專案 2026-09-02 的根因).
  WiFi.setSleep(false);
  // 先掃描再連:mesh 環境每個節點廣播同一個 SSID,直接 begin 會連上先回應的那台,
  // 常是遠端節點. 非同步掃描由 wifiTick() 推進,不卡開機.
  WiFi.scanNetworks(true);
  phase = PHASE_SCAN;
  state = WIFI_STATE_CONNECTING;
  staStartMs = millis();
  phaseEndMs = staStartMs + SCAN_TIMEOUT_MS;
  Serial.printf("STA scanning for %s\n", config.ssid);
}

static bool connectToStrongest(int16_t found) {
  int16_t best = -1;
  int32_t bestRssi = 0;
  for (int16_t i = 0; i < found; ++i) {
    if (WiFi.SSID(i) != config.ssid) continue;
    if (best < 0 || WiFi.RSSI(i) > bestRssi) {
      best = i;
      bestRssi = WiFi.RSSI(i);
    }
  }
  if (best < 0) return false;
  Serial.printf("STA best node RSSI=%ddBm ch=%d of %d networks\n", (int)bestRssi, (int)WiFi.channel(best), (int)found);
  WiFi.begin(config.ssid, config.password, WiFi.channel(best), WiFi.BSSID(best));
  return true;
}

static void fallbackToGeneric() {
  Serial.println(F("STA -> generic connect"));
  WiFi.disconnect();
  WiFi.begin(config.ssid, config.password);
  phase = PHASE_GENERIC;
}

// 退回試用前的設定並重啟 WiFi. 只重啟無線網路,控制工作(飛行)不受影響.
static void revertBootTrial() {
  Preferences prefs;
  if (prefs.begin(PREF_NAMESPACE, false)) {
    WifiConfig prev;
    readConfigKeys(prefs, prev, "b_");
    writeConfigKeys(prefs, prev, "");
    removeBackupKeys(prefs);
    prefs.end();
  }
  bootTrial = false;
  bootTrialStartMs = 0;
  Serial.println(F("WiFi settings not confirmed -> reverted to previous, restarting WiFi"));
  eventLog(EV_WIFI, 2);
  wifiRestart();
}

static void wifiRestart() {
  // 先停 mDNS 再關 WiFi:mDNS 還綁在舊網卡時關掉 WiFi,mDNS 下一次加入多播群組會碰到已釋放的網卡而當機
  // (2026-09-14 測試:試用退回時 Guru Meditation,esp_netif_is_netif_up ← mdns join_group,板子重開. 飛行中重開 = 馬達停).
  MDNS.end();
  WiFi.scanDelete();
  WiFi.disconnect(true);
  WiFi.softAPdisconnect(true);
  WiFi.mode(WIFI_OFF);
  activeApSsid[0] = 0;
  wifiBegin();
}

void wifiTick() {
  if (servicesStarted) {
    // 待機以外不處理 OTA 請求:連握手都不回,PlatformIO 端會直接顯示連不上.
    if (controlOtaAllowed()) ArduinoOTA.handle();
  }
  const uint32_t nowMs = millis();
  if (bootCountPending && nowMs >= RESCUE_WINDOW_MS) {
    // 通電超過 5 秒:不是在做「連續開關電救援」,計數歸零
    bootCountPending = false;
    Preferences prefs;
    if (prefs.begin(PREF_NAMESPACE, false)) {
      prefs.putUChar("bootcnt", 0);
      prefs.end();
    }
  }
  // 起飛程序與飛行中:試用計時暫停(安全審查 B5). 退回會改發射功率或重啟 WiFi 並寫快閃,空中不做;
  // 落地後剩下的試用時間繼續算,使用者還來得及按「保持」.
  {
    const bool locked = controlSettingsLocked();
    const uint32_t delta = lastTickMs ? nowMs - lastTickMs : 0;
    lastTickMs = nowMs;
    if (locked && delta) {
      if (txpTrialUntilMs) {
        txpTrialUntilMs += delta;
        if (!deferLoggedTxp) {
          deferLoggedTxp = true;
          eventLog(EV_WIFI_DEFER, 1);
        }
      }
      if (bootTrial && bootTrialStartMs) {
        bootTrialStartMs += delta;
        if (!deferLoggedBoot) {
          deferLoggedBoot = true;
          eventLog(EV_WIFI_DEFER, 2);
        }
      }
    }
    if (!locked) deferLoggedTxp = deferLoggedBoot = false;
  }
  if (txpTrialUntilMs && (int32_t)(nowMs - txpTrialUntilMs) >= 0) {
    txpTrialUntilMs = 0;
    applyTxPowerRaw(txpPrev);
    Serial.printf("WiFi tx power not confirmed -> back to %udBm\n", (unsigned)txpPrev);
    eventLog(EV_WIFI, 3, txpPrev);
  }
  if (bootTrial && bootTrialStartMs && (int32_t)(nowMs - bootTrialStartMs) >= (int32_t)BOOT_TRIAL_MS) {
    revertBootTrial();
    return;
  }
  // 家用 WiFi 中途斷線:每 5 秒重連一次,超過等待秒數還連不回來就改開自身熱點.
  // r3 以前斷線後停在「已連線 IP 0.0.0.0」,既不重連也不開熱點,只能重新上電(2026-09-14 實際遇到).
  if (state == WIFI_STATE_STA) {
    if (WiFi.status() == WL_CONNECTED) {
      staLostMs = 0;
    } else if (!staLostMs) {
      staLostMs = nowMs | 1;
      staRetryMs = nowMs;
      Serial.println(F("STA lost -> reconnecting"));
      if (!staTestBlock) WiFi.reconnect();
    } else if (nowMs - staLostMs >= (uint32_t)config.staTimeoutSec * 1000UL) {
      staLostMs = 0;
      staTestBlock = false;
      Serial.println(F("STA lost too long -> AP"));
      eventLog(EV_WIFI, 4, config.staTimeoutSec);
      startAp();
    } else if (nowMs - staRetryMs >= 5000 && !staTestBlock) {
      staRetryMs = nowMs;
      WiFi.reconnect();
    }
  }
  if (state != WIFI_STATE_CONNECTING) return;

  if (WiFi.status() == WL_CONNECTED) {
    state = WIFI_STATE_STA;
    if (bootTrial && !bootTrialStartMs) bootTrialStartMs = millis() | 1;   // 連上家用 WiFi,使用者可以連進來確認了
    startServices();
    Serial.printf("STA connected IP=%s RSSI=%d\n", WiFi.localIP().toString().c_str(), (int)WiFi.RSSI());
    return;
  }

  // 總逾時涵蓋掃描與所有嘗試:分階段各自計時的話最壞會拖到設定值的好幾倍.
  const uint32_t now = millis();
  const uint32_t totalMs = (uint32_t)config.staTimeoutSec * 1000UL;
  const bool overallExpired = (now - staStartMs) >= totalMs;
  const bool phaseExpired = (int32_t)(now - phaseEndMs) >= 0;

  if (phase == PHASE_SCAN) {
    const int16_t found = WiFi.scanComplete();
    if (found == WIFI_SCAN_RUNNING && !phaseExpired && !overallExpired) return;
    if (found >= 0) {
      const bool started = connectToStrongest(found);
      WiFi.scanDelete();
      if (!started) {
        // 掃得到東西但沒有同名 SSID:網路不在附近,再等也沒用,直接開熱點.
        Serial.println(F("STA ssid not found -> AP"));
        startAp();
        return;
      }
      phase = PHASE_BSSID;
      phaseEndMs = staStartMs + totalMs / 2;   // 指定節點只給一半時間,留後路
      return;
    }
    WiFi.scanDelete();
    fallbackToGeneric();
    return;
  }
  if (phase == PHASE_BSSID && phaseExpired && !overallExpired) {
    fallbackToGeneric();
    return;
  }
  if (overallExpired) {
    Serial.println(F("STA timeout -> AP"));
    startAp();
  }
}

WifiState wifiState() { return state; }

String wifiIpText() {
  if (state == WIFI_STATE_STA) return WiFi.localIP().toString();
  if (state == WIFI_STATE_AP) return WiFi.softAPIP().toString();
  return String("");
}

int32_t wifiRssi() { return state == WIFI_STATE_STA ? WiFi.RSSI() : 0; }

uint16_t wifiStaCountdownSeconds() {
  if (state != WIFI_STATE_CONNECTING) return 0;
  const uint32_t totalMs = (uint32_t)config.staTimeoutSec * 1000UL;
  const uint32_t elapsed = millis() - staStartMs;
  return elapsed >= totalMs ? 0 : (uint16_t)((totalMs - elapsed + 999) / 1000);
}
