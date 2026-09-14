// 版本流水號: r1 (2026-09-13) 初版:事件紀錄(通電後的重要事件與原因,記憶體環形緩衝,斷電清除)
#include "event_log.h"

static EventRecord ring[EVENT_LOG_CAPACITY];
static uint32_t total = 0;
static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;

void eventLog(EventType type, uint8_t arg, float a, float b) {
  EventRecord r = {millis(), (uint8_t)type, arg, 0, a, b};
  portENTER_CRITICAL(&lock);
  ring[total % EVENT_LOG_CAPACITY] = r;
  ++total;
  portEXIT_CRITICAL(&lock);
}

uint32_t eventLogTotal() {
  portENTER_CRITICAL(&lock);
  const uint32_t t = total;
  portEXIT_CRITICAL(&lock);
  return t;
}

uint32_t eventLogOldest() {
  const uint32_t t = eventLogTotal();
  return t > EVENT_LOG_CAPACITY ? t - EVENT_LOG_CAPACITY : 0;
}

bool eventLogGet(uint32_t seq, EventRecord &out) {
  bool ok = false;
  portENTER_CRITICAL(&lock);
  const uint32_t oldest = total > EVENT_LOG_CAPACITY ? total - EVENT_LOG_CAPACITY : 0;
  if (seq >= oldest && seq < total) {
    out = ring[seq % EVENT_LOG_CAPACITY];
    ok = true;
  }
  portEXIT_CRITICAL(&lock);
  return ok;
}
