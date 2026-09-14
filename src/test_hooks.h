// 版本流水號: r2 (2026-09-14) 安全開關覆寫(armsw),sim pulse 延遲參數
// 舊: r1 (2026-09-13) 初版:感測器模擬注入,GPIO5 脈寬量測,狀態燈腳位取樣(全功能測試用)
#pragma once
#include <Arduino.h>
#include "imu.h"
// ============================================================================
// 桌上測試用掛勾. GG 2026-09-13 要求測試全部功能(觸地,撞擊,手勢,外力,扭轉,傾斜,抖動…),
// 板子放在桌上做不出這些動作,所以讓控制工作可以吃「模擬的感測器讀值」,整條判斷鏈照真的跑.
//
// 安全:只有 USB 序列指令能開啟(飛行時沒接 USB 不可能誤開),存在記憶體,重開機即清除;
// 開關都記進事件紀錄,狀態 API 有 sim 欄位.
//
// 模擬讀值是機身座標(已套安裝方位,已扣陀螺儀零點),直接取代 imuRead 的結果;
// 真的感測器照常讀取(I2C 時序與靜止窗不變).
// ============================================================================

// 序列指令 sim ... 的處理(Arduino loop 呼叫). 回覆文字寫進 reply.
//   sim att <機頭°> <滾轉°> [大小g]  靜止姿態(重力方向),姿態濾波立即重新定姿
//   sim attq <機頭°> <滾轉°> [大小g] 同上但不重新定姿(讓濾波自己收斂)
//   sim acc <x> <y> <z>              直接給加速度(g)
//   sim gyro <x> <y> <z>             角速度(°/秒)
//   sim vib <振幅g> [頻率Hz]          Z 軸正弦抖動(0 = 關)
//   sim pulse <x|y|z> <g> <毫秒>      一次性加在某軸的脈衝(推手勢,觸地,撞擊)
//   sim fail <0|1>                   模擬 I2C 讀取失敗
//   sim off                          關閉模擬,回到真的感測器
void testSimCommand(const char *args, char *reply, size_t replySize);
// 控制工作每拍在 imuRead 之後呼叫. 模擬中覆寫 reading 與 readOk.
void testSimApply(ImuReading &reading, bool &readOk, uint32_t nowMs);
bool testSimActive();

// 安全開關覆寫(序列指令 armsw 0|1|off):開發板沒接 GPIO21 的微動開關,測試時用這個假裝按下.
// -1 = 不覆寫(讀真的腳位),0 = 當作沒按,1 = 當作按下. 只存記憶體,重開即清除.
// 覆寫值存 RTC 記憶體:軟體重開保留(測試中途重開不用重送),拔電再接電清掉. setup() 呼叫 testArmOverrideBoot() 讀回.
void testArmOverrideBoot();
void testArmOverrideSet(int8_t v);
int8_t testArmOverride();

// GPIO5 脈寬量測(GPIO5 跳線接 GPIO4,只在 PWM 協定用;與 escemu 不可同時)
struct PwmCapStats {
  bool active;
  uint32_t pulses;       // 量到的完整脈衝數
  uint32_t highUs;       // 最近 16 個高電位寬度的中位數
  uint32_t periodUs;     // 最近 16 個週期的中位數
  uint32_t minHighUs;    // 上次 reset 後的最小/最大高電位寬度
  uint32_t maxHighUs;
  uint32_t edgeAgeMs;    // 最後一個邊緣距今(沒有訊號時會變大)
};
const char *testPwmCapStart();
const char *testPwmCapStartPin(uint8_t pin);   // 量輸出腳自己的電位(GPIO3 收輪舵機)
void testPwmCapStop();
void testPwmCapResetMinMax();
void testPwmCapGet(PwmCapStats &out);

// 狀態燈腳位取樣:ledcap 開始取樣 ms 毫秒(讀 GPIO8 腳位實際電位),結果是亮/滅的連續段長度
void testLedCaptureStart(uint32_t durationMs);
void testLedSample(uint32_t nowMs);           // 控制工作每拍呼叫
void testLedCaptureReport(char *out, size_t outSize);

#if defined(LP_TEST_HOOKS_OFF) && !defined(LP_TEST_HOOKS_IMPL)
// A/B 對照用:編譯時加 -DLP_TEST_HOOKS_OFF,控制工作與狀態 API 每拍/每次呼叫的掛勾變成空的
#define testSimApply(r, ok, now) ((void)0)
#define testLedSample(now) ((void)0)
#define testPwmCapGet(o) ((void)memset(&(o), 0, sizeof(o)))
#endif
