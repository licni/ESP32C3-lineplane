// 版本流水號: r5 (2026-10-30) 只記起飛程序(GG:插著電聊天不要記一堆沒用的):進入倒數開始記,馬達停後 5 秒停;旗標 0x10 標每趟第一筆
// 舊: r4 (2026-10-30) 改存快閃(GG:斷電保留):閒置的 spiffs 分割區 128KB 當環形紀錄,約 19 分鐘;控制工作只推進 RAM 佇列,
//   Arduino loop 寫快閃;倒數時先擦好這趟要用的區塊,飛行中只寫頁(停 1ms),不擦(停 30~50ms 會漏姿態). 網頁讀取靠 mmap,格式不變
// 舊: r3 (2026-10-29) 每筆加翼軸仰角 sideDeg(0~90)與方位角 azim(0~255 = 0~360°);一筆 11 位元組,3D 半球軌跡用
// 舊: r2 (2026-10-29) 每筆加線軸 G(0.1g 單位,區間最後的低通值);一筆 9 位元組,網頁依 /api/log 標頭的每筆大小解碼
// 舊: r1 (2026-09-13) 初版:0.1 秒一筆的環形紀錄(角度,油門,G 力,Z 抖動,短尖峰,手勢推力,狀態)
#pragma once
#include <Arduino.h>
// ============================================================================
// 飛行紀錄. 控制工作每個節拍餵資料,每 100ms 收成一筆(區間內取最大值,短尖峰不會漏掉).
// 只記起飛程序(r5,GG:飛場插著電聊天不要記一堆沒用的):從進入倒數開始(倒數那幾秒是地面 1g 的參考),到馬達停止(或取消)後 5 秒停,
// 待機與等待安全開關都不記,快閃也不磨耗. 每趟第一筆旗標加 LOG_FLAG_REC_START,網頁用它畫分趟線(相鄰兩趟在圖上緊接著).
// 存在快閃的 spiffs 分割區(分割表 min_spiffs 給了 128KB,韌體沒用它當檔案系統),斷電保留,寫滿自動覆蓋最舊的;
// 韌體更新不動這塊. 約 19.8 分鐘,夠放兩趟 8 分鐘的飛行. 為什麼記在板子上:飛行中手機在飛手口袋裡,不可能即時接收.
//
// 快閃版面:32 個 4KB 區塊,每塊 8 位元組標頭(magic,序號,每筆大小)+ 371 筆. 序號遞增,開機掃標頭找最新的區塊接著寫.
// 全域編號 = 序號 × 371 + 區塊內位置,網頁的增量讀取不用改. 讀取用 mmap(記憶體映射,走快取,不停機).
// 寫入時機:控制工作只把收成的一筆推進 RAM 佇列(不碰快閃);loop 每秒把佇列寫進快閃(寫一頁約停 1ms).
// 擦除區塊會讓整顆晶片停 30~50ms(控制工作漏 6~10 拍姿態),所以進入倒數時先把這趟要用的區塊擦好(flightLogRequestPrepare),
// 飛行中只在擦好的區塊裡寫;真的寫到沒擦的區塊才就地擦(飛太久才會遇到).
// ============================================================================

const uint16_t FLIGHT_LOG_SAMPLE_MS = 100;

// 旗標位元
const uint8_t LOG_FLAG_LEVEL = 0x01;          // 正飛水平(提早降落的姿態條件)
const uint8_t LOG_FLAG_ROLL_HOLD = 0x02;      // 地面滑行抖動已持續到門檻秒數
const uint8_t LOG_FLAG_IMU_FAULT = 0x04;
const uint8_t LOG_FLAG_GESTURE = 0x08;        // 手勢推力達標
const uint8_t LOG_FLAG_REC_START = 0x10;      // 這趟紀錄的第一筆(r5:進入倒數開始記)

struct __attribute__((packed)) FlightLogSample {
  int8_t pitchDeg;      // 機頭角度(已含角度修正)
  uint8_t throttlePct;  // 電變輸出換算的油門 %
  uint8_t accMaxDg;     // 區間內 |a| 最大值,單位 0.1g
  uint8_t vibCg2;       // 區間內 Z 抖動最大值,單位 0.02g
  uint8_t spikeDg;      // 區間內結束的短尖峰最大峰值,單位 0.1g(0 = 沒有)
  int8_t pushDg;        // 區間內手勢推力(機頭方向)最大值,單位 0.1g
  uint8_t state;        // 飛行狀態(第 4 階段)
  uint8_t flags;
  uint8_t lineDg;       // 線軸 G(低通後)區間最後的值,單位 0.1g(r2 加在尾端,舊網頁照每筆大小跳過)
  uint8_t sideDeg;      // 翼軸仰角 0~90(r3):半球上的高度角
  uint8_t azim;         // 方位角 0~255 = 0~360°(r3):半球上繞飛手的角度,馬達啟動時歸零
};

// 開機呼叫(控制工作啟動前):找分割區,mmap,掃標頭接續上次的位置. 找不到分割區就只用 RAM 佇列(網頁看不到紀錄).
void flightLogBegin();
// Arduino loop 每圈呼叫:把佇列寫進快閃,處理擦除請求.
void flightLogService(uint32_t nowMs);
// 進入倒數時呼叫(控制工作):請 loop 把接下來 samples 筆要用的區塊先擦好.
void flightLogRequestPrepare(uint32_t samples);
// 控制工作呼叫. 各值取區間最大,時間到自動收成一筆. 只在起飛程序中(倒數~馬達停後 5 秒)才收;其他時候呼叫沒有作用.
void flightLogFeed(float pitchDeg, float throttlePct, float accMagG, float vibG, float spikeG, float pushG,
                   float lineG, float sideDeg, float azimuthDeg, uint8_t state, uint8_t flags, uint32_t nowMs);
// 已寫進快閃的總筆數(單調遞增,讀取端拿來做增量更新). 佇列裡還沒寫的不算.
uint32_t flightLogTotal();
// 取第 index 筆(以總筆數編號). 不在保留範圍內回 false.
bool flightLogGet(uint32_t index, FlightLogSample &out);
// 保留範圍內最舊的一筆編號.
uint32_t flightLogOldest();
// 診斷:快閃可用,區塊數,目前區塊序號,佇列溢出丟掉的筆數,飛行中就地擦除次數.
void flightLogStats(bool &flashOk, uint16_t &sectors, uint32_t &seq, uint32_t &dropped, uint32_t &inflightErases);
