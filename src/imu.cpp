// 版本流水號: r2 (2026-09-13) 靜止判斷的 1g 容許範圍放寬到 ±0.3g(副廠晶片實測靜止讀 1.12g)
#include "imu.h"
#include <Wire.h>

// --- MPU6050 暫存器 ----------------------------------------------------------
static const uint8_t MPU_ADDRESS = 0x68;
static const uint8_t REG_SMPLRT_DIV = 0x19;
static const uint8_t REG_CONFIG = 0x1A;
static const uint8_t REG_GYRO_CONFIG = 0x1B;
static const uint8_t REG_ACCEL_CONFIG = 0x1C;
static const uint8_t REG_ACCEL_XOUT_H = 0x3B;
static const uint8_t REG_PWR_MGMT_1 = 0x6B;
static const uint8_t REG_WHO_AM_I = 0x75;

static const float GYRO_LSB_PER_DPS = 16.4f;   // ±2000dps
static const float ACC_LSB_PER_G = 2048.0f;    // ±16g
static const int16_t RAW_SATURATION = 32700;

// --- 姿態濾波參數(模擬結果,見 docs/開發紀錄.md 階段 0) ------------------------------
static const float KP_GROUND = 2.0f;     // 地面:時間常數約 0.5 秒,快速貼齊加速度計
static const float KP_FLIGHT = 0.3f;     // 飛行:時間常數約 3 秒,短期信陀螺儀
static const float ACC_TRUST_BAND_G = 0.4f;   // 補償後大小偏離 1g 越多越不信,偏 0.4g 以上完全不用
static const float GRAVITY = 9.80665f;
static const float DEG_PER_RAD = 57.29578f;

// --- 靜止偵測 -----------------------------------------------------------------
static const uint16_t STILL_WINDOW_SAMPLES = 100;     // 200Hz × 0.5 秒
static const float STILL_GYRO_RANGE_DPS = 4.0f;       // 窗內每軸擺幅上限
static const float STILL_ACC_RANGE_G = 0.06f;         // 窗內加速度大小擺幅上限
// 加速度大小的寬鬆合理範圍. 靜止的判斷依據是「窗內擺幅小」,不是「剛好 1g」:
// 副廠 MPU6050 刻度與零點誤差常達 10% 以上(GG 開發板靜止讀 1.12g),訂太緊會永遠判定沒靜止,
// 陀螺儀零點也就永遠學不到. 這個範圍只用來排除自由落體與持續加速這種不可能是靜止的情況.
static const float STILL_ACC_MAG_TOL_G = 0.3f;
static const float STILL_WINDOW_SECONDS = 0.5f;

static int8_t orientMatrix[3][3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};  // 機身 = M × 晶片
static float gyroBiasDps[3] = {0, 0, 0};
static bool gyroBiasLearned = false;

static float q0 = 1, q1 = 0, q2 = 0, q3 = 0;
static bool attitudeNeedsInit = true;

static uint16_t winCount = 0;
static float winGyroMin[3], winGyroMax[3], winGyroSum[3];
static float winAccMin, winAccMax;
static bool stillNow = false;
static float stillSeconds = 0;

static bool writeRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission() == 0;
}

static bool readRegister(uint8_t reg, uint8_t &value) {
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDRESS, 1) != 1) return false;
  value = (uint8_t)Wire.read();
  return true;
}

bool imuBegin() {
  uint8_t who = 0;
  if (!readRegister(REG_WHO_AM_I, who)) return false;
  // 正版 MPU6050 回 0x68;市面相容晶片常見 0x70(MPU6500 系)與 0x98. 這幾個暫存器位置相同.
  if (who != 0x68 && who != 0x70 && who != 0x98) {
    Serial.printf("ERR MPU WHO_AM_I=0x%02X\n", who);
    return false;
  }
  if (!writeRegister(REG_PWR_MGMT_1, 0x80)) return false;   // 重置
  delay(100);
  if (!writeRegister(REG_PWR_MGMT_1, 0x01)) return false;   // 時脈用陀螺儀 X 軸 PLL,比內部 RC 穩
  delay(50);
  // DLPF 3:加速度 44Hz / 陀螺儀 42Hz,延遲約 5ms. 濾掉馬達震動又不拖慢反應.
  if (!writeRegister(REG_CONFIG, 0x03)) return false;
  if (!writeRegister(REG_SMPLRT_DIV, 4)) return false;      // 1kHz / (1+4) = 200Hz
  // 特技直角彎可達 400°/秒以上,撞擊偵測要看到 14g,所以兩個量程都開到最大.
  if (!writeRegister(REG_GYRO_CONFIG, 0x18)) return false;  // ±2000dps
  if (!writeRegister(REG_ACCEL_CONFIG, 0x18)) return false; // ±16g
  attitudeNeedsInit = true;
  return true;
}

static void mapToBody(const float chip[3], float body[3]) {
  for (uint8_t i = 0; i < 3; ++i)
    body[i] = orientMatrix[i][0] * chip[0] + orientMatrix[i][1] * chip[1] + orientMatrix[i][2] * chip[2];
}

static void updateStillWindow(const float gyroChipDps[3], float accMag) {
  if (winCount == 0) {
    for (uint8_t i = 0; i < 3; ++i) {
      winGyroMin[i] = winGyroMax[i] = gyroChipDps[i];
      winGyroSum[i] = 0;
    }
    winAccMin = winAccMax = accMag;
  }
  for (uint8_t i = 0; i < 3; ++i) {
    if (gyroChipDps[i] < winGyroMin[i]) winGyroMin[i] = gyroChipDps[i];
    if (gyroChipDps[i] > winGyroMax[i]) winGyroMax[i] = gyroChipDps[i];
    winGyroSum[i] += gyroChipDps[i];
  }
  if (accMag < winAccMin) winAccMin = accMag;
  if (accMag > winAccMax) winAccMax = accMag;
  if (++winCount < STILL_WINDOW_SAMPLES) return;

  bool still = (winAccMax - winAccMin) < STILL_ACC_RANGE_G &&
               fabsf(winAccMin - 1.0f) < STILL_ACC_MAG_TOL_G && fabsf(winAccMax - 1.0f) < STILL_ACC_MAG_TOL_G;
  for (uint8_t i = 0; i < 3; ++i)
    if ((winGyroMax[i] - winGyroMin[i]) > STILL_GYRO_RANGE_DPS) still = false;
  winCount = 0;

  stillNow = still;
  stillSeconds = still ? stillSeconds + STILL_WINDOW_SECONDS : 0;
}

bool imuRead(ImuReading &out) {
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(REG_ACCEL_XOUT_H);
  if (Wire.endTransmission(false) != 0) return false;
  const uint8_t count = 14;
  if (Wire.requestFrom((int)MPU_ADDRESS, (int)count) != count || Wire.available() < count) return false;
  uint8_t d[14];
  for (uint8_t i = 0; i < count; ++i) d[i] = (uint8_t)Wire.read();

  float accChip[3], gyroChipRaw[3];
  bool saturated = false;
  for (uint8_t axis = 0; axis < 3; ++axis) {
    const int16_t a = (int16_t)(((uint16_t)d[axis * 2] << 8) | d[axis * 2 + 1]);
    const int16_t g = (int16_t)(((uint16_t)d[8 + axis * 2] << 8) | d[9 + axis * 2]);
    if (a > RAW_SATURATION || a < -RAW_SATURATION || g > RAW_SATURATION || g < -RAW_SATURATION) saturated = true;
    accChip[axis] = a / ACC_LSB_PER_G;
    gyroChipRaw[axis] = g / GYRO_LSB_PER_DPS;
  }
  const float accMag = sqrtf(accChip[0] * accChip[0] + accChip[1] * accChip[1] + accChip[2] * accChip[2]);
  updateStillWindow(gyroChipRaw, accMag);

  float gyroChip[3];
  for (uint8_t i = 0; i < 3; ++i) gyroChip[i] = gyroChipRaw[i] - gyroBiasDps[i];
  mapToBody(gyroChip, out.gyroDps);
  mapToBody(accChip, out.accG);
  out.accMagG = accMag;
  out.saturated = saturated;
  return true;
}

bool imuSetOrientation(uint8_t noseAxis, uint8_t upAxis) {
  if (noseAxis > IMU_AXIS_NZ || upAxis > IMU_AXIS_NZ) return false;
  if ((noseAxis / 2) == (upAxis / 2)) return false;   // 同一軸(含反向)
  int8_t x[3] = {0, 0, 0}, z[3] = {0, 0, 0};
  x[noseAxis / 2] = (noseAxis % 2) ? -1 : 1;
  z[upAxis / 2] = (upAxis % 2) ? -1 : 1;
  // y(左翼) = z × x
  int8_t y[3] = {(int8_t)(z[1] * x[2] - z[2] * x[1]), (int8_t)(z[2] * x[0] - z[0] * x[2]),
                 (int8_t)(z[0] * x[1] - z[1] * x[0])};
  for (uint8_t i = 0; i < 3; ++i) {
    orientMatrix[0][i] = x[i];
    orientMatrix[1][i] = y[i];
    orientMatrix[2][i] = z[i];
  }
  attitudeNeedsInit = true;
  return true;
}

void attitudeReset() { attitudeNeedsInit = true; }

static void initFromAccel(const float a[3]) {
  // 靜止時加速度計讀到的是「上方」:機頭朝上 x 為正,左翼朝上 y 為正.
  const float pitch = atan2f(a[0], sqrtf(a[1] * a[1] + a[2] * a[2]));
  const float roll = atan2f(a[1], a[2]);
  // q = qy(-pitch) ⊗ qx(roll)
  const float cy = cosf(-pitch * 0.5f), sy = sinf(-pitch * 0.5f);
  const float cx = cosf(roll * 0.5f), sx = sinf(roll * 0.5f);
  q0 = cy * cx;
  q1 = cy * sx;
  q2 = sy * cx;
  q3 = -sy * sx;
}

void attitudeUpdate(const ImuReading &r, float dt, float speedMps, bool inFlight) {
  // 馬達沒轉且靜止時學零點. 零點以晶片座標記錄,換安裝方位不必重學.
  // 用剛結束那一窗的平均:窗是 0.5 秒,winCount 歸零的那一刻 winGyroSum 仍是整窗總和.
  if (!inFlight && stillNow && winCount == 0) {
    float chipMean[3];
    for (uint8_t i = 0; i < 3; ++i) chipMean[i] = winGyroSum[i] / STILL_WINDOW_SAMPLES;
    const float k = gyroBiasLearned ? 0.3f : 1.0f;
    for (uint8_t i = 0; i < 3; ++i) gyroBiasDps[i] += (chipMean[i] - gyroBiasDps[i]) * k;
    gyroBiasLearned = true;
  }

  float ax = r.accG[0], ay = r.accG[1], az = r.accG[2];
  if (attitudeNeedsInit) {
    const float a[3] = {ax, ay, az};
    initFromAccel(a);
    attitudeNeedsInit = false;
    return;
  }

  float gx = r.gyroDps[0] / DEG_PER_RAD;
  float gy = r.gyroDps[1] / DEG_PER_RAD;
  float gz = r.gyroDps[2] / DEG_PER_RAD;

  if (speedMps > 0) {
    // 扣掉向心加速度 (0, r·V, -q·V),單位換成 g.
    ay -= gz * speedMps / GRAVITY;
    az += gy * speedMps / GRAVITY;
  }

  const float norm = sqrtf(ax * ax + ay * ay + az * az);
  if (!r.saturated && norm > 0.05f) {
    float trust = 1.0f - fabsf(norm - 1.0f) / ACC_TRUST_BAND_G;
    if (trust > 0) {
      const float kp = (inFlight ? KP_FLIGHT : KP_GROUND) * trust;
      ax /= norm;
      ay /= norm;
      az /= norm;
      const float vx = 2 * (q1 * q3 - q0 * q2);
      const float vy = 2 * (q0 * q1 + q2 * q3);
      const float vz = q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3;
      gx += kp * (ay * vz - az * vy);
      gy += kp * (az * vx - ax * vz);
      gz += kp * (ax * vy - ay * vx);
    }
  }

  const float h = 0.5f * dt;
  const float n0 = q0 + (-q1 * gx - q2 * gy - q3 * gz) * h;
  const float n1 = q1 + (q0 * gx + q2 * gz - q3 * gy) * h;
  const float n2 = q2 + (q0 * gy - q1 * gz + q3 * gx) * h;
  const float n3 = q3 + (q0 * gz + q1 * gy - q2 * gx) * h;
  const float s = sqrtf(n0 * n0 + n1 * n1 + n2 * n2 + n3 * n3);
  if (s < 1e-6f) {
    attitudeNeedsInit = true;
    return;
  }
  q0 = n0 / s;
  q1 = n1 / s;
  q2 = n2 / s;
  q3 = n3 / s;
}

float attitudePitchDeg() {
  float v = 2 * (q1 * q3 - q0 * q2);
  if (v > 1) v = 1;
  if (v < -1) v = -1;
  return asinf(v) * DEG_PER_RAD;
}

float attitudeRollDeg() {
  return atan2f(2 * (q0 * q1 + q2 * q3), q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * DEG_PER_RAD;
}

bool imuIsStill() { return stillNow; }
float imuStillSeconds() { return stillSeconds; }

void imuGyroBiasDps(float out[3]) {
  for (uint8_t i = 0; i < 3; ++i) out[i] = gyroBiasDps[i];
}
