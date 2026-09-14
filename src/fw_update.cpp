// 版本流水號: r6 (2026-09-14) 韌體身分標記 FW_ID_MARK 與上傳檔案掃描(網頁上傳拿錯成別的 ESP32-C3 程式時擋下)
// 舊: r5 (2026-09-14) 修正:網站版本和目前「不同」就當成新版(板子 .12,網站 .11 也說有新版本,GG 發現).
//   改成逐段比數字,只有網站版本比較新才可以下載安裝;狀態加 remoteNewer
// 舊: r4 (2026-09-14) manifest 的 file 可以是「一層資料夾/檔名」(公開專案韌體檔集中到 firmware/,GG)
// 舊: r3 (2026-09-14) 測試用更新來源(序列指令 fwurl,只存 RAM):驗證檢查碼不符,大小不符,檔案不存在,下載中斷
// 舊: r2 (2026-09-14) 修正:確認計時起點 nowMs|1 在偶數毫秒時相減溢位,新韌體一開機就被判逾時退回(約一半機率)
// 舊: r1 (2026-09-14) 初版:更新鎖,新韌體確認與自動退回,板子自己下載更新(公開 GitHub 專案)
#include "fw_update.h"
#include <HTTPClient.h>
#include <NetworkClientSecure.h>
#include <Preferences.h>
#include <Update.h>
#include <esp_ota_ops.h>
#include <esp_partition.h>
#include <mbedtls/sha256.h>
#include "control.h"
#include "event_log.h"
#include "settings.h"
#include "wifi_manager.h"

// ESP-IDF 內建的根憑證包(預建函式庫 libmbedtls 內),用來驗證 raw.githubusercontent.com 的憑證.
// 用整包而不是釘單一憑證:GitHub 換憑證機構時,送出去的板子才不會從此無法更新.
// sdkconfig 沒開 MBEDTLS_HAVE_TIME_DATE:不檢查憑證日期,板子不用先對時.
extern const uint8_t x509BundleStart[] asm("_binary_x509_crt_bundle_start");
extern const uint8_t x509BundleEnd[] asm("_binary_x509_crt_bundle_end");

// Arduino 核心預設開機就確認新韌體;改成延後,由網頁連上後 fwUpdateConfirm() 確認.
extern "C" bool verifyRollbackLater() { return true; }

static const char *const PREF_NAMESPACE = "lpfw";
static const uint32_t HTTP_TIMEOUT_MS = 15000;
static const uint32_t DOWNLOAD_STALL_MS = 20000;   // 下載中這麼久沒收到資料就放棄
static const uint32_t RESTART_DELAY_MS = 2500;     // 寫完後等網頁拿到「完成」再重開
static const size_t MANIFEST_MAX = 4096;

static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
static FwStatus st = {};
static volatile bool busyFlag = false;
static volatile bool pendingFlag = false;
static uint32_t wifiReadyMs = 0;
static uint16_t confirmWindowS = FW_CONFIRM_WINDOW_S;
static uint32_t restartAtMs = 0;
static TaskHandle_t task = nullptr;
static char remoteFile[64] = "";
// 測試用更新來源(只有 USB 序列指令 fwurl 能設,不存檔,重開即恢復正式來源). 空字串 = 正式來源 FW_UPDATE_BASE_URL.
static char testBaseUrl[160] = "";
static char remoteSha[65] = "";
static uint8_t dlBuf[2048];

#define LOCKED(stmt) do { portENTER_CRITICAL(&lock); stmt; portEXIT_CRITICAL(&lock); } while (0)

// --- 韌體身分標記 ------------------------------------------------------------------
// 標記本身就是比對用的字串(被掃描程式引用,連結器不會丟掉),放在韌體檔的唯讀資料段,檔案裡是連續的原始位元組.
__attribute__((used)) static const char FW_ID_MARK[] = FW_ID_PREFIX FW_VERSION "|";
static const size_t FW_ID_PREFIX_LEN = sizeof(FW_ID_PREFIX) - 1;
static size_t idMatch = 0;
static char idVer[24] = "";
static size_t idVerLen = 0;
static bool idFound = false;

void fwIdScanReset() {
  idMatch = 0;
  idVerLen = 0;
  idVer[0] = 0;
  idFound = false;
}

void fwIdScanFeed(const uint8_t *data, size_t len) {
  for (size_t i = 0; i < len && !idFound; ++i) {
    const char c = (char)data[i];
    if (idMatch < FW_ID_PREFIX_LEN) {
      if (c == FW_ID_MARK[idMatch]) ++idMatch;
      else idMatch = c == FW_ID_MARK[0] ? 1 : 0;
      idVerLen = 0;
    } else if (c == '|' && idVerLen > 0) {
      idVer[idVerLen] = 0;
      idFound = true;
    } else if (((c >= '0' && c <= '9') || c == '.') && idVerLen < sizeof(idVer) - 1) {
      idVer[idVerLen++] = c;
    } else {
      // 開頭對上但後面不是「版本|」(例如網頁程式裡的比對字串):重新找
      idMatch = c == FW_ID_MARK[0] ? 1 : 0;
      idVerLen = 0;
    }
  }
}

const char *fwIdScanVersion() { return idFound ? idVer : nullptr; }

static void setError(const char *code) {
  LOCKED(strlcpy(st.err, code, sizeof(st.err)); st.check = FWC_ERROR);
}

static void clearPrefs(Preferences &p) {
  p.remove("expect");
  p.remove("tover");
}

// --- 開機判斷 --------------------------------------------------------------------
void fwUpdateBegin() {
  Serial.printf("FW id %s\n", FW_ID_MARK);   // 整段標記都要留在韌體裡(網頁上傳靠它認檔案)
  const esp_partition_t *running = esp_ota_get_running_partition();
  esp_ota_img_states_t runState;
  const bool pending = running && esp_ota_get_state_partition(running, &runState) == ESP_OK && runState == ESP_OTA_IMG_PENDING_VERIFY;
  Preferences p;
  if (p.begin(PREF_NAMESPACE, false)) {
    if (p.isKey("expect")) {
      const uint8_t expect = p.getUChar("expect", 0xFF);
      if (running && running->subtype == expect) {
        if (!pending) clearPrefs(p);   // 新韌體已經確認過(或這版沒有待確認狀態)
      } else {
        // 開機的不是預期的分區:看預期的那個分區是不是被開機程式判定失敗(沒確認就重開 = ABORTED,逾時退回 = INVALID).
        // USB 燒錄會重寫 otadata,讀不到狀態,那種情況不算退回.
        const esp_partition_t *exp = esp_partition_find_first(ESP_PARTITION_TYPE_APP, (esp_partition_subtype_t)expect, nullptr);
        esp_ota_img_states_t expState;
        if (exp && esp_ota_get_state_partition(exp, &expState) == ESP_OK &&
            (expState == ESP_OTA_IMG_ABORTED || expState == ESP_OTA_IMG_INVALID)) {
          st.rolledBack = true;
          strlcpy(st.rolledBackFrom, p.getString("tover", "").c_str(), sizeof(st.rolledBackFrom));
          eventLog(EV_FW, FWE_ROLLED_BACK);
        }
        clearPrefs(p);
      }
    }
    p.end();
  }
  pendingFlag = pending;
  st.pending = pending;
  st.confirmRemainS = -1;
  if (pending) {
    eventLog(EV_FW, FWE_PENDING);
    Serial.println(F("FW new firmware pending confirmation (open the web page)"));
  }
}

uint8_t fwUpdateBlockReason() { return busyFlag ? 1 : (pendingFlag ? 2 : 0); }

void fwUpdateStarted(FwSource src) {
  busyFlag = true;
  LOCKED(st.busy = true);
  eventLog(EV_FW, FWE_STARTED, (float)src);
}

void fwUpdateFlashed(bool ok, const char *toVersion) {
  if (!ok) {
    busyFlag = false;
    LOCKED(st.busy = false);
    eventLog(EV_FW, FWE_FAILED);
    return;
  }
  // 記下預期的開機分區:下次開機若不是它(沒確認被退回),舊韌體就知道要提示
  const esp_partition_t *boot = esp_ota_get_boot_partition();
  Preferences p;
  if (boot && p.begin(PREF_NAMESPACE, false)) {
    p.putUChar("expect", (uint8_t)boot->subtype);
    p.putString("tover", toVersion ? toVersion : "");
    p.end();
  }
  eventLog(EV_FW, FWE_FLASHED);
}

bool fwUpdateConfirm() {
  if (!pendingFlag) return true;
  if (esp_ota_mark_app_valid_cancel_rollback() != ESP_OK) return false;
  pendingFlag = false;
  LOCKED(st.pending = false; st.confirmRemainS = -1);
  Preferences p;
  if (p.begin(PREF_NAMESPACE, false)) {
    clearPrefs(p);
    p.end();
  }
  eventLog(EV_FW, FWE_CONFIRMED);
  Serial.println(F("FW new firmware confirmed"));
  return true;
}

void fwUpdateTestSetWindow(uint16_t sec) {
  confirmWindowS = sec;
  wifiReadyMs = 0;   // 重新開始計時
}

void fwUpdateTick(uint32_t nowMs) {
  if (pendingFlag) {
    if (!wifiReadyMs && wifiState() != WIFI_STATE_CONNECTING) wifiReadyMs = nowMs | 1;
    float remain = -1;
    bool timeout = nowMs >= (uint32_t)FW_CONFIRM_HARD_LIMIT_S * 1000UL && confirmWindowS >= FW_CONFIRM_WINDOW_S;
    if (wifiReadyMs) {
      // wifiReadyMs 是 nowMs|1,偶數毫秒時比 nowMs 大 1:直接相減會變成 0xFFFFFFFF,當場判定逾時退回
      // (r1 實測:新韌體一開機就退回,約一半機率). 還沒到就當 0.
      const uint32_t elapsed = (int32_t)(nowMs - wifiReadyMs) > 0 ? nowMs - wifiReadyMs : 0;
      remain = elapsed >= confirmWindowS * 1000UL ? 0 : (confirmWindowS * 1000UL - elapsed) / 1000.0f;
      if (remain <= 0) timeout = true;
    }
    LOCKED(st.confirmRemainS = remain);
    // 待確認時不准起飛,正常一定在待機;還是再確認一次,飛行中絕不重開
    if (timeout && controlOtaAllowed()) {
      Serial.println(F("FW not confirmed in time -> rolling back to previous firmware"));
      eventLog(EV_FW, FWE_TIMEOUT);
      delay(100);
      esp_ota_mark_app_invalid_rollback_and_reboot();   // 成功就不會回來
      pendingFlag = false;                                // 沒有可退回的分區:放棄待確認,避免一直擋起飛
      LOCKED(st.pending = false; st.confirmRemainS = -1);
    }
  }
  if (restartAtMs && (int32_t)(nowMs - restartAtMs) >= 0 && controlOtaAllowed()) {
    Serial.println(F("FW download installed, rebooting"));
    delay(100);
    ESP.restart();
  }
}

// --- 下載 --------------------------------------------------------------------------
static bool validToken(const char *s, size_t maxLen, bool allowDotBin) {
  const size_t n = strlen(s);
  if (n == 0 || n > maxLen) return false;
  for (size_t i = 0; i < n; ++i) {
    const char c = s[i];
    if (!(isalnum((unsigned char)c) || c == '.' || c == '_' || c == '-')) return false;
  }
  if (strstr(s, "..")) return false;
  return !allowDotBin || (n > 4 && strcmp(s + n - 4, ".bin") == 0);
}

// 韌體檔路徑:檔名,或「一層資料夾/檔名」(GG 2026-09-14:公開專案的韌體檔集中放 firmware/ 資料夾,首頁才不會越來越長).
// 不允許開頭斜線,兩層以上,..,其他字元.
static bool validFilePath(const char *s, size_t maxLen) {
  const size_t n = strlen(s);
  if (n == 0 || n > maxLen) return false;
  const char *slash = strchr(s, '/');
  if (!slash) return validToken(s, maxLen, true);
  if (slash == s || strchr(slash + 1, '/')) return false;
  char dir[32];
  const size_t dn = slash - s;
  if (dn >= sizeof(dir)) return false;
  memcpy(dir, s, dn);
  dir[dn] = 0;
  return validToken(dir, sizeof(dir) - 1, false) && validToken(slash + 1, maxLen, true);
}

// 取 JSON 字串欄位(manifest 由發布工具產生,格式固定;支援 \" \\ \n 跳脫). UTF-8 截斷時退回完整字元.
static bool jsonStr(const String &j, const char *key, char *out, size_t outSize) {
  const String pat = String("\"") + key + "\"";
  int k = j.indexOf(pat);
  if (k < 0) return false;
  int i = k + pat.length();
  while (i < (int)j.length() && (j[i] == ' ' || j[i] == ':' || j[i] == '\t' || j[i] == '\r' || j[i] == '\n')) ++i;
  if (i >= (int)j.length() || j[i] != '"') return false;
  size_t n = 0;
  bool full = false;
  for (++i; i < (int)j.length(); ++i) {
    char c = j[i];
    if (c == '"') {
      out[n] = 0;
      return true;
    }
    if (c == '\\' && i + 1 < (int)j.length()) {
      const char e = j[++i];
      c = e == 'n' ? '\n' : (e == 't' ? ' ' : e);
    }
    if (full) continue;
    if (n + 1 < outSize) {
      out[n++] = c;
    } else {
      full = true;
      while (n > 0 && ((uint8_t)out[n - 1] & 0xC0) == 0x80) --n;   // 去掉半個字
      if (n > 0 && ((uint8_t)out[n - 1] & 0xC0) == 0xC0) --n;
    }
  }
  return false;
}

static bool jsonNum(const String &j, const char *key, uint32_t &out) {
  const String pat = String("\"") + key + "\"";
  int k = j.indexOf(pat);
  if (k < 0) return false;
  int i = k + pat.length();
  while (i < (int)j.length() && (j[i] == ' ' || j[i] == ':')) ++i;
  if (i >= (int)j.length() || !isdigit((unsigned char)j[i])) return false;
  uint64_t v = 0;
  for (; i < (int)j.length() && isdigit((unsigned char)j[i]); ++i) v = v * 10 + (j[i] - '0');
  if (v > 0xFFFFFFFFULL) return false;
  out = (uint32_t)v;
  return true;
}

// 版本「年.月.日.序號」逐段比數字(字串比較會把 .9 排在 .10 後面). 每段取開頭的數字,缺的段當 0.
int fwVersionCompare(const char *a, const char *b) {
  while (*a || *b) {
    uint32_t x = 0, y = 0;
    while (isdigit((unsigned char)*a)) x = x * 10 + (*a++ - '0');
    while (isdigit((unsigned char)*b)) y = y * 10 + (*b++ - '0');
    if (x != y) return x > y ? 1 : -1;
    while (*a && *a != '.') ++a;   // 段內數字後面的其他字元不比
    while (*b && *b != '.') ++b;
    if (*a == '.') ++a;
    if (*b == '.') ++b;
  }
  return 0;
}

static String baseUrl() { return testBaseUrl[0] ? String(testBaseUrl) : String(FW_UPDATE_BASE_URL); }

bool fwUpdateTestSetBaseUrl(const char *url) {
  if (task || busyFlag) return false;
  if (!url || !url[0]) {
    testBaseUrl[0] = 0;
  } else {
    const size_t n = strlen(url);
    // 只接受 HTTPS 且以 / 結尾(下載一樣走憑證驗證)
    if (strncmp(url, "https://", 8) != 0 || url[n - 1] != '/' || n >= sizeof(testBaseUrl)) return false;
    strlcpy(testBaseUrl, url, sizeof(testBaseUrl));
  }
  LOCKED(st.check = FWC_IDLE; st.err[0] = 0; st.remoteVersion[0] = 0);
  return true;
}

static bool httpBegin(HTTPClient &http, NetworkClientSecure &client, const String &url) {
  client.setCACertBundle(x509BundleStart, x509BundleEnd - x509BundleStart);
  http.setConnectTimeout(HTTP_TIMEOUT_MS);
  http.setTimeout(HTTP_TIMEOUT_MS);
  http.setReuse(false);
  if (!http.begin(client, url)) return false;
  http.addHeader("Cache-Control", "no-cache");
  return true;
}

static void doCheck() {
  NetworkClientSecure client;
  HTTPClient http;
  if (!httpBegin(http, client, baseUrl() + FW_MANIFEST_NAME)) return setError("url");
  const int code = http.GET();
  if (code != 200) {
    http.end();
    Serial.printf("FW manifest HTTP %d\n", code);
    return setError(code < 0 ? "net" : (code == 404 ? "nomanifest" : "http"));
  }
  if (http.getSize() > (int)MANIFEST_MAX) {
    http.end();
    return setError("manifest");
  }
  const String body = http.getString();
  http.end();
  char ver[24], file[64], sha[65];
  static char notes[FW_NOTES_MAX + 1];
  uint32_t size = 0;
  if (!jsonStr(body, "version", ver, sizeof(ver)) || !jsonStr(body, "file", file, sizeof(file)) ||
      !jsonStr(body, "sha256", sha, sizeof(sha)) || !jsonNum(body, "size", size))
    return setError("manifest");
  if (!jsonStr(body, "notes", notes, sizeof(notes))) notes[0] = 0;
  bool shaOk = strlen(sha) == 64;
  for (size_t i = 0; shaOk && i < 64; ++i) shaOk = isxdigit((unsigned char)sha[i]);
  const esp_partition_t *next = esp_ota_get_next_update_partition(nullptr);
  if (!validToken(ver, 23, false) || !validFilePath(file, 63) || !shaOk || size < 100000) return setError("manifest");
  if (!next || size > next->size) return setError("toolarge");
  strlcpy(remoteFile, file, sizeof(remoteFile));
  for (size_t i = 0; i < 64; ++i) remoteSha[i] = tolower((unsigned char)sha[i]);
  remoteSha[64] = 0;
  const int newer = fwVersionCompare(ver, FW_VERSION);
  LOCKED(strlcpy(st.remoteVersion, ver, sizeof(st.remoteVersion)); st.remoteSize = size; strlcpy(st.notes, notes, sizeof(st.notes));
         st.remoteNewer = (int8_t)newer; st.err[0] = 0; st.check = FWC_CHECKED);
  Serial.printf("FW manifest version=%s size=%lu newer=%d\n", ver, (unsigned long)size, newer);
}

static void doInstall() {
  char ver[24];
  uint32_t size;
  LOCKED(strlcpy(ver, st.remoteVersion, sizeof(ver)); size = st.remoteSize);
  NetworkClientSecure client;
  HTTPClient http;
  if (!httpBegin(http, client, baseUrl() + remoteFile)) return setError("url");
  const int code = http.GET();
  if (code != 200) {
    http.end();
    return setError(code < 0 ? "net" : (code == 404 ? "nofile" : "http"));
  }
  if (http.getSize() != (int)size) {
    http.end();
    return setError("size");
  }
  if (!controlOtaAllowed()) {
    http.end();
    return setError("busy");
  }
  fwUpdateStarted(FWS_DOWNLOAD);
  if (!Update.begin(size)) {
    http.end();
    fwUpdateFlashed(false);
    return setError("flashbegin");
  }
  mbedtls_sha256_context sha;
  mbedtls_sha256_init(&sha);
  mbedtls_sha256_starts(&sha, 0);
  NetworkClient *stream = http.getStreamPtr();
  uint32_t got = 0, lastDataMs = millis();
  const char *err = nullptr;
  while (got < size) {
    const int avail = stream->available();
    if (avail > 0) {
      const size_t want = min((size_t)avail, min(sizeof(dlBuf), (size_t)(size - got)));
      const int r = stream->read(dlBuf, want);
      if (r <= 0) continue;
      if (Update.write(dlBuf, r) != (size_t)r) {
        err = "flashwrite";
        break;
      }
      mbedtls_sha256_update(&sha, dlBuf, r);
      got += r;
      lastDataMs = millis();
      LOCKED(st.progress = (uint8_t)((uint64_t)got * 100 / size));
    } else {
      if (!stream->connected()) {
        err = "short";
        break;
      }
      if (millis() - lastDataMs > DOWNLOAD_STALL_MS) {
        err = "timeout";
        break;
      }
      vTaskDelay(pdMS_TO_TICKS(2));
    }
  }
  http.end();
  uint8_t digest[32];
  mbedtls_sha256_finish(&sha, digest);
  mbedtls_sha256_free(&sha);
  if (!err) {
    char hex[65];
    for (int i = 0; i < 32; ++i) snprintf(hex + i * 2, 3, "%02x", digest[i]);
    if (strcmp(hex, remoteSha) != 0) {
      Serial.printf("FW sha mismatch got %s\n", hex);
      err = "sha";
    }
  }
  // 大小或 SHA-256 不符:不切換開機分區,舊韌體照常
  if (err || !Update.end()) {
    if (!err) err = "flashend";
    Update.abort();
    fwUpdateFlashed(false);
    return setError(err);
  }
  fwUpdateFlashed(true, ver);
  LOCKED(st.progress = 100; st.check = FWC_DONE);
  restartAtMs = (millis() + RESTART_DELAY_MS) | 1;
  Serial.printf("FW %s installed (%lu bytes)\n", ver, (unsigned long)got);
}

static void fwTask(void *arg) {
  const bool install = arg != nullptr;
  if (install) doInstall();
  else doCheck();
  task = nullptr;
  vTaskDelete(nullptr);
}

static const char *startTask(bool install) {
  // TLS 交握要 6~8KB 堆疊;優先權 1 和 Arduino loop 同級,不影響控制工作(24)
  if (xTaskCreate(fwTask, "fwupd", 10240, install ? (void *)1 : nullptr, 1, &task) != pdPASS) {
    task = nullptr;
    return "nomem";
  }
  return nullptr;
}

const char *fwUpdateCheckStart() {
  if (task) return "fwbusy";
  if (busyFlag) return "fwbusy";
  if (wifiState() != WIFI_STATE_STA) return "nosta";   // 自身熱點模式沒有網際網路
  LOCKED(st.check = FWC_CHECKING; st.err[0] = 0; st.progress = 0);
  const char *err = startTask(false);
  if (err) setError(err);
  return err;
}

const char *fwUpdateInstallStart(const char *version) {
  if (task || busyFlag) return "fwbusy";
  if (pendingFlag) return "fwpending";
  if (!controlOtaAllowed()) return "busy";
  if (settingsAnyDirty()) return "fwdirty";   // 重開機會丟掉沒儲存的設定
  if (wifiState() != WIFI_STATE_STA) return "nosta";
  bool ok;
  bool newer;
  LOCKED(ok = st.check == FWC_CHECKED && version && strcmp(version, st.remoteVersion) == 0; newer = st.remoteNewer > 0);
  if (!ok) return "fwstale";
  if (!newer) return "fwnotnewer";   // 網站上的版本和目前一樣或比較舊:不裝(要換舊版請手動上傳韌體檔)
  LOCKED(st.check = FWC_DOWNLOADING; st.err[0] = 0; st.progress = 0);
  const char *err = startTask(true);
  if (err) setError(err);
  return err;
}

void fwUpdateGetStatus(FwStatus &out) {
  LOCKED(out = st; out.busy = busyFlag; out.pending = pendingFlag);
}
