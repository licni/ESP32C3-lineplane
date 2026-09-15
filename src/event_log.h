// 版本流水號: r7 (2026-09-14) EV_ARM_SWITCH arg 5:安全開關已停用(設定忽略安全開關),起飛程序不等開關
// 舊: r6 (2026-09-14) EV_ARM_SWITCH arg 3/4:等安全開關超過上限(取消起飛程序 / 不再自動倒數)
// 舊: r5 (2026-09-14) EV_ARM_SWITCH(28,安全開關:等開關按下才倒數,開關按下)
// 舊: r4 (2026-09-14) EV_CALIB_CLEAR(26,校正旗標自動取消),EV_WIFI_DEFER(27,飛行中 WiFi 試用退回延後)
// 舊: r3 (2026-09-14) 加 EV_WIFI 註解補齊,EV_FW(25,韌體更新:開始,完成,確認,退回,下載失敗)
// 舊: r2 (2026-09-13) 加 EV_SIM(測試用感測器模擬開關)
// 舊: r1 (2026-09-13) 初版:事件紀錄(通電後的重要事件與原因,記憶體環形緩衝,斷電清除)
#pragma once
#include <Arduino.h>
// ============================================================================
// 事件紀錄. GG:飛到一半忽然觸發降落,甚至馬達忽然停了,使用者要能查到原因與排查方向.
// 每筆:通電後毫秒,事件種類,兩個數值(G 力,秒數,原因代碼…). 文字在網頁端依種類組出來,韌體只存數字.
// 存在記憶體(128 筆環形),斷電或重開機才清除;開機第一筆記「這次為什麼開機」(上電/軟體重開/電壓不足/當機…),
// 飛行中馬達忽然停掉若其實是板子重開,看第一筆就知道.
// 任何工作都可以寫(內部上鎖,只複製 16 位元組).
// ============================================================================

enum EventType : uint8_t {
  EV_BOOT = 1,          // a = esp_reset_reason
  EV_ARMED,             // 電變解鎖完成. arg = 1 手勢開啟 / 0 上電自動倒數 / 2 自動倒數已用過 / 3 不是上電開機,不自動倒數
  EV_GESTURE,           // 啟動手勢成立. a = 推力 g
  EV_REJECT,            // 拒絕啟動. arg = RejectReason
  EV_COUNTDOWN,         // 開始倒數. a = 倒數秒數, arg = 1 延長後繼續 / 2 重新倒數 / 0 首次
  EV_DISTURB,           // 倒數中外力介入. a = 外力 g, b = 門檻, arg = DisturbAction
  EV_CANCEL,            // 取消倒數(網頁)
  EV_MOTOR_START,       // 馬達啟動. arg = 風格編號, a = 第一段油門 %, b = 起飛油門 %(0 = 不使用)
  EV_PHASE2,            // 換到第二段. a = 飛行秒數
  EV_LAND_START,        // 開始降落. arg = LandingCause, a = 飛行秒數, b = 觸地提早降落時抖動持續秒數
  EV_MOTOR_STOP,        // 馬達停止. arg = FlightEndReason, a = 主要數值(見網頁), b = 門檻或飛行秒數
  EV_IMU_FAULT,         // 感測器讀取失敗(飛行中角度補償暫停). arg = 當時是否馬達運轉
  EV_IMU_OK,            // 感測器恢復
  EV_MANUAL_START,      // 網頁手動輸出開始
  EV_MANUAL_END,        // 手動輸出結束. arg = 1 心跳逾時 / 0 上鎖或狀態改變
  EV_CALIB_START,       // 電變校正開始. a = 最高脈寬, b = 保持秒數
  EV_CALIB_DONE,        // 校正切到最低
  EV_LOOP_LATE,         // 控制迴圈延遲. a = 毫秒
  EV_SATURATED,         // 加速度或角速度超出量程(撞擊或劇烈震動). arg = 當時是否馬達運轉
  EV_TWIST_CANCEL,      // 扭轉機尾取消起飛. a = 扭轉角度, b = 門檻, arg = 封鎖手勢秒數
  EV_TILT_CANCEL,       // 起飛程序中角度超過水平限制取消. a = 機頭角度, b = 滾轉, arg = 限制角度
  EV_SIM,               // 測試用感測器模擬開啟/關閉(只有 USB 序列指令能開). arg = 1 開 / 0 關
  EV_GEAR,              // 機輪收腳. arg = 1 收起 / 0 放下, a = 飛行秒數
  EV_WIFI,              // WiFi 設定保護. arg = 1 連續開關電救援回出廠 / 2 設定沒確認已退回 / 3 發射功率沒確認已退回(a = 退回的 dBm)
  EV_FW,                // 韌體更新. arg 見 fw_update.h 的 FwEvent
  EV_CALIB_CLEAR,       // 電變校正旗標自動取消. arg = 1 設定後 10 秒沒拔電 / 2 軟體重開
  EV_WIFI_DEFER,        // 起飛程序或飛行中,WiFi 試用退回延後到落地. arg = 1 功率試用 / 2 設定試用
  EV_ARM_SWITCH,        // 安全開關(等按下才倒數). arg = 0 起飛程序已放穩,等開關 / 1 上電自動倒數等開關 / 2 開關按下 /
                        //   3 等開關超過上限,取消起飛程序 / 4 上電自動倒數等開關超過上限,不再自動倒數. a = 上限秒數 /
                        //   5 安全開關已停用(設定忽略),起飛程序不等開關 / 6 上電自動倒數等待中改成手勢啟動,自動倒數作廢

};

struct EventRecord {
  uint32_t ms;
  uint8_t type;
  uint8_t arg;
  uint16_t reserved;
  float a;
  float b;
};

const uint16_t EVENT_LOG_CAPACITY = 128;

void eventLog(EventType type, uint8_t arg = 0, float a = 0, float b = 0);
// 目前總共記過幾筆(含已被覆蓋的). 網頁看這個數字變了才來抓.
uint32_t eventLogTotal();
// 取第 seq 筆(0 起算). 已被覆蓋或還沒發生回 false.
bool eventLogGet(uint32_t seq, EventRecord &out);
uint32_t eventLogOldest();
