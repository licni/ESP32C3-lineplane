// 版本流水號: r4 (2026-09-14) sim pulse 加延遲參數(韌體寫入中 loop 被佔住收不到序列指令,要事先排好推力)
// 舊: r3 (2026-09-13) 重新定姿那一拍不加抖動與脈衝(抖動負半週讓定姿變倒飛 180°)
// 舊: r2 (2026-09-13) 關閉模擬時用真的讀值重新定姿
// 舊: r1 (2026-09-13) 初版:感測器模擬注入,GPIO5 脈寬量測,狀態燈腳位取樣(全功能測試用)
#define LP_TEST_HOOKS_IMPL
#include "test_hooks.h"
#include "event_log.h"
#include "pins_config.h"
#include "esp_timer.h"
#include "esp_system.h"
#include "hal/gpio_ll.h"

static const uint8_t PIN_TEST_CAPTURE = 5;   // GG 插的跳線:GPIO5 ↔ GPIO4

// --- 感測器模擬 ----------------------------------------------------------------
static portMUX_TYPE simLock = portMUX_INITIALIZER_UNLOCKED;
static bool simOn = false;
static bool simFail = false;
static bool simReinit = false;
static float simAcc[3] = {0, 0, 1};
static float simGyro[3] = {0, 0, 0};
static float simVibAmp = 0, simVibHz = 20;
static float simPulse[3] = {0, 0, 0};
static uint32_t simPulseUntilMs = 0;
static uint32_t simPulseStartMs = 0;   // 0 = 立刻開始;延遲脈衝用(韌體寫入中 loop 被佔住,序列指令要事先排好)

static void setAtt(float pitchDeg, float rollDeg, float mag) {
  const float p = pitchDeg * DEG_TO_RAD, r = rollDeg * DEG_TO_RAD;
  // 與 imu.cpp initFromAccel 相反:機頭朝上 x 為正,左翼朝上 y 為正
  simAcc[0] = mag * sinf(p);
  simAcc[1] = mag * cosf(p) * sinf(r);
  simAcc[2] = mag * cosf(p) * cosf(r);
}

void testSimCommand(const char *args, char *reply, size_t n) {
  char word[8] = {0};
  float a = 0, b = 0, c = 0;
  const int got = sscanf(args, "%7s %f %f %f", word, &a, &b, &c);
  bool wasOn;
  portENTER_CRITICAL(&simLock);
  wasOn = simOn;
  bool ok = true;
  if (got >= 1 && !strcmp(word, "off")) {
    simOn = false;
    simFail = false;
    simVibAmp = 0;
    simPulseUntilMs = simPulseStartMs = 0;
    for (uint8_t i = 0; i < 3; ++i) simGyro[i] = 0;
    simReinit = true;
  } else if (got >= 3 && (!strcmp(word, "att") || !strcmp(word, "attq"))) {
    setAtt(a, b, got >= 4 ? c : 1.0f);
    simReinit = !strcmp(word, "att");
    simOn = true;
  } else if (got >= 4 && !strcmp(word, "acc")) {
    simAcc[0] = a, simAcc[1] = b, simAcc[2] = c;
    simOn = true;
  } else if (got >= 4 && !strcmp(word, "gyro")) {
    simGyro[0] = a, simGyro[1] = b, simGyro[2] = c;
    simOn = true;
  } else if (got >= 2 && !strcmp(word, "vib")) {
    simVibAmp = a;
    if (got >= 3 && b > 0) simVibHz = b;
    simOn = true;
  } else if (got >= 2 && !strcmp(word, "fail")) {
    simFail = a != 0;
    simOn = true;
  } else {
    ok = false;
  }
  portEXIT_CRITICAL(&simLock);

  // pulse 的軸是字母,另外解析
  if (!ok && !strncmp(args, "pulse ", 6)) {
    char axis = 0;
    float g = 0, ms = 0, delayMs = 0;
    if (sscanf(args + 6, " %c %f %f %f", &axis, &g, &ms, &delayMs) >= 3 && axis >= 'x' && axis <= 'z' && ms > 0 && delayMs >= 0 &&
        delayMs <= 120000) {
      portENTER_CRITICAL(&simLock);
      for (uint8_t i = 0; i < 3; ++i) simPulse[i] = 0;
      simPulse[axis - 'x'] = g;
      const uint32_t now = millis();
      simPulseStartMs = delayMs > 0 ? (now + (uint32_t)delayMs) | 1 : 0;
      simPulseUntilMs = (now + (uint32_t)delayMs + (uint32_t)ms) | 1;
      simOn = true;
      portEXIT_CRITICAL(&simLock);
      ok = true;
    }
  }
  if (!ok && got < 1) {
    snprintf(reply, n, "sim on=%d fail=%d acc=%.3f,%.3f,%.3f gyro=%.1f,%.1f,%.1f vib=%.2f@%.0fHz", simOn, simFail,
             simAcc[0], simAcc[1], simAcc[2], simGyro[0], simGyro[1], simGyro[2], simVibAmp, simVibHz);
    return;
  }
  if (!ok) {
    snprintf(reply, n, "ERR sim usage: att p r [g] | attq p r [g] | acc x y z | gyro x y z | vib amp [hz] | pulse x|y|z g ms [delayMs] | fail 0|1 | off");
    return;
  }
  const bool nowOn = simOn;
  if (nowOn != wasOn) eventLog(EV_SIM, nowOn ? 1 : 0);
  snprintf(reply, n, "OK sim %s", nowOn ? "on" : "off");
}

void testSimApply(ImuReading &r, bool &readOk, uint32_t nowMs) {
  if (!simOn) {
    if (simReinit) {   // 剛關閉模擬:用真的讀值重新定姿,不讓濾波從模擬的角度慢慢收斂回來
      simReinit = false;
      attitudeReset();
    }
    return;
  }
  float acc[3], gyro[3], pulse[3], vibAmp, vibHz;
  bool fail, reinit, pulseOn;
  portENTER_CRITICAL(&simLock);
  memcpy(acc, simAcc, sizeof(acc));
  memcpy(gyro, simGyro, sizeof(gyro));
  memcpy(pulse, simPulse, sizeof(pulse));
  vibAmp = simVibAmp;
  vibHz = simVibHz;
  fail = simFail;
  reinit = simReinit;
  simReinit = false;
  const bool pulseStarted = !simPulseStartMs || (int32_t)(nowMs - simPulseStartMs) >= 0;
  pulseOn = simPulseUntilMs && pulseStarted && (int32_t)(nowMs - simPulseUntilMs) < 0;
  if (simPulseUntilMs && pulseStarted && !pulseOn) simPulseUntilMs = simPulseStartMs = 0;
  portEXIT_CRITICAL(&simLock);

  if (fail) {
    readOk = false;
    return;
  }
  readOk = true;
  // 重新定姿那一拍只給靜止姿態:抖動 1.5g 的負半週會讓 Z 讀到 -0.5g,單筆定姿直接變成倒飛 180°
  // (全功能測試段 3 第一次跑踩到,正好反向時 Mahony 叉積為 0 拉不回來)
  const bool clean = reinit;
  for (uint8_t i = 0; i < 3; ++i) {
    r.accG[i] = acc[i] + (pulseOn && !clean ? pulse[i] : 0);
    r.gyroDps[i] = gyro[i];
  }
  if (vibAmp > 0 && !clean) r.accG[2] += vibAmp * sinf(2 * PI * vibHz * (nowMs % 100000) / 1000.0f);
  r.accMagG = sqrtf(r.accG[0] * r.accG[0] + r.accG[1] * r.accG[1] + r.accG[2] * r.accG[2]);
  r.saturated = false;
  for (uint8_t i = 0; i < 3; ++i)
    if (fabsf(r.accG[i]) >= 16.0f || fabsf(r.gyroDps[i]) >= 2000.0f) r.saturated = true;
  if (reinit) attitudeReset();
}

bool testSimActive() { return simOn; }

// 覆寫值放 RTC 記憶體:軟體重開(測試常用 /api/reboot)保留,真的拔電再接電清掉. 上半部是校驗碼,上電後的亂值不會被誤認.
static RTC_NOINIT_ATTR uint32_t armOverrideRtc;
static const uint32_t ARM_OVERRIDE_MAGIC = 0xA5C30000;
static volatile int8_t armOverride = -1;
void testArmOverrideBoot() {
  if (esp_reset_reason() != ESP_RST_POWERON && (armOverrideRtc & 0xFFFF0000) == ARM_OVERRIDE_MAGIC)
    armOverride = (int8_t)(armOverrideRtc & 0xFF);
  else
    armOverrideRtc = 0;
}
void testArmOverrideSet(int8_t v) {
  armOverride = v;
  armOverrideRtc = v < 0 ? 0 : (ARM_OVERRIDE_MAGIC | (uint8_t)v);
}
int8_t testArmOverride() { return armOverride; }

// --- GPIO5 脈寬量測 ------------------------------------------------------------
static portMUX_TYPE capLock = portMUX_INITIALIZER_UNLOCKED;
static const uint8_t CAP_RING = 16;
static volatile bool capOn = false;
static int64_t capRiseUs = 0;
static int64_t capLastEdgeUs = 0;
static uint32_t capHigh[CAP_RING], capPeriod[CAP_RING];
static uint8_t capIdx = 0, capFilled = 0;
static uint32_t capPulses = 0, capMin = UINT32_MAX, capMax = 0;

static uint8_t capPin = PIN_TEST_CAPTURE;

static void IRAM_ATTR capIsr() {
  const int64_t t = esp_timer_get_time();
  const bool level = gpio_ll_get_level(GPIO_LL_GET_HW(GPIO_PORT_0), capPin);
  portENTER_CRITICAL_ISR(&capLock);
  capLastEdgeUs = t;
  if (level) {
    if (capRiseUs) capPeriod[capIdx] = (uint32_t)(t - capRiseUs);
    capRiseUs = t;
  } else if (capRiseUs) {
    const uint32_t w = (uint32_t)(t - capRiseUs);
    capHigh[capIdx] = w;
    capIdx = (capIdx + 1) % CAP_RING;
    if (capFilled < CAP_RING) ++capFilled;
    ++capPulses;
    if (w < capMin) capMin = w;
    if (w > capMax) capMax = w;
  }
  portEXIT_CRITICAL_ISR(&capLock);
}

const char *testPwmCapStart() {
  if (capOn) testPwmCapStop();
  capPin = PIN_TEST_CAPTURE;
  pinMode(capPin, INPUT);
  attachInterrupt(capPin, capIsr, CHANGE);
  testPwmCapResetMinMax();
  capOn = true;
  return nullptr;
}

// 量輸出腳自己的電位(例如 GPIO3 收輪舵機):不改腳位模式,attachInterrupt 會打開輸入緩衝,LEDC 照常輸出
const char *testPwmCapStartPin(uint8_t pin) {
  if (capOn) testPwmCapStop();
  capPin = pin;
  attachInterrupt(capPin, capIsr, CHANGE);
  testPwmCapResetMinMax();
  capOn = true;
  return nullptr;
}

void testPwmCapStop() {
  if (!capOn) return;
  detachInterrupt(capPin);
  capOn = false;
}

void testPwmCapResetMinMax() {
  portENTER_CRITICAL(&capLock);
  capMin = UINT32_MAX;
  capMax = 0;
  capFilled = 0;
  capRiseUs = 0;
  portEXIT_CRITICAL(&capLock);
}

static uint32_t median(uint32_t *v, uint8_t n) {
  for (uint8_t i = 1; i < n; ++i) {
    const uint32_t x = v[i];
    int8_t j = i - 1;
    while (j >= 0 && v[j] > x) {
      v[j + 1] = v[j];
      --j;
    }
    v[j + 1] = x;
  }
  return n ? v[n / 2] : 0;
}

void testPwmCapGet(PwmCapStats &o) {
  uint32_t hi[CAP_RING], per[CAP_RING];
  uint8_t n, idx;
  int64_t last;
  portENTER_CRITICAL(&capLock);
  n = capFilled;
  idx = capIdx;
  memcpy(hi, capHigh, sizeof(hi));
  memcpy(per, capPeriod, sizeof(per));
  o.pulses = capPulses;
  o.minHighUs = capMin == UINT32_MAX ? 0 : capMin;
  o.maxHighUs = capMax;
  last = capLastEdgeUs;
  portEXIT_CRITICAL(&capLock);
  o.active = capOn;
  // 環形緩衝還沒填滿時,有效資料在最前面 n 格(從 capIdx 往回數);填滿後全部有效
  uint32_t h[CAP_RING], p[CAP_RING];
  for (uint8_t i = 0; i < n; ++i) {
    const uint8_t k = (idx + CAP_RING - 1 - i) % CAP_RING;
    h[i] = hi[k];
    p[i] = per[k];
  }
  o.highUs = median(h, n);
  o.periodUs = median(p, n);
  o.edgeAgeMs = last ? (uint32_t)((esp_timer_get_time() - last) / 1000) : UINT32_MAX;
}

// --- 狀態燈腳位取樣 ------------------------------------------------------------
static const uint8_t LED_RUNS = 48;
static volatile uint32_t ledCapUntilMs = 0;
static bool ledCapInit = false;
static bool ledPrev = false;
static uint32_t ledRunStartMs = 0;
static uint16_t ledRunMs[LED_RUNS];
static bool ledRunLevel[LED_RUNS];
static uint8_t ledRunCount = 0;
static bool ledCapDone = false;

void testLedCaptureStart(uint32_t durationMs) {
  gpio_ll_input_enable(GPIO_LL_GET_HW(GPIO_PORT_0), PIN_STATUS_LED);   // 輸出腳也打開輸入緩衝,讀腳位實際電位
  ledRunCount = 0;
  ledCapDone = false;
  ledCapInit = false;
  ledCapUntilMs = (millis() + durationMs) | 1;
}

void testLedSample(uint32_t nowMs) {
  if (!ledCapUntilMs) return;
  const bool pad = gpio_ll_get_level(GPIO_LL_GET_HW(GPIO_PORT_0), PIN_STATUS_LED);
  const bool on = pad != STATUS_LED_ACTIVE_LOW;
  if (!ledCapInit) {
    ledCapInit = true;
    ledPrev = on;
    ledRunStartMs = nowMs;
  }
  const bool end = (int32_t)(nowMs - ledCapUntilMs) >= 0;
  if (on != ledPrev || end) {
    if (ledRunCount < LED_RUNS) {
      ledRunMs[ledRunCount] = (uint16_t)min<uint32_t>(nowMs - ledRunStartMs, 65535);
      ledRunLevel[ledRunCount] = ledPrev;
      ++ledRunCount;
    }
    ledPrev = on;
    ledRunStartMs = nowMs;
  }
  if (end) {
    ledCapUntilMs = 0;
    ledCapDone = true;
  }
}

void testLedCaptureReport(char *out, size_t n) {
  if (!ledCapDone) {
    snprintf(out, n, "led busy");
    return;
  }
  size_t len = snprintf(out, n, "led runs=%u", ledRunCount);
  for (uint8_t i = 0; i < ledRunCount && len + 12 < n; ++i)
    len += snprintf(out + len, n - len, " %c%u", ledRunLevel[i] ? '+' : '-', ledRunMs[i]);
}
