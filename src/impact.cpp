// 版本流水號: r2 (2026-09-13) 加地面滑行抖動判斷
// 舊: r1 (2026-09-13) 初版:衝擊尖峰偵測(分辨機輪觸地的短尖峰與特技動作的持續 G 力)
#include "impact.h"

static const float BASE_TAU_S = 0.3f;
static const float SPIKE_START_G = 1.0f;
static const float SPIKE_END_G = 0.5f;

static const float ROLL_LPF_TAU_S = 0.02f;   // 約 8Hz
static const float ROLL_RMS_TAU_S = 0.5f;

void GroundRollDetector::reset() {
  initialized_ = false;
  meanSquare_ = 0;
  vibG_ = 0;
  holdS_ = 0;
  level_ = false;
}

void GroundRollDetector::update(float az, float pitchDeg, float rollDeg, float dt, float vibThr, float tiltDeg) {
  if (!initialized_) {
    lpf_ = az;
    initialized_ = true;
  }
  lpf_ += (az - lpf_) * (dt / ROLL_LPF_TAU_S);
  const float hp = az - lpf_;
  meanSquare_ += (hp * hp - meanSquare_) * (dt / ROLL_RMS_TAU_S);
  vibG_ = sqrtf(meanSquare_);
  level_ = fabsf(pitchDeg) <= tiltDeg && fabsf(rollDeg) <= tiltDeg;
  if (vibG_ >= vibThr && level_) holdS_ += dt;
  else holdS_ = max(0.0f, holdS_ - 2 * dt);
}

void ImpactDetector::reset() {
  initialized_ = false;
  active_ = false;
  peakG_ = 0;
  elapsedMs_ = 0;
}

bool ImpactDetector::update(float accMagG, float dt, ImpactEvent &event) {
  if (!initialized_) {
    baseG_ = accMagG;
    initialized_ = true;
  }
  const float excess = accMagG - baseG_;
  bool fired = false;
  if (!active_) {
    if (excess > SPIKE_START_G) {
      active_ = true;
      peakG_ = excess;
      elapsedMs_ = 0;
    }
  } else {
    elapsedMs_ += dt * 1000.0f;
    if (excess > peakG_) peakG_ = excess;
    if (excess < SPIKE_END_G) {
      event.peakG = peakG_;
      event.durationMs = (uint16_t)min(elapsedMs_, 60000.0f);
      active_ = false;
      fired = true;
    }
  }
  if (!active_ || elapsedMs_ > IMPACT_MAX_SPIKE_MS) baseG_ += (accMagG - baseG_) * (dt / BASE_TAU_S);
  return fired;
}
