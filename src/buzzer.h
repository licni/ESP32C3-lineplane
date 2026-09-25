// 版本流水號: r2 (2026-09-14) 電位由設定傳入(buzzerLow,網頁切換)
// 舊: r1 (2026-09-14) 初版(試做):開機就緒滴滴,等安全開關長音,倒數越近越急促,最後 3 秒連續長音到馬達啟動
#pragma once
#include <Arduino.h>
#include "flight.h"
// ============================================================================
// 蜂鳴器提示音(GG 2026-09-14). 在控制工作每拍依飛行狀態決定響或不響,腳位只在變化時寫.
//   開機就緒(電變解鎖完成,離開 FS_ARMING):滴滴兩聲
//   等安全開關按下:長音 0.5 秒,每 2.5 秒一次(響 0.5 + 停 2)
//   倒數:短音,剩越少間隔越短;最後 3 秒連續長音,一直響到馬達啟動
//   降落減力提醒(風格開啟時):忽高忽低跟著高油門響,逐漸減力響半秒停半秒
// mode = 有源高電位/有源低電位/無源 2kHz(設定沿用 buzzerLow);待機修改下一拍生效.
// ============================================================================

enum BuzzerMode : uint8_t { BUZZER_ACTIVE_HIGH = 0, BUZZER_ACTIVE_LOW = 1, BUZZER_PASSIVE = 2 };
bool buzzerBegin(uint8_t mode);   // 載入設定後先靜音,回傳硬體 PWM 是否就緒
void buzzerUpdate(uint32_t nowMs, const FlightStatus &f, uint8_t mode);
void buzzerDebug(char *out, size_t n);   // 序列指令 buzz:模式,PWM 是否掛上,duty 讀回,腳位實際電位
