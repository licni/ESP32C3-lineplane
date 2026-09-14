// 版本流水號: r2 (2026-09-13) 電變校正(開機保持最高油門後回最低)與網頁手動輸出(心跳逾時回最低)
// 舊: r1 (2026-09-13) 由 main.cpp 拆出:控制工作與遙測快照
#pragma once
#include <Arduino.h>
// ============================================================================
// 控制工作(系統最高優先權,200Hz 固定節拍):讀陀螺儀,算姿態,(之後)飛行狀態機,寫電變,狀態燈.
// 為什麼獨立成工作:C3 只有一顆核心,內建網頁伺服器送一整頁時 Arduino loop 會停住
// 0.5 秒以上(參考專案實測). 飛行中控制迴圈絕不能被網頁拖住,放進優先權較高的工作,
// 網頁再忙也會被搶先. 其他工作只透過 controlGetTelemetry() 的快照讀資料.
// ============================================================================

struct Telemetry {
  float pitchDeg;         // 已加上角度修正,控制與顯示都用這個
  float rawPitchDeg;      // 晶片量到的原始值(安裝方位設定畫面用)
  float rollDeg;
  float accMagG;
  float gyroDps[3];
  float biasDps[3];
  bool still;
  float stillSeconds;
  bool imuPresent;
  bool imuFault;
  uint16_t escUs;
  uint16_t escDshot;      // DShot 時送出的值(0 或 48~2047);PWM 時 0xFFFF
  uint32_t loopCount;
  uint32_t maxExecUs;     // 單次控制迴圈最長執行時間
  uint32_t maxLateMs;     // 節拍最長延遲
  float impactPeakG;      // 最近一次短尖峰(觸地類衝擊)的峰值
  uint16_t impactMs;      // 它持續幾毫秒
  uint32_t impactAgeMs;   // 距今幾毫秒(從未發生為 UINT32_MAX)
  float vibG;             // Z 軸抖動強度(地面滑行判斷用)
  bool levelOk;           // 正飛水平(提早降落的姿態條件)
  float rollHoldS;        // 抖動條件已持續幾秒
  float pushG;            // 手勢推力(機頭方向,已扣重力)
  bool gestureLamp;       // 試推燈:最近 1.5 秒內推力達標
  float gesturePeakG;     // 最近一次達標的最大推力
  float pushPeak3sG;      // 3 秒內最大推力
  bool manualActive;      // 網頁手動輸出中
  uint8_t calibState;     // CalibState
  float calibRemainS;     // 校正最高油門還要保持幾秒
};

enum CalibState : uint8_t { CALIB_NONE = 0, CALIB_HOLD_MAX, CALIB_DONE };

// calibrate:這次開機要做電變校正(開機時已輸出最高油門,從 calibStartMs 起算保持秒數).
void controlBegin(bool imuPresent, bool calibrate = false, uint32_t calibStartMs = 0);
// 網頁手動輸出(Arduino loop 呼叫,網頁每 0.2 秒送一次當心跳). 超過 0.5 秒沒收到自動回最低油門並結束.
// 限制:只在待機/結束狀態,不在校正中;要從最低油門開始(防止滑桿停在高處時一解鎖就高轉速). 成功回 nullptr.
const char *controlManualWrite(uint16_t us);
void controlManualStop();
void controlGetTelemetry(Telemetry &out);
// 感測器是否在線. 序列埠的 mpu 指令重新初始化成功後呼叫.
bool controlImuPresent();
void controlSetImuPresent(bool present);
// 清除最長執行時間與最長延遲的紀錄(看某段操作有沒有拖慢控制迴圈時用).
void controlResetTimingStats();
// 目前能不能做 OTA 更新. 第 4 階段起:只有待機狀態可以(寫快閃期間控制迴圈會停住).
bool controlOtaAllowed();
// 設定是否鎖定. 第 4 階段起:手勢成立到回到待機之間鎖定.
bool controlSettingsLocked();
// 網頁「試收輪」:待機/結束時把輪子收起最多 10 秒(調限位行程用),離開待機或 up=false 立即放下. 成功回 nullptr.
const char *controlGearTest(bool up);
bool controlGearTesting();