// 版本流水號: r1 (2026-09-13) 初版:機輪收腳舵機(GPIO3,50Hz,限位行程,反轉,速度)
#pragma once
#include <Arduino.h>
#include "settings.h"
// ============================================================================
// 機輪收腳舵機(GG 2026-09-13 追加). 只允許控制工作呼叫 gearUpdate().
// 什麼時候收/放由飛行狀態機決定(flight.cpp:馬達啟動 N 秒後收,降落減力一開始放,馬達停就放,
// 觸地提早降落開啟時永遠放著). 這裡只管把舵機以設定的速度移到目標位置.
//
// 開機一律從「放下」開始輸出;關閉收輪功能時也持續輸出放下位置(裝了收腳的飛機輪子保持放下).
// 位置用 0(放下)~1(收起)表示,每拍依行程與反轉換算脈寬,待機時改行程設定舵機會立刻跟著動(方便調限位).
// ============================================================================

const uint16_t GEAR_PWM_HZ = 50;    // 一般舵機

void gearBegin(const SharedSettings &cfg);
// 控制工作每拍呼叫. wantUp = 目標收起.
void gearUpdate(bool wantUp, const SharedSettings &cfg, float dt);
float gearPosition();       // 0 = 放下,1 = 收起
uint16_t gearCurrentUs();
