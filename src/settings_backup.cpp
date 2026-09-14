// 版本流水號: r4 (2026-09-14) 世代 3:忽略安全開關 armSwitchOff
// 舊: r3 (2026-09-14) 名稱長度 0 改對照本檔凍結的名稱表(出廠名稱第 6 組改成「測試」後,舊碼的 TEST 不會跟著變)
// 舊: r2 (2026-09-14) 世代 2:蜂鳴器電位 buzzerLow
// 舊: r1 (2026-09-14) 初版:設定備份碼(LP + base62,每個參數固定位元數,新功能往尾端加,CRC-24)
#include "settings_backup.h"
#include "settings.h"

// ============================================================================
// 位元組資料:
//   [格式大版本 2 bit + 欄位世代 6 bit][飛行使用風格 3 bit]
//   [六組名稱:5 bit 長度(0 = CODEC_DEFAULT_NAMES 的名稱)+ UTF-8][世代 1 欄位:共用 → 風格 0~5][世代 2 欄位 …]…[補 0 到整位元組][CRC-24]
// 每個欄位存 (值 − 編碼下限) ÷ 步進 的整數,固定位元數(目前範圍所需 + 1 位元預留).
//
// ★ 編碼表定案後永遠不改(改了舊短碼就解錯):
//   - 新參數:開新世代,欄位接在後面. 舊短碼沒有這一段,套用時維持出廠值.
//   - 參數範圍超出位元數:新世代再放一次這個參數(新的下限/位元數),解碼時後面的世代蓋過前面的.
//   - 參數刪掉:表裡的欄位保留(照樣佔位元),解碼時參數表查不到就略過.
//   - 結構大改才加 FORMAT_MAJOR,舊韌體看到不認得的大版本會說「請更新韌體」.
// ============================================================================

namespace {

const uint8_t FORMAT_MAJOR = 1;
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

}  // namespace

const char *backupEncode(String &out) {
  static SettingsImage img;   // 約 600 位元組,不放在 loop 的堆疊上
  settingsGetImage(img);
  uint8_t buf[MAX_BYTES];
  BitWriter w{buf, sizeof(buf) - 3};
  w.put((FORMAT_MAJOR << 6) | MY_GENERATION, 8);
  w.put(img.active, 3);
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    const char *name = img.profiles[i].name;
    const bool isDefault = strncmp(name, CODEC_DEFAULT_NAMES[i], PROFILE_NAME_BUFFER) == 0;
    const size_t len = isDefault ? 0 : strnlen(name, PROFILE_NAME_BUFFER - 1);
    w.put(len, NAME_LEN_BITS);
    for (size_t k = 0; k < len; ++k) w.put((uint8_t)name[k], 8);
  }
  for (const Generation &g : GENERATIONS) {
    for (uint8_t k = 0; k < g.sharedCount; ++k) writeField(w, img, -1, g.shared[k]);
    for (uint8_t p = 0; p < PROFILE_COUNT; ++p)
      for (uint8_t k = 0; k < g.profileCount; ++k) writeField(w, img, p, g.profile[k]);
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

const char *backupDecode(const char *text, bool apply, BackupInfo &info) {
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
  if ((buf[0] >> 6) != FORMAT_MAJOR) return "bkver";
  const uint8_t gen = buf[0] & 0x3F;
  if (gen == 0) return "bkcrc";
  info.generation = gen;
  info.newer = gen > MY_GENERATION;

  static SettingsImage img;
  settingsDefaultImage(img);   // 短碼沒有的欄位(較舊世代)維持出廠值
  BitReader r{buf, (size_t)(n - 3) * 8};
  r.pos = 8;
  const uint8_t act = (uint8_t)r.get(3);
  if (act < PROFILE_COUNT) {
    img.active = act;
  } else {
    img.active = 0;
    info.clamped = "\"act\"";
  }
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    const uint8_t nl = (uint8_t)r.get(NAME_LEN_BITS);
    if (nl == 0) {
      settingsImageSetName(img, i, CODEC_DEFAULT_NAMES[i]);
      continue;
    }
    if (nl > PROFILE_NAME_BUFFER - 1) return "bkcrc";
    char name[PROFILE_NAME_BUFFER];
    for (uint8_t k = 0; k < nl; ++k) name[k] = (char)r.get(8);
    name[nl] = 0;
    if (r.overflow) return "bkcrc";
    if (const char *e = settingsImageSetName(img, i, name)) {
      info.badScope = (int8_t)i;
      return e;
    }
  }
  const uint8_t known = gen < MY_GENERATION ? gen : MY_GENERATION;
  for (uint8_t gi = 0; gi < known; ++gi) {
    const Generation &g = GENERATIONS[gi];
    for (uint8_t k = 0; k < g.sharedCount; ++k) readField(r, img, -1, g.shared[k], info.clamped);
    for (uint8_t p = 0; p < PROFILE_COUNT; ++p)
      for (uint8_t k = 0; k < g.profileCount; ++k) readField(r, img, p, g.profile[k], info.clamped);
  }
  if (r.overflow) return "bkcrc";
  if (!info.newer) {
    // 同世代或較舊:剩下的只能是補齊位元組的 0,多出來就是格式不對
    if (r.totalBits - r.pos >= 8 || r.get((uint8_t)(r.totalBits - r.pos)) != 0) return "bkcrc";
  }

  if (const char *e = settingsImageValidate(img, info.badScope)) return e;
  if (apply) settingsApplyImage(img);
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
