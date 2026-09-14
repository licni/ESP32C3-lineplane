// 版本流水號: r2 (2026-09-13) 修正每筆實際 105ms(區間起點改走固定 100ms 格點)
// 舊: r1 (2026-09-13) 初版:0.1 秒一筆的環形紀錄(角度,油門,G 力,Z 抖動,短尖峰,手勢推力,狀態)
#include "flight_log.h"

static FlightLogSample buffer[FLIGHT_LOG_CAPACITY];
static volatile uint32_t total = 0;

// 目前區間的累積
static bool slotOpen = false;
static uint32_t slotStartMs = 0;
static FlightLogSample slot;
static float slotAcc = 0, slotVib = 0, slotSpike = 0, slotPush = -100;

static uint8_t clampU8(float v) { return v <= 0 ? 0 : (v >= 255 ? 255 : (uint8_t)lroundf(v)); }
static int8_t clampI8(float v) { return v <= -127 ? -127 : (v >= 127 ? 127 : (int8_t)lroundf(v)); }

void flightLogFeed(float pitchDeg, float throttlePct, float accMagG, float vibG, float spikeG, float pushG,
                   uint8_t state, uint8_t flags, uint32_t nowMs) {
  if (!slotOpen) {
    slotOpen = true;
    // 區間起點走固定 100ms 格點. r1 用「這一拍」當起點:收尾那一拍算進上一區,下一區從再下一拍才開,
    // 每筆實際 105ms,時間軸慢 5%(全功能測試段 4:33 秒飛行只有 314 筆). 落後超過一格(例如剛開機)才重新對齊.
    slotStartMs = (slotStartMs && nowMs - slotStartMs < 2 * FLIGHT_LOG_SAMPLE_MS) ? slotStartMs + FLIGHT_LOG_SAMPLE_MS : nowMs;
    slotAcc = slotVib = slotSpike = 0;
    slotPush = -100;
    slot.flags = 0;
  }
  if (accMagG > slotAcc) slotAcc = accMagG;
  if (vibG > slotVib) slotVib = vibG;
  if (spikeG > slotSpike) slotSpike = spikeG;
  if (pushG > slotPush) slotPush = pushG;
  slot.flags |= flags;   // 區間內出現過就記
  // 角度,油門,狀態取區間最後一個值
  slot.pitchDeg = clampI8(pitchDeg);
  slot.throttlePct = clampU8(throttlePct);
  slot.state = state;

  if (nowMs - slotStartMs < FLIGHT_LOG_SAMPLE_MS) return;
  slot.accMaxDg = clampU8(slotAcc * 10);
  slot.vibCg2 = clampU8(slotVib * 50);
  slot.spikeDg = clampU8(slotSpike * 10);
  slot.pushDg = clampI8(slotPush * 10);
  buffer[total % FLIGHT_LOG_CAPACITY] = slot;   // 先寫資料
  total = total + 1;                             // 再推進計數
  slotOpen = false;
}

uint32_t flightLogTotal() { return total; }

uint32_t flightLogOldest() {
  const uint32_t t = total;
  // 環形已滿時丟掉最舊一筆:讀取期間它可能正被覆寫
  return t > FLIGHT_LOG_CAPACITY ? t - FLIGHT_LOG_CAPACITY + 1 : 0;
}

bool flightLogGet(uint32_t index, FlightLogSample &out) {
  if (index >= total || index < flightLogOldest()) return false;
  out = buffer[index % FLIGHT_LOG_CAPACITY];
  return true;
}
