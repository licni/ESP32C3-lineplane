// 版本流水號: r4 (2026-09-14) 校正旗標時效改 10 秒(GG)
// 舊: r3 (2026-09-14) 校正旗標時效(安全審查 A4):設定後通電 10 分鐘沒拔電就取消;軟體重開(不是上電)開機看到旗標就取消;事件 26
// 舊: r2 (2026-09-14) 開機是否允許上電自動倒數:只認上電重置;序列指令 powerontest 讓下一次軟體重開也算(測試用,校正不受影響)
// 舊: r1 (2026-09-13) 初版:電變校正旗標(下次通電進入校正)
#include "esc_service.h"
#include <Preferences.h>
#include <esp_system.h>
#include "event_log.h"

static const char *const PREF_NAMESPACE = "lpesc";
static const char *const KEY_CALIB = "calib";
static const char *const KEY_POWERON_TEST = "pwtest";

static bool pending = false;
static bool powerOnBoot = false;
static bool autoStartBoot = false;
static uint32_t pendingSinceMs = 0;   // 這次開機設定旗標的時刻(0 = 沒有或開機前就設的)

static bool writeFlag(bool on) {
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return false;
  const bool ok = prefs.putUChar(KEY_CALIB, on ? 1 : 0) == 1;
  prefs.end();
  return ok;
}

bool escCalibTakeAtBoot() {
  powerOnBoot = esp_reset_reason() == ESP_RST_POWERON;
  autoStartBoot = powerOnBoot;
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return false;
  // 測試旗標只給自動倒數用,讀到就刪(只生效一次). 電變校正仍然只認真正的上電.
  if (prefs.isKey(KEY_POWERON_TEST)) {
    if (prefs.getUChar(KEY_POWERON_TEST, 0)) autoStartBoot = true;
    prefs.remove(KEY_POWERON_TEST);
  }
  pending = prefs.getUChar(KEY_CALIB, 0) != 0;
  bool take = false;
  if (pending && powerOnBoot) {
    // 先清旗標再開始校正:校正途中斷電,下次通電也不會又進校正.
    take = prefs.putUChar(KEY_CALIB, 0) == 1;
    if (take) pending = false;
  } else if (pending) {
    // 軟體重開(網頁重開機,OTA 更新完,當機或電壓不足重開)看到旗標就取消(GG 2026-09-14 安全審查 A4):
    // 旗標只給「設定後馬上拔電再接電」用. r2 以前保留到下一次真的上電,幾天後裝著螺旋槳接電池就是全速.
    if (prefs.putUChar(KEY_CALIB, 0) == 1) {
      pending = false;
      eventLog(EV_CALIB_CLEAR, 2);
    }
  }
  prefs.end();
  return take;
}

bool escCalibPending() { return pending; }

const char *escCalibSetPending(bool on) {
  if (!writeFlag(on)) return "savefail";
  pending = on;
  pendingSinceMs = on ? (millis() | 1) : 0;
  return nullptr;
}

static uint32_t expireMs = ESC_CALIB_EXPIRE_MS;
void escCalibTestSetExpire(uint32_t sec) { expireMs = sec * 1000UL; }

float escCalibExpireRemainS(uint32_t nowMs) {
  if (!pending || !pendingSinceMs) return -1;
  const uint32_t el = (int32_t)(nowMs - pendingSinceMs) > 0 ? nowMs - pendingSinceMs : 0;
  return el >= expireMs ? 0 : (expireMs - el) / 1000.0f;
}

void escCalibTick(uint32_t nowMs) {
  // 設定後通電超過時效(10 秒)還沒拔電:使用者多半忘了,取消旗標
  if (pending && pendingSinceMs && escCalibExpireRemainS(nowMs) <= 0) {
    if (writeFlag(false)) {
      pending = false;
      pendingSinceMs = 0;
      eventLog(EV_CALIB_CLEAR, 1);
      Serial.println(F("ESC calibration flag expired (no power cycle within the time limit)"));
    }
  }
}

bool escBootWasPowerOn() { return powerOnBoot; }

bool escBootAllowsAutoStart() { return autoStartBoot; }

bool escPowerOnTestArm() {
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return false;
  const bool ok = prefs.putUChar(KEY_POWERON_TEST, 1) == 1;
  prefs.end();
  return ok;
}
