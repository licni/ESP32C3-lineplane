// 版本流水號: r1 (2026-09-13) 初版:機輪收腳舵機(GPIO3,50Hz,限位行程,反轉,速度)
#include "gear.h"
#include "pins_config.h"

static const uint8_t GEAR_RESOLUTION_BITS = 14;
static float pos = 0;          // 0 放下,1 收起
static uint16_t outUs = 0;
static bool attached = false;

static uint16_t posToUs(float p, const SharedSettings &cfg) {
  const float downUs = cfg.gearReverse ? cfg.gearMaxUs : cfg.gearMinUs;
  const float upUs = cfg.gearReverse ? cfg.gearMinUs : cfg.gearMaxUs;
  return (uint16_t)lroundf(downUs + (upUs - downUs) * p);
}

static void write(uint16_t us) {
  if (!attached || us == outUs) return;
  outUs = us;
  const uint32_t periodUs = 1000000UL / GEAR_PWM_HZ;
  ledcWrite(PIN_GEAR_SERVO, (uint32_t)((uint64_t)us * ((1UL << GEAR_RESOLUTION_BITS) - 1) / periodUs));
}

void gearBegin(const SharedSettings &cfg) {
  pos = 0;
  attached = ledcAttach(PIN_GEAR_SERVO, GEAR_PWM_HZ, GEAR_RESOLUTION_BITS);
  outUs = 0;
  write(posToUs(0, cfg));
}

void gearUpdate(bool wantUp, const SharedSettings &cfg, float dt) {
  const float target = wantUp ? 1.0f : 0.0f;
  if (cfg.gearTravelSec <= 0) {
    pos = target;
  } else {
    const float step = dt / cfg.gearTravelSec;
    if (pos < target) pos = min(target, pos + step);
    else if (pos > target) pos = max(target, pos - step);
  }
  write(posToUs(pos, cfg));
}

float gearPosition() { return pos; }
uint16_t gearCurrentUs() { return outUs; }
