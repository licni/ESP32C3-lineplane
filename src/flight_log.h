// 版本流水號: r1 (2026-09-13) 初版:0.1 秒一筆的環形紀錄(角度,油門,G 力,Z 抖動,短尖峰,手勢推力,狀態)
#pragma once
#include <Arduino.h>
// ============================================================================
// 飛行紀錄. 控制工作每個節拍餵資料,每 100ms 收成一筆(區間內取最大值,短尖峰不會漏掉).
// 一直在記(不分飛行或地面),保留最近 10 分鐘,重新通電清除.
// 為什麼記在板子上:飛行中手機在飛手口袋裡,不可能即時接收. 降落後再打開紀錄頁看.
// 用途(GG 第三輪回饋):先關掉提早降落飛幾個特技,看特技的最高 G 力與地面滑行的抖動各是多少,再訂門檻.
//
// 記憶體:一筆 8 位元組 × 6000 筆 = 48KB,開機時靜態配置,不碎片化.
// 讀取端(網頁)不上鎖直接讀:寫入是「先寫資料再推進計數」,讀到的一定是完整的舊資料;
// 唯一的風險是環形覆寫時最舊那一筆被改寫,讀取端丟掉最舊一筆即可.
// ============================================================================

const uint16_t FLIGHT_LOG_SAMPLE_MS = 100;
const uint16_t FLIGHT_LOG_CAPACITY = 6000;   // 10 分鐘

// 旗標位元
const uint8_t LOG_FLAG_LEVEL = 0x01;          // 正飛水平(提早降落的姿態條件)
const uint8_t LOG_FLAG_ROLL_HOLD = 0x02;      // 地面滑行抖動已持續到門檻秒數
const uint8_t LOG_FLAG_IMU_FAULT = 0x04;
const uint8_t LOG_FLAG_GESTURE = 0x08;        // 手勢推力達標

struct __attribute__((packed)) FlightLogSample {
  int8_t pitchDeg;      // 機頭角度(已含角度修正)
  uint8_t throttlePct;  // 電變輸出換算的油門 %
  uint8_t accMaxDg;     // 區間內 |a| 最大值,單位 0.1g
  uint8_t vibCg2;       // 區間內 Z 抖動最大值,單位 0.02g
  uint8_t spikeDg;      // 區間內結束的短尖峰最大峰值,單位 0.1g(0 = 沒有)
  int8_t pushDg;        // 區間內手勢推力(機頭方向)最大值,單位 0.1g
  uint8_t state;        // 飛行狀態(第 4 階段)
  uint8_t flags;
};

// 控制工作呼叫. 各值取區間最大,時間到自動收成一筆.
void flightLogFeed(float pitchDeg, float throttlePct, float accMagG, float vibG, float spikeG, float pushG,
                   uint8_t state, uint8_t flags, uint32_t nowMs);
// 已寫入的總筆數(單調遞增,讀取端拿來做增量更新).
uint32_t flightLogTotal();
// 取第 index 筆(以總筆數編號). 不在保留範圍內回 false.
bool flightLogGet(uint32_t index, FlightLogSample &out);
// 保留範圍內最舊的一筆編號.
uint32_t flightLogOldest();
