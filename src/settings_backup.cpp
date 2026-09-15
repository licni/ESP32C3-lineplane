// 版本流水號: r9 (2026-09-15) 安全審查:解碼從板上目前值起算(碼裡沒有的欄位一律保持,舊碼不再把新功能洗回出廠);含 WiFi 時先存 WiFi 再套飛行設定
// 舊: r8 (2026-09-15) 套用時可取消碼裡的項目(GG:對方多複製了不要的設定):取消的項目照樣讀掉位元但寫進 scratch,保持目前的值;
//   回傳實際套用的分區/風格與碼裡各組名稱;格式不變
// 舊: r7 (2026-09-15) 格式大版本 3:分區選擇(GG:分享計時器不該蓋掉對方的安裝與電變,備份獨立分頁全部可選).
//   多 6 bit 分區記號(起飛降落與安全/安裝/電變/WiFi),共用參數依分區決定存不存;WiFi 區塊(含密碼,套用時存檔並試用).
//   大版本 1,2 的舊碼照舊解讀(三區共用設定全有,沒有 WiFi)
// 舊: r6 (2026-09-15) 格式大版本 2:選組備份(GG:預設只存「測試」組,碼從 336 字縮到約 100 字).
//   多 6 bit 選組記號,沒選的風格名稱與欄位都不存;「測試」組名稱鎖定不存. 大版本 1 的舊碼照舊當六組全選解讀
// 舊: r5 (2026-09-15) 世代 4:起飛油門 takeoffPct,起飛油門持續時間 takeoffHold
// 舊: r4 (2026-09-14) 世代 3:忽略安全開關 armSwitchOff
// 舊: r3 (2026-09-14) 名稱長度 0 改對照本檔凍結的名稱表(出廠名稱第 6 組改成「測試」後,舊碼的 TEST 不會跟著變)
// 舊: r2 (2026-09-14) 世代 2:蜂鳴器電位 buzzerLow
// 舊: r1 (2026-09-14) 初版:設定備份碼(LP + base62,每個參數固定位元數,新功能往尾端加,CRC-24)
#include "settings_backup.h"
#include "settings.h"
#include "wifi_manager.h"

// ============================================================================
// 位元組資料(大版本 3,目前產生的格式):
//   [格式大版本 2 bit + 欄位世代 6 bit][飛行使用風格 3 bit][分區 6 bit(bit 4,5 預留 0)][選組 6 bit:風格 0~5 各 1 bit]
//   [選到的組的名稱:5 bit 長度(0 = CODEC_DEFAULT_NAMES 的名稱)+ UTF-8;「測試」組不存]
//   [有選 WiFi 時:WiFi 區塊,見 writeWifi]
//   [世代 1 欄位:共用(只存選到的分區)→ 選到的風格][世代 2 欄位 …]…[補 0 到整位元組][CRC-24]
// 大版本 2(2026-09-15 開發中短暫使用):沒有分區記號與 WiFi 區塊,共用設定全部都有.
// 大版本 1(2026-09-14 ~ 09-15 產生的舊碼):再加上沒有選組記號,六組名稱(含「測試」組)與欄位全部都有. 解碼都照舊支援.
// 每個欄位存 (值 − 編碼下限) ÷ 步進 的整數,固定位元數(目前範圍所需 + 1 位元預留).
//
// ★ 編碼表定案後永遠不改(改了舊短碼就解錯):
//   - 新參數:開新世代,欄位接在後面. 舊短碼沒有這一段,套用時保持板上目前的值(r9 起;以前是出廠值). 共用參數要同時登記分區(SHARED_SECTIONS).
//   - 參數範圍超出位元數:新世代再放一次這個參數(新的下限/位元數),解碼時後面的世代蓋過前面的.
//   - 參數刪掉:表裡的欄位與分區登記都保留(照樣佔位元),解碼時參數表查不到就略過.
//   - 結構大改才加 FORMAT_MAJOR,舊韌體看到不認得的大版本會說「請更新韌體」;新韌體要繼續能解舊的大版本.
// ============================================================================

namespace {

const uint8_t FORMAT_MAJOR = 3;
const uint8_t FORMAT_MAJOR_SELECT = 2;    // 從這個大版本開始有選組記號
const uint8_t FORMAT_MAJOR_SECTION = 3;   // 從這個大版本開始有分區記號與 WiFi 區塊
const uint8_t SECTION_BITS = 6;
const uint8_t SECTION_KNOWN = BACKUP_SEC_ALL;   // bit 4,5 預留:有設的碼來自較新的韌體
const uint8_t NAME_LEN_BITS = 5;
const size_t MAX_BYTES = 640;
const size_t MAX_CODE_CHARS = 2000;
// 名稱長度 0 代表這個名稱(格式定案時的出廠名稱,永遠不改;韌體出廠名稱改了也不影響舊碼)
const char *const CODEC_DEFAULT_NAMES[PROFILE_COUNT] = {"A", "B", "C", "D", "E", "TEST"};

struct CodecField {
  const char *key;
  float encMin;
  float step;
  uint8_t bits;
};

// --- 世代 1(2026-09-14) ----------------------------------------------------------
const CodecField GEN1_SHARED[] = {
    {"noseAxis", 0, 1, 4},        {"upAxis", 0, 1, 4},          {"noseRight", 0, 1, 2},
    {"pitchTrim", -30, 0.1f, 11}, {"escProtocol", 0, 1, 3},     {"escPwmHz", 50, 10, 7},
    {"escMinUs", 800, 5, 9},      {"escMaxUs", 1500, 5, 9},     {"gestureEnable", 0, 1, 2},
    {"gestureG", 0.5f, 0.1f, 7},  {"startLevel", 10, 1, 8},     {"armWait", 1, 1, 6},
    {"countdownSec", 5, 1, 8},    {"disturbG", 0.05f, 0.01f, 8}, {"disturbMode", 0, 1, 3},
    {"extendSec", 1, 1, 7},       {"touchdownG", 1.5f, 0.1f, 8}, {"touchdownStill", 0.5f, 0.1f, 7},
    {"landingTimeout", 5, 1, 8},  {"crashEnable", 0, 1, 2},     {"crashG", 6, 0.5f, 6},
    {"lineLength", 5, 0.1f, 9},   {"lapSec", 2, 0.1f, 8},       {"calibHold", 1, 0.5f, 6},
    {"earlyLand", 0, 1, 2},       {"earlyLandArm", 3, 1, 7},    {"earlyLandTilt", 5, 1, 7},
    {"earlyLandVib", 0.1f, 0.05f, 8}, {"earlyLandHold", 0.2f, 0.1f, 7}, {"twistCancel", 0, 1, 9},
    {"twistBlock", 1, 1, 6},      {"escRpm", 0, 1, 2},          {"motorPoles", 2, 2, 6},
    {"gearEnable", 0, 1, 2},      {"gearReverse", 0, 1, 2},     {"gearMinUs", 500, 5, 9},
    {"gearMaxUs", 1500, 5, 9},    {"gearRetractSec", 1, 1, 8},  {"gearTravelSec", 0, 0.1f, 8},
};

// 曲線的角度,死區,補償值都是 int8,直接存整個 int8 範圍
const CodecField GEN1_PROFILE[] = {
    {"phase1Pct", 0, 1, 8},     {"phase1Sec", 10, 5, 9},     {"phase2Pct", 0, 1, 8},     {"flightSec", 30, 5, 10},
    {"takeoffRamp", 0, 0.1f, 8}, {"phaseRamp", 0, 0.5f, 7},  {"noCompSec", 0, 0.5f, 7},  {"minPct", 0, 1, 8},
    {"maxPct", 0, 1, 8},        {"landingRamp", 0, 0.5f, 7}, {"landingPct", 0, 1, 8},    {"phaseMode", 0, 1, 3},
    {"upDb", -128, 1, 8},       {"upN", 1, 1, 3},
    {"up1a", -128, 1, 8},       {"up1p", -128, 1, 8},        {"up2a", -128, 1, 8},       {"up2p", -128, 1, 8},
    {"up3a", -128, 1, 8},       {"up3p", -128, 1, 8},        {"up4a", -128, 1, 8},       {"up4p", -128, 1, 8},
    {"dnDb", -128, 1, 8},       {"dnN", 1, 1, 3},
    {"dn1a", -128, 1, 8},       {"dn1p", -128, 1, 8},        {"dn2a", -128, 1, 8},       {"dn2p", -128, 1, 8},
    {"dn3a", -128, 1, 8},       {"dn3p", -128, 1, 8},        {"dn4a", -128, 1, 8},       {"dn4p", -128, 1, 8},
};

// --- 世代 2(2026-09-14):蜂鳴器 ------------------------------------------------------
const CodecField GEN2_SHARED[] = {
    {"buzzerLow", 0, 1, 2},
};

// --- 世代 3(2026-09-14):忽略安全開關 -------------------------------------------------
const CodecField GEN3_SHARED[] = {
    {"armSwitchOff", 0, 1, 2},
};

// --- 世代 4(2026-09-15):起飛油門 ----------------------------------------------------------
const CodecField GEN4_PROFILE[] = {
    {"takeoffPct", 0, 1, 8}, {"takeoffHold", 0, 0.5f, 8},
};

// --- 世代 5(2026-09-15):蜂鳴器範圍放寬為 0~2,保留世代 2 原表 ------------------------
const CodecField GEN5_SHARED[] = {
    {"buzzerLow", 0, 1, 3},
};

// --- 共用參數的分區(與網頁分頁一致;★ 登記後永遠不改,參數刪掉也保留) -----------------------------
struct KeySection {
  const char *key;
  uint8_t sec;
};
const KeySection SHARED_SECTIONS[] = {
    // 設定頁:啟動與倒數,觸地提早降落,降落與撞擊
    {"gestureEnable", BACKUP_SEC_FLIGHT}, {"startLevel", BACKUP_SEC_FLIGHT},   {"gestureG", BACKUP_SEC_FLIGHT},
    {"twistCancel", BACKUP_SEC_FLIGHT},   {"twistBlock", BACKUP_SEC_FLIGHT},   {"armSwitchOff", BACKUP_SEC_FLIGHT},
    {"armWait", BACKUP_SEC_FLIGHT},       {"countdownSec", BACKUP_SEC_FLIGHT}, {"disturbG", BACKUP_SEC_FLIGHT},
    {"disturbMode", BACKUP_SEC_FLIGHT},   {"extendSec", BACKUP_SEC_FLIGHT},    {"earlyLand", BACKUP_SEC_FLIGHT},
    {"earlyLandVib", BACKUP_SEC_FLIGHT},  {"earlyLandHold", BACKUP_SEC_FLIGHT}, {"earlyLandTilt", BACKUP_SEC_FLIGHT},
    {"earlyLandArm", BACKUP_SEC_FLIGHT},  {"touchdownG", BACKUP_SEC_FLIGHT},   {"touchdownStill", BACKUP_SEC_FLIGHT},
    {"landingTimeout", BACKUP_SEC_FLIGHT}, {"crashEnable", BACKUP_SEC_FLIGHT}, {"crashG", BACKUP_SEC_FLIGHT},
    // 安裝頁:感測器方位,角度修正,飛行速度,機輪收腳,蜂鳴器
    {"noseAxis", BACKUP_SEC_INSTALL},     {"upAxis", BACKUP_SEC_INSTALL},      {"noseRight", BACKUP_SEC_INSTALL},
    {"pitchTrim", BACKUP_SEC_INSTALL},    {"lineLength", BACKUP_SEC_INSTALL},  {"lapSec", BACKUP_SEC_INSTALL},
    {"gearEnable", BACKUP_SEC_INSTALL},   {"gearReverse", BACKUP_SEC_INSTALL}, {"gearMinUs", BACKUP_SEC_INSTALL},
    {"gearMaxUs", BACKUP_SEC_INSTALL},    {"gearRetractSec", BACKUP_SEC_INSTALL}, {"gearTravelSec", BACKUP_SEC_INSTALL},
    {"buzzerLow", BACKUP_SEC_INSTALL},
    // 電變頁:輸出協定,PWM 頻率,脈寬,校正保持,轉速回傳,馬達極數
    {"escProtocol", BACKUP_SEC_ESC},      {"escPwmHz", BACKUP_SEC_ESC},        {"escMinUs", BACKUP_SEC_ESC},
    {"escMaxUs", BACKUP_SEC_ESC},         {"calibHold", BACKUP_SEC_ESC},       {"escRpm", BACKUP_SEC_ESC},
    {"motorPoles", BACKUP_SEC_ESC},
};

uint8_t sectionOf(const char *key) {
  for (const KeySection &s : SHARED_SECTIONS)
    if (strcmp(s.key, key) == 0) return s.sec;
  return 0;
}

struct Generation {
  const CodecField *shared;
  uint8_t sharedCount;
  const CodecField *profile;
  uint8_t profileCount;
};

#define COUNT_OF(a) (uint8_t)(sizeof(a) / sizeof(a[0]))
const Generation GENERATIONS[] = {
    {GEN1_SHARED, COUNT_OF(GEN1_SHARED), GEN1_PROFILE, COUNT_OF(GEN1_PROFILE)},
    {GEN2_SHARED, COUNT_OF(GEN2_SHARED), nullptr, 0},
    {GEN3_SHARED, COUNT_OF(GEN3_SHARED), nullptr, 0},
    {nullptr, 0, GEN4_PROFILE, COUNT_OF(GEN4_PROFILE)},
    {GEN5_SHARED, COUNT_OF(GEN5_SHARED), nullptr, 0},
};
const uint8_t MY_GENERATION = COUNT_OF(GENERATIONS);

// --- 位元讀寫(高位先) -------------------------------------------------------------
struct BitWriter {
  uint8_t *buf;
  size_t cap;
  size_t bits = 0;
  bool overflow = false;
  void put(uint32_t v, uint8_t n) {
    for (int i = n - 1; i >= 0; --i) {
      const size_t byte = bits >> 3;
      if (byte >= cap) {
        overflow = true;
        return;
      }
      if ((bits & 7) == 0) buf[byte] = 0;
      if ((v >> i) & 1) buf[byte] |= 0x80 >> (bits & 7);
      ++bits;
    }
  }
};

struct BitReader {
  const uint8_t *buf;
  size_t totalBits;
  size_t pos = 0;
  bool overflow = false;
  uint32_t get(uint8_t n) {
    uint32_t v = 0;
    for (uint8_t i = 0; i < n; ++i) {
      if (pos >= totalBits) {
        overflow = true;
        return 0;
      }
      v = (v << 1) | ((buf[pos >> 3] >> (7 - (pos & 7))) & 1);
      ++pos;
    }
    return v;
  }
};

// CRC-24(OpenPGP):漏抓機率約 1600 萬分之一
uint32_t crc24(const uint8_t *d, size_t n) {
  uint32_t crc = 0xB704CE;
  for (size_t i = 0; i < n; ++i) {
    crc ^= (uint32_t)d[i] << 16;
    for (uint8_t k = 0; k < 8; ++k) {
      crc <<= 1;
      if (crc & 0x1000000) crc ^= 0x1864CFB;
    }
  }
  return crc & 0xFFFFFF;
}

// --- base62:每 5 位元組 → 7 字,只用 0-9 A-Z a-z(LINE 不會在符號處斷行,點兩下能整串選取) ---
const char ALPHABET[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
const uint8_t CHARS_FOR_BYTES[6] = {0, 2, 3, 5, 6, 7};   // 最後一段不足 5 位元組時的字數

void base62Append(String &out, const uint8_t *d, size_t n) {
  for (size_t i = 0; i < n; i += 5) {
    const size_t k = n - i < 5 ? n - i : 5;
    uint64_t v = 0;
    for (size_t j = 0; j < k; ++j) v = (v << 8) | d[i + j];
    const uint8_t c = CHARS_FOR_BYTES[k];
    char tmp[8];
    for (int j = c - 1; j >= 0; --j) {
      tmp[j] = ALPHABET[v % 62];
      v /= 62;
    }
    tmp[c] = 0;
    out += tmp;
  }
}

int base62Digit(char ch) {
  if (ch >= '0' && ch <= '9') return ch - '0';
  if (ch >= 'A' && ch <= 'Z') return ch - 'A' + 10;
  if (ch >= 'a' && ch <= 'z') return ch - 'a' + 36;
  return -1;
}

// 回傳位元組數;有不合法字元,長度對不上或某段數值超出位元組範圍回 -1
int base62Decode(const char *s, size_t len, uint8_t *out, size_t cap) {
  size_t n = 0;
  for (size_t i = 0; i < len;) {
    const size_t c = len - i < 7 ? len - i : 7;
    int k = -1;
    for (uint8_t b = 1; b <= 5; ++b)
      if (CHARS_FOR_BYTES[b] == c) k = b;
    if (k < 0 || n + k > cap) return -1;
    uint64_t v = 0;
    for (size_t j = 0; j < c; ++j) {
      const int dgt = base62Digit(s[i + j]);
      if (dgt < 0) return -1;
      v = v * 62 + (uint64_t)dgt;
    }
    if (v >> (8 * k)) return -1;
    for (int j = k - 1; j >= 0; --j) {
      out[n + j] = (uint8_t)(v & 0xFF);
      v >>= 8;
    }
    n += k;
    i += c;
  }
  return (int)n;
}

void writeField(BitWriter &w, const SettingsImage &img, int8_t scope, const CodecField &f) {
  float v = f.encMin;   // 這版參數表沒有的欄位(已刪除的參數)寫下限,解碼端會略過
  if (settingsImageGet(img, scope, f.key, v)) {
    float mn = 0, mx = 0;
    if (settingsParamRange(scope < 0, f.key, mn, mx)) v = constrain(v, mn, mx);   // 解碼端就不會出現「被夾」
  }
  long q = lroundf((v - f.encMin) / f.step);
  const long top = (1L << f.bits) - 1;
  w.put((uint32_t)constrain(q, 0L, top), f.bits);
}

void readField(BitReader &r, SettingsImage &img, int8_t scope, const CodecField &f, String &clamped) {
  const uint32_t q = r.get(f.bits);
  if (r.overflow) return;
  bool over = false;
  if (!settingsImagePut(img, scope, f.key, f.encMin + q * f.step, over)) return;   // 這版韌體沒有的參數:略過
  if (!over) return;
  if (clamped.length()) clamped += ',';
  clamped += '"';
  clamped += scope < 0 ? String("s") : String(scope);
  clamped += ':';
  clamped += f.key;
  clamped += '"';
}

// --- WiFi 區塊 --------------------------------------------------------------------
// [12 bit 內容位元數][家用 SSID 6 bit 長度 + 位元組][家用密碼 6 + 位元組][裝置名稱 5 + 位元組]
// [熱點名稱後綴 4 + 位元組][熱點密碼 6 + 位元組][等待秒數 7 bit][一律用熱點 1 bit][發射功率 5 bit]
// 開頭記內容位元數:以後在尾端加欄位,舊韌體讀完認得的部分直接跳過其餘.
const uint8_t WIFI_LEN_BITS = 12;
struct WifiStr {
  uint8_t lenBits;
  uint8_t maxLen;
};
const WifiStr WIFI_SSID_F = {6, WIFI_SSID_BUFFER - 1}, WIFI_PW_F = {6, WIFI_PASS_BUFFER - 1},
              WIFI_HOST_F = {5, MDNS_HOST_BUFFER - 1}, WIFI_SFX_F = {4, WIFI_AP_SUFFIX_MAX_BYTES},
              WIFI_APPW_F = {6, WIFI_PASS_BUFFER - 1};

size_t wifiStrBits(const WifiStr &f, const char *s) { return f.lenBits + 8 * strnlen(s, f.maxLen); }

void writeWifiStr(BitWriter &w, const WifiStr &f, const char *s) {
  const size_t n = strnlen(s, f.maxLen);
  w.put(n, f.lenBits);
  for (size_t i = 0; i < n; ++i) w.put((uint8_t)s[i], 8);
}

void writeWifi(BitWriter &w, const WifiConfig &c) {
  const size_t bits = wifiStrBits(WIFI_SSID_F, c.ssid) + wifiStrBits(WIFI_PW_F, c.password) + wifiStrBits(WIFI_HOST_F, c.host) +
                      wifiStrBits(WIFI_SFX_F, c.apSuffix) + wifiStrBits(WIFI_APPW_F, c.apPassword) + 7 + 1 + 5;
  w.put(bits, WIFI_LEN_BITS);
  writeWifiStr(w, WIFI_SSID_F, c.ssid);
  writeWifiStr(w, WIFI_PW_F, c.password);
  writeWifiStr(w, WIFI_HOST_F, c.host);
  writeWifiStr(w, WIFI_SFX_F, c.apSuffix);
  writeWifiStr(w, WIFI_APPW_F, c.apPassword);
  w.put(c.staTimeoutSec, 7);
  w.put(c.forceAp ? 1 : 0, 1);
  w.put(c.txPowerDbm, 5);
}

bool readWifiStr(BitReader &r, const WifiStr &f, char *out, size_t cap) {
  const uint32_t n = r.get(f.lenBits);
  if (r.overflow || n > f.maxLen || n >= cap) return false;
  for (uint32_t i = 0; i < n; ++i) out[i] = (char)r.get(8);
  out[n] = 0;
  return !r.overflow;
}

// 讀進 out(呼叫前先放目前的設定,這裡逐欄蓋掉). 格式不對回 false.
bool readWifi(BitReader &r, WifiConfig &out) {
  const uint32_t bits = r.get(WIFI_LEN_BITS);
  const size_t start = r.pos;
  if (r.overflow || start + bits > r.totalBits) return false;
  if (!readWifiStr(r, WIFI_SSID_F, out.ssid, sizeof(out.ssid)) || !readWifiStr(r, WIFI_PW_F, out.password, sizeof(out.password)) ||
      !readWifiStr(r, WIFI_HOST_F, out.host, sizeof(out.host)) || !readWifiStr(r, WIFI_SFX_F, out.apSuffix, sizeof(out.apSuffix)) ||
      !readWifiStr(r, WIFI_APPW_F, out.apPassword, sizeof(out.apPassword)))
    return false;
  out.staTimeoutSec = (uint8_t)r.get(7);
  out.forceAp = r.get(1) != 0;
  out.txPowerDbm = (uint8_t)r.get(5);
  if (r.overflow || r.pos > start + bits) return false;
  r.pos = start + bits;   // 較新韌體加在尾端的欄位:跳過
  return true;
}

}  // namespace

const char *backupEncode(String &out, uint8_t profileMask, uint8_t sectionMask) {
  if (profileMask > BACKUP_ALL_PROFILES || sectionMask > BACKUP_SEC_ALL || (profileMask == 0 && sectionMask == 0)) return "bksel";
  static SettingsImage img;   // 約 600 位元組,不放在 loop 的堆疊上
  settingsGetImage(img);
  const auto selected = [&](uint8_t i) { return (profileMask >> i) & 1; };
  uint8_t buf[MAX_BYTES];
  BitWriter w{buf, sizeof(buf) - 3};
  w.put((FORMAT_MAJOR << 6) | MY_GENERATION, 8);
  w.put(img.active, 3);
  w.put(sectionMask, SECTION_BITS);
  w.put(profileMask, PROFILE_COUNT);
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    if (!selected(i) || i == PROFILE_TEST_INDEX) continue;   // 沒選的不存;「測試」名稱鎖定不必存
    const char *name = img.profiles[i].name;
    const bool isDefault = strncmp(name, CODEC_DEFAULT_NAMES[i], PROFILE_NAME_BUFFER) == 0;
    const size_t len = isDefault ? 0 : strnlen(name, PROFILE_NAME_BUFFER - 1);
    w.put(len, NAME_LEN_BITS);
    for (size_t k = 0; k < len; ++k) w.put((uint8_t)name[k], 8);
  }
  if (sectionMask & BACKUP_SEC_WIFI) writeWifi(w, wifiConfig());
  for (const Generation &g : GENERATIONS) {
    for (uint8_t k = 0; k < g.sharedCount; ++k)
      if (sectionOf(g.shared[k].key) & sectionMask) writeField(w, img, -1, g.shared[k]);
    for (uint8_t p = 0; p < PROFILE_COUNT; ++p) {
      if (!selected(p)) continue;
      for (uint8_t k = 0; k < g.profileCount; ++k) writeField(w, img, p, g.profile[k]);
    }
  }
  if (w.overflow) return "bkfail";
  size_t n = (w.bits + 7) >> 3;   // 最後不足一位元組的部分 put 時已補 0
  const uint32_t crc = crc24(buf, n);
  buf[n++] = (uint8_t)(crc >> 16);
  buf[n++] = (uint8_t)(crc >> 8);
  buf[n++] = (uint8_t)crc;
  out.reserve(2 + n * 7 / 5 + 8);
  out = "LP";
  base62Append(out, buf, n);
  return nullptr;
}

const char *backupDecode(const char *text, bool apply, BackupInfo &info, uint8_t filterProfiles, uint8_t filterSections) {
  info = BackupInfo();
  // 拿掉空白與換行(聊天軟體會自動斷行)
  static char code[MAX_CODE_CHARS + 1];
  size_t len = 0;
  for (const char *p = text; *p; ++p) {
    if (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') continue;
    if (len >= MAX_CODE_CHARS) return "bkcrc";
    code[len++] = *p;
  }
  code[len] = 0;
  if (len < 2 || code[0] != 'L' || code[1] != 'P') return "bkprefix";

  uint8_t buf[MAX_BYTES];
  const int n = base62Decode(code + 2, len - 2, buf, sizeof(buf));
  if (n < 5) return "bkcrc";
  const uint32_t crc = crc24(buf, n - 3);
  if (((uint32_t)buf[n - 3] << 16 | (uint32_t)buf[n - 2] << 8 | buf[n - 1]) != crc) return "bkcrc";
  const uint8_t major = buf[0] >> 6;
  if (major == 0) return "bkcrc";
  if (major > FORMAT_MAJOR) return "bkver";   // 比這版韌體新的格式;較舊的大版本照舊解讀
  const uint8_t gen = buf[0] & 0x3F;
  if (gen == 0) return "bkcrc";
  info.generation = gen;
  info.newer = gen > MY_GENERATION;

  // 從板子目前的值起算(安全審查 3-A,GG 2026-09-15 決定):碼裡沒有的東西 —— 沒選的風格/分區,使用者取消的項目,
  // 較舊世代沒有的欄位 —— 一律保持板上目前的值. 09-14 的設計「舊碼缺的欄位回出廠值」作廢:有了分區與取消機制後,
  // 「碼裡沒有的部分不動」才是使用者看到的說明. 順帶讓 reserved 位元組與未選分區的浮點值不會因為重新對齊而顯示未儲存.
  static SettingsImage img;
  settingsGetImage(img);
  BitReader r{buf, (size_t)(n - 3) * 8};
  r.pos = 8;
  const uint8_t act = (uint8_t)r.get(3);
  if (act < PROFILE_COUNT) {
    img.active = act;
  } else {
    img.active = 0;
    info.clamped = "\"act\"";
  }
  const bool hasSection = major >= FORMAT_MAJOR_SECTION;
  const uint8_t sec = hasSection ? (uint8_t)r.get(SECTION_BITS) : BACKUP_SEC_SHARED;   // 大版本 1,2 = 共用設定全部,沒有 WiFi
  if (sec & ~SECTION_KNOWN) return "bkver";   // 較新韌體才有的分區
  const uint8_t mask = major >= FORMAT_MAJOR_SELECT ? (uint8_t)r.get(PROFILE_COUNT) : BACKUP_ALL_PROFILES;   // 大版本 1 = 六組全選
  if (mask == 0 && sec == 0) return "bkcrc";
  if (mask == 0 && !hasSection) return "bkcrc";
  info.sectionMask = sec;
  info.profileMask = mask;
  // 實際套用 = 碼裡有的 ∩ 使用者沒取消的. 取消的項目照樣要把位元讀掉(位置才對得上),只是讀進 scratch 不用.
  const uint8_t useMask = mask & filterProfiles, useSec = sec & filterSections;
  if (useMask == 0 && useSec == 0) return "bknone";
  info.applyProfileMask = useMask;
  info.applySectionMask = useSec;
  const auto inCode = [&](uint8_t i) { return (mask >> i) & 1; };
  const auto used = [&](uint8_t i) { return (useMask >> i) & 1; };
  static SettingsImage live, scratch;
  settingsGetImage(live);
  scratch = live;   // 取消的項目讀進這裡(位元要讀掉,值不用)
  String ignoredClamp;
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    if (!inCode(i)) continue;
    SettingsImage &dst = used(i) ? img : scratch;
    if (major >= FORMAT_MAJOR_SELECT && i == PROFILE_TEST_INDEX) continue;   // 新格式不存「測試」名稱(大版本 1 有存,照樣讀掉)
    const uint8_t nl = (uint8_t)r.get(NAME_LEN_BITS);
    if (nl == 0) {
      settingsImageSetName(dst, i, CODEC_DEFAULT_NAMES[i]);
      continue;
    }
    if (nl > PROFILE_NAME_BUFFER - 1) return "bkcrc";
    char name[PROFILE_NAME_BUFFER];
    for (uint8_t k = 0; k < nl; ++k) name[k] = (char)r.get(8);
    name[nl] = 0;
    if (r.overflow) return "bkcrc";
    if (const char *e = settingsImageSetName(dst, i, name)) {
      info.badScope = (int8_t)i;
      return e;
    }
  }
  // 碼裡各組的名稱(網頁顯示勾選用;「測試」組名稱固定)
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    if (i) info.names += ',';
    info.names += '"';
    if (inCode(i)) {
      for (const char *c = (used(i) ? img : scratch).profiles[i].name; *c; ++c) {
        if (*c == '"' || *c == '\\') info.names += '\\';
        info.names += *c;
      }
    }
    info.names += '"';
  }
  static WifiConfig wifi;
  const bool hasWifi = hasSection && (sec & BACKUP_SEC_WIFI);
  const bool useWifi = hasWifi && (useSec & BACKUP_SEC_WIFI);
  if (hasWifi) {
    wifi = wifiConfig();
    if (!readWifi(r, wifi)) return "bkcrc";
  }
  const uint8_t known = gen < MY_GENERATION ? gen : MY_GENERATION;
  for (uint8_t gi = 0; gi < known; ++gi) {
    const Generation &g = GENERATIONS[gi];
    for (uint8_t k = 0; k < g.sharedCount; ++k) {
      const uint8_t fs = sectionOf(g.shared[k].key);
      if (hasSection && !(fs & sec)) continue;   // 碼裡沒存這個欄位
      const bool use = (fs & useSec) != 0;
      readField(r, use ? img : scratch, -1, g.shared[k], use ? info.clamped : ignoredClamp);
    }
    for (uint8_t p = 0; p < PROFILE_COUNT; ++p) {
      if (!inCode(p)) continue;
      for (uint8_t k = 0; k < g.profileCount; ++k)
        readField(r, used(p) ? img : scratch, p, g.profile[k], used(p) ? info.clamped : ignoredClamp);
    }
  }
  if (r.overflow) return "bkcrc";
  if (!info.newer) {
    // 同世代或較舊:剩下的只能是補齊位元組的 0,多出來就是格式不對
    if (r.totalBits - r.pos >= 8 || r.get((uint8_t)(r.totalBits - r.pos)) != 0) return "bkcrc";
  }

  // 只套用部分風格時不切換飛行使用的風格:分享一兩組給別人時,不會改掉對方正在飛的那組
  if (useMask != BACKUP_ALL_PROFILES) img.active = live.active;
  if (const char *e = settingsImageValidate(img, info.badScope)) return e;
  if (useWifi) {
    if (const char *e = wifiValidateConfig(wifi)) {
      info.badScope = -2;
      return e;
    }
  }
  if (apply) {
    // WiFi 不走設定的儲存/放棄:直接存檔並標記試用,重新開機生效,WiFi 就緒 3 分鐘內沒按保持就退回.
    // 先存 WiFi 再套飛行設定(安全審查 3-B):寫入失敗時什麼都沒改,不會留下「WiFi 沒存但飛行設定已套」的半套狀態.
    if (useWifi) {
      if (const char *e = wifiSaveConfig(wifi, true)) {
        info.badScope = -2;
        return e;
      }
      info.wifiSaved = true;
    }
    settingsApplyImage(img);
  }
  return nullptr;
}

void backupSelfCheck() {
  uint16_t bad = 0;
  // 參數表每一項都要在編碼表裡(新增參數忘了開新世代,備份碼就帶不過去)
  for (uint8_t s = 0; s < 2; ++s) {
    for (size_t i = 0; const char *key = settingsParamKey(s == 0, i); ++i) {
      bool found = false;
      for (const Generation &g : GENERATIONS) {
        const CodecField *table = s ? g.profile : g.shared;
        const uint8_t count = s ? g.profileCount : g.sharedCount;
        for (uint8_t k = 0; k < count && !found; ++k) found = strcmp(table[k].key, key) == 0;
      }
      if (!found) {
        Serial.printf("backup codec: %s not in any generation, add a new generation\n", key);
        ++bad;
      }
      // 共用參數要登記分區,不然選哪一區都帶不過去
      if (s == 0 && !sectionOf(key)) {
        Serial.printf("backup codec: %s has no section, add it to SHARED_SECTIONS\n", key);
        ++bad;
      }
    }
  }
  for (const Generation &g : GENERATIONS) {
    for (uint8_t s = 0; s < 2; ++s) {
      const CodecField *table = s ? g.profile : g.shared;
      const uint8_t count = s ? g.profileCount : g.sharedCount;
      for (uint8_t k = 0; k < count; ++k) {
        float mn = 0, mx = 0;
        if (!settingsParamRange(s == 0, table[k].key, mn, mx)) continue;
        const float top = table[k].encMin + ((1L << table[k].bits) - 1) * table[k].step;
        if (mn < table[k].encMin - 1e-3f || mx > top + 1e-3f) {
          Serial.printf("backup codec: %s range %.2f~%.2f does not fit gen field (%.2f~%.2f), add a new generation\n",
                        table[k].key, mn, mx, table[k].encMin, top);
          ++bad;
        }
      }
    }
  }
  if (!bad) Serial.printf("backup codec ok, generation %u\n", (unsigned)MY_GENERATION);
}
