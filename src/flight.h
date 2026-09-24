// 版本流水號: r15 (2026-09-24) 強制停機結束原因 END_FORCE_SWITCH(長按安全開關)/ END_FORCE_WAG(搖擺機尾);狀態加 landPulse,landBuzz
// 舊: r14 (2026-09-15) 輸入加 escFail(電變輸出掛載失敗),拒絕原因 10 REJECT_ESC_OUTPUT
// 舊: r13 (2026-09-15) 狀態加 takeoffBoost(起飛油門階段)
// 舊: r12 (2026-09-14) 安全開關等待上限(GG):超過設定分鐘數沒按就取消(END_ARM_TIMEOUT);輸入加測試覆寫秒數,狀態加剩餘秒數
// 舊: r11 (2026-09-14) 安全開關改成「起飛程序照常開始,按下才倒數」(GG);狀態加 armLatched
// 舊: r10 (2026-09-14) 拒絕原因 9:撞擊斷電後推飛機不算手勢
// 舊: r9 (2026-09-14) 安全開關輸入 armSwitch,拒絕原因 7/8,狀態回報開關
// 舊: r8 (2026-09-14) 輸入加 fwBlock:韌體更新中或新韌體待確認時拒絕起飛(REJECT_FW_UPDATING / REJECT_FW_UNCONFIRMED)
// 舊: r7 (2026-09-14) 手勢請求加來源(網頁開始起飛按鈕)
// 舊: r6 (2026-09-13) 輸出加 gearUp(機輪收腳)
// 舊: r5 (2026-09-13) 等待放穩/倒數中角度超過水平限制 → 取消(END_TILT_CANCEL)
// 舊: r4 (2026-09-13) 起飛前水平限制:角度超過時手勢被拒(REJECT_TILT),上電自動倒數暫停等放平(REJECT_TILT_WAIT)
// 舊: r3 (2026-09-13) 扭轉機尾取消手勢起飛(END_TWIST_CANCEL,狀態加扭轉角度與手勢封鎖剩餘秒數)
// 舊: r2 (2026-09-13) 輸入加 escService(校正/手動輸出中不啟動,解鎖時間從校正結束算)
// 舊: r1 (2026-09-13) 初版:飛行狀態機(解鎖,待機,手勢,放穩,倒數,外力,起飛,換段,補償,降落,觸地,撞擊,緊急停止,燈號)
#pragma once
#include <Arduino.h>
#include "settings.h"
// ============================================================================
// 飛行狀態機. 只在控制工作裡跑(200Hz). 網頁與序列埠只能透過 request* 函式送請求,
// 由控制工作在下一拍處理 —— 狀態只有一個工作在改,不會有兩邊同時改的問題.
//
// 流程(規格第 3 節):
//   上電 → 電變解鎖(3 秒) ─┬ 手勢開啟 → 待機 ─(啟動手勢)→ 等待放穩 ─(安全開關按過)→ 倒數 → 起飛 → 飛行 → 降落 → 結束
//                          └ 手勢關閉 → 待機等安全開關按下與放平 → 直接倒數(每次上電只一次)
//   安全開關(GG 2026-09-14 r11):不擋起飛程序開始,等按下才倒數. 起飛程序中按下一次就記住(開始當下按著也算).
//   等待上限(r12,設定 armWaitMin 分鐘):起飛程序開始(上電自動倒數是解鎖完)後超過上限還沒按 → 取消回待機;
//   上電自動倒數取消後這次通電不再自動倒數. 按過開關之後不再計時(等放穩或等放平不受上限影響).
//   倒數中外力介入 → 退回等待放穩,再放穩後依設定延長/重置/不理會(不必再按開關).
//   結束後(手勢開啟時)可再做手勢起飛;手勢關閉時要重新上電.
//
// 設定:手勢成立(或自動倒數開始)那一刻複製共用設定與飛行風格,之後整趟飛行只用這份快照,
// 飛行中網頁怎麼改都不影響. 有未儲存變更時拒絕啟動.
// ============================================================================

enum FlightState : uint8_t {
  FS_ARMING = 0,    // 上電後電變解鎖中
  FS_STANDBY,       // 待機(等手勢;手勢關閉時是「已自動啟動過,重新上電才會再倒數」)
  FS_WAIT_STILL,    // 等飛機放穩
  FS_COUNTDOWN,     // 倒數
  FS_TAKEOFF,       // 緩啟動加力
  FS_FLYING,        // 飛行(第一段/換段/第二段)
  FS_LANDING,       // 降落程序
  FS_DONE,          // 結束(馬達停)
};

enum FlightEndReason : uint8_t {
  END_NONE = 0,
  END_TOUCH_SPIKE,     // 降落中觸地衝擊
  END_TOUCH_STILL,     // 降落中完全靜止
  END_TOUCH_ROLL,      // 降落中地面滑行抖動
  END_LANDING_TIMEOUT, // 降落保險時間到
  END_CRASH,           // 撞擊斷電
  END_ESTOP,           // 網頁緊急停止
  END_CANCELED,        // 倒數中取消
  END_TWIST_CANCEL,    // 手勢起飛後扭轉機尾取消
  END_TILT_CANCEL,     // 起飛程序中(等待放穩/倒數)角度超過起飛前水平限制,取消
  END_ARM_TIMEOUT,     // 等安全開關超過等待上限,取消(上電自動倒數的等待逾時也用這個)
  END_FORCE_SWITCH,    // 馬達運轉中長按安全開關 2 秒,強制停機
  END_FORCE_WAG,       // 馬達運轉中左右搖擺機尾 3 個來回,強制停機
};

enum LandingCause : uint8_t { LAND_NONE = 0, LAND_TIME, LAND_EARLY_ROLL };
// REJECT_TILT:推了啟動手勢但機身角度超過起飛前水平限制;REJECT_TILT_WAIT:上電自動倒數因角度超過而暫停等待
// REJECT_FW_UPDATING:韌體更新進行中;REJECT_FW_UNCONFIRMED:剛更新的新韌體還沒在網頁確認(沒確認會自動退回舊版,
// 飛行中退回重開等於馬達停,所以確認前不准起飛)
// REJECT_ARM_SWITCH / REJECT_ARM_WAIT:r10 以前安全開關沒按下就拒絕開始. r11 起改成等開關按下才倒數,不再產生(保留編號)
// REJECT_CRASH_LOCK:撞擊斷電後推飛機不算手勢(撿飛機,扶正時容易推到),要網頁開始起飛程序或重新上電
enum RejectReason : uint8_t { REJECT_NONE = 0, REJECT_UNSAVED, REJECT_IMU, REJECT_TILT, REJECT_TILT_WAIT, REJECT_FW_UPDATING, REJECT_FW_UNCONFIRMED,
                              REJECT_ARM_SWITCH, REJECT_ARM_WAIT, REJECT_CRASH_LOCK,
                              REJECT_ESC_OUTPUT };   // 10:電變輸出掛載失敗(開機 LEDC/RMT 建立失敗,腳位沒訊號)
enum DisturbAction : uint8_t { DISTURB_ACT_NONE = 0, DISTURB_ACT_EXTEND, DISTURB_ACT_RESET };

struct FlightInputs {
  bool imuOk;
  float pitchDeg;        // 已含角度修正
  float rollDeg;
  float accG[3];         // 機身座標
  float accMagG;
  float gyroDps[3];
  float pushG;           // 機頭方向推力(已扣重力)
  bool gestureLevel;     // 手勢的「機身大致水平」
  float spikeG;          // 這一拍結束的短尖峰峰值(0 = 沒有)
  float rollHoldS;       // 地面滑行抖動已持續秒數
  bool escService;       // 電變校正或網頁手動輸出進行中:不接受啟動,並用掉「上電自動倒數」
  uint8_t fwBlock;       // 0 = 可起飛,1 = 韌體更新中,2 = 新韌體待確認(見 fw_update.h)
  bool escFail;          // 電變輸出掛載失敗(escOutputOk() == false):拒絕起飛
  bool armSwitch;        // 安全開關已按下(GPIO21 低電位持續 50ms,控制迴圈去抖)
  uint16_t armWaitTestS; // 測試用:安全開關等待上限改成這麼多秒(序列指令 armwait;0 = 用設定的分鐘數)
  uint32_t nowMs;
};

struct FlightOutputs {
  bool motorOn;          // false 時輸出油門 0%
  float throttlePct;
  float speedMps;        // 姿態向心力補償用的飛行速度
  bool inFlight;         // 姿態濾波用飛行增益,停止學陀螺儀零點
  bool gearUp;           // 機輪收起(馬達啟動 N 秒後;降落,停止,待機一律放下)
};

struct FlightStatus {
  FlightState state;
  float stateSeconds;
  float countdownRemainS;
  float flightSeconds;       // 從馬達啟動算
  float basePct;
  float compPct;
  float outPct;
  uint8_t phase;             // 1 = 第一段,2 = 第二段(換段過渡中也算 2)
  bool takeoffBoost;         // 在起飛油門階段(維持中或換回第一段的過渡中)
  LandingCause landingCause;
  FlightEndReason endReason;
  RejectReason rejectReason;
  uint32_t rejectAgeMs;      // 拒絕發生距今(UINT32_MAX = 從未)
  DisturbAction disturbAction;
  float disturbG;
  uint32_t disturbAgeMs;
  bool gestureEnabled;
  bool autoStartUsed;
  uint8_t flightProfile;     // 這趟飛行用的風格編號
  float settleSeconds;       // 已放穩幾秒
  float distG;               // 目前外力(加速度相對放穩參考的變化,g)
  float distPeakG;           // 3 秒內最大外力
  uint32_t distOverAgeMs;    // 外力超過門檻距今(UINT32_MAX = 從未)
  float twistDeg;            // 手勢起飛後機尾已扭轉的角度(繞機背軸,取消起飛用)
  float gestureBlockS;       // 扭轉取消後還要幾秒才接受手勢
  bool autoWaitLevel;        // 上電自動倒數在等飛機放平(角度超過起飛前水平限制)或等安全開關按下
  bool armSwitch;            // 安全開關目前是否按下(網頁顯示用)
  bool armLatched;           // 這趟起飛程序(等待放穩/倒數,或上電自動倒數等待中)已經按過安全開關
  float armWaitLeftS;        // 等安全開關還剩幾秒就自動取消(-1 = 不在等安全開關)
  bool landPulse;            // 降落中忽高忽低提醒進行中
  bool landBuzz;             // 這一拍蜂鳴器要響(降落提醒)
};

void flightBegin();
// 每拍呼叫. 回傳這一拍的輸出.
FlightOutputs flightUpdate(const FlightInputs &in, float dt);
void flightGetStatus(FlightStatus &out);
uint8_t flightLedPattern(uint32_t nowMs, bool imuFault);   // 回傳 LED 應亮(1)或滅(0)

// 其他工作送來的請求(下一拍處理)
void flightRequestCancel();        // 等待放穩/倒數中 → 待機
void flightRequestEstop();         // 馬達運轉中 → 立即停
// 啟動手勢的來源(事件紀錄用)
enum GestureSource : uint8_t { GESTURE_SRC_PUSH = 0, GESTURE_SRC_SERIAL = 1, GESTURE_SRC_WEB = 2 };
// 不推飛機也當作做了一次啟動手勢:序列埠測試,或網頁「開始起飛程序」按鈕(GG 2026-09-14:不用去踢飛機).
// 與真的推飛機走同一套檢查:手勢要開啟,待機/結束狀態,未儲存變更,感測器,起飛前水平限制,扭轉取消封鎖期.
void flightRequestGesture(uint8_t source = GESTURE_SRC_SERIAL);
void flightRequestDisturb();       // 序列埠模擬倒數中外力介入(測試用)
void flightRequestTwist();         // 序列埠模擬扭轉機尾取消起飛(測試用)
void flightRequestTilt();          // 序列埠模擬起飛程序中角度超過水平限制(測試用)

// 待機時是目前的共用設定,手勢成立後是這趟飛行的快照. 控制工作的門檻判斷一律用這份.
const SharedSettings &flightShared();

bool flightSettingsLocked();       // 手勢成立到結束之間
bool flightOtaAllowed();           // 解鎖,待機,結束
