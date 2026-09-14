// 版本流水號: r1 (2026-09-13) 初版:MPU6050 讀取,安裝方位,向心力補償 Mahony,靜止偵測與零點學習
#pragma once
#include <Arduino.h>
// ============================================================================
// 陀螺儀與姿態估算. 只允許控制工作呼叫(I2C 與濾波狀態都不上鎖).
//
// 座標:機身 FLU —— x=機頭,y=左翼,z=機背. 逆時針繞圈(從上往下看)偏航率為正.
// 機頭仰角:機頭方向與地平線的夾角,朝上為正,-90~+90 度,與滾轉無關(倒飛也成立).
//
// 為什麼要向心力補償:線控飛機繞圈的向心力約 3g,加速度計讀到的「下方」嚴重偏掉.
// 機身座標的運動加速度 = 角速度 × (飛行速度,0,0) = (0, r·V, -q·V),扣掉後再融合.
// 模擬驗證見 tools/sim_attitude.py 與 docs/開發紀錄.md 階段 0.
// ============================================================================

// 晶片軸代號:用在「哪一軸朝機頭,哪一軸朝機背」的安裝方位設定.
enum ImuAxis : uint8_t { IMU_AXIS_PX = 0, IMU_AXIS_NX, IMU_AXIS_PY, IMU_AXIS_NY, IMU_AXIS_PZ, IMU_AXIS_NZ };

struct ImuReading {
  float gyroDps[3];   // 機身座標,已扣零點
  float accG[3];      // 機身座標,原始比力(未扣向心力)
  float accMagG;      // 加速度大小
  bool saturated;     // 任一軸打到量程上限(撞擊或極端動作),這一筆的姿態不可信
};

// 初始化 MPU6050(量程 ±2000dps / ±16g,取樣 200Hz). 讀不到回 false.
bool imuBegin();
// 讀一筆並換算到機身座標. I2C 失敗回 false.
bool imuRead(ImuReading &out);
// 設定安裝方位. 兩軸不可同軸或反向,不合法回 false 且不改變現況.
bool imuSetOrientation(uint8_t noseAxis, uint8_t upAxis);
// 更新姿態. speedMps = 目前套用的飛行速度(馬達沒轉時給 0),inFlight 決定融合增益.
void attitudeUpdate(const ImuReading &r, float dt, float speedMps, bool inFlight);
// 重新以加速度計直接定姿(開機或故障恢復時).
void attitudeReset();

float attitudePitchDeg();
float attitudeRollDeg();

// 靜止偵測:以 0.5 秒為一窗,陀螺儀擺幅與加速度大小都在門檻內才算靜止.
// 馬達沒轉且靜止時自動學習陀螺儀零點.
bool imuIsStill();
float imuStillSeconds();          // 已連續靜止幾秒
void imuGyroBiasDps(float out[3]);  // 晶片座標的零點
