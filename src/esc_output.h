// 版本流水號: r6 (2026-09-13) DShot300 雙向轉速回傳(單腳)與解碼自我測試
// 舊: r5 (2026-09-13) DShot 改 150/300(GG:不需要 600)
// 舊: r4 (2026-09-13) PWM 頻率可調(50~400Hz,開機套用)
// 舊: r3 (2026-09-13) 加 DShot300/600(RMT 硬體連續重送 4kHz),開機依設定協定初始化,回授自我檢查
// 舊: r2 (2026-09-13) escBegin 可指定初始脈寬(電變校正開機直接輸出最高油門)
// 舊: r1 (2026-09-13) 初版:LEDC 50Hz 14bit 脈寬輸出
#pragma once
#include <Arduino.h>
// ============================================================================
// 電變輸出:PWM 50~400Hz(LEDC)或 DShot150/300(RMT).
// 只允許控制工作(control task)呼叫寫入函式,避免兩個工作搶著改輸出.
//
// 協定只在開機時決定:電變通常在上電後第一次看到訊號時判斷訊號種類,之後要重新上電才能換
// (BLHeli_32 手冊). 所以開機先把腳位拉低,讀完設定才掛上正確的協定,不先送 PWM 再切 DShot.
//
// DShot 送出頻率:BLHeli_32 手冊寫 48MHz 的電變 MCU 收 DShot 最低約 1kHz,MCU 越快下限越高;
// 控制迴圈只有 200Hz,所以用 RMT 硬體迴圈模式連續重送最新的訊框(每 250µs 一框 = 4kHz),
// 控制工作只在數值改變時換訊框. 查證紀錄:docs/電變校正說明查證_2026-09-13.md 批次 4.
// ============================================================================

const uint16_t ESC_PWM_FREQ_HZ = 50;          // 預設;共用設定 escPwmHz 可改 50~400Hz
const uint8_t ESC_PWM_RESOLUTION_BITS = 14;   // C3 的 LEDC 上限,一格 20000/16384 = 1.22µs
const uint16_t ESC_US_ABSOLUTE_MIN = 800;     // 絕對保護範圍,任何設定都不能超出
const uint16_t ESC_US_ABSOLUTE_MAX = 2200;
const uint16_t ESC_US_SAFE_IDLE = 1000;       // 開機與故障時輸出的值

const uint16_t DSHOT_STOP = 0;                // DShot 指令 0 = 停止(解鎖前要持續送)
const uint16_t DSHOT_THROTTLE_MIN = 48;       // 48~2047 = 油門 0~100%
const uint16_t DSHOT_THROTTLE_MAX = 2047;
const uint32_t DSHOT_FRAME_PERIOD_US = 250;   // 4kHz

// 開機最先呼叫:腳位定成低電位輸出(還沒決定協定前不留浮空).
void escPinLow();
// 依協定(settings.h 的 EscProtocol)掛上輸出. PWM 輸出 initialUs;DShot 輸出停止指令.
// rpmTelemetry:雙向 DShot 轉速回傳(只在 DShot300 生效).
bool escBegin(uint8_t protocol, uint16_t initialUs = ESC_US_SAFE_IDLE, uint16_t pwmHz = ESC_PWM_FREQ_HZ,
              bool rpmTelemetry = false);
// 控制工作每拍呼叫. us = PWM 脈寬;pct = 油門百分比(DShot 用);stop = 馬達停止(DShot 送 0).
void escWrite(uint16_t us, float pct, bool stop);
// 目前輸出:PWM 的脈寬(µs);DShot 時是換算回等效脈寬,顯示用.
uint16_t escCurrentUs();
// DShot 時目前送出的值(0 或 48~2047);PWM 時 0xFFFF.
uint16_t escCurrentDshot();
uint8_t escActiveProtocol();
uint16_t escActivePwmHz();

// 雙向 DShot 轉速回傳統計(累計值;網頁用兩次讀取的差算失敗率)
struct EscRpmStats {
  uint32_t frames;     // 送出訊框數
  uint32_t replies;    // 收到回傳(接收完成)次數
  uint32_t ok;         // 解碼成功
  uint32_t bad;        // 收到但解碼失敗(GCR 無效或 CRC 錯)
  uint32_t noReply;    // 下一框前沒收到回傳
  uint32_t periodUs;   // 最近一次成功的電氣週期 µs(0xFFFF = 馬達停止)
  uint32_t lastOkMs;   // 最近一次成功的時刻(開機後毫秒)
};
bool escRpmActive();
void escRpmGetStats(EscRpmStats &out);
// 解碼自我測試:暫停送訊框,送一段合成的電變回傳波形給自己收,比對解出的週期. 只在轉速回傳啟用時可用.
bool escRpmSelfTest(uint32_t periodUs, char *out, size_t outSize);

// 模擬電變(測試用,GPIO5 跳線接 GPIO4;只由序列指令 escemu 啟動). 對每個收到的訊框回傳指定週期(0xFFFF = 停止).
struct EscEmuStats {
  uint32_t frames;       // GPIO5 收到的控制器訊框
  uint32_t frameCrcOk;   // 其中反相 CRC 正確的
  uint32_t replies;      // 送出的回傳
  uint32_t lastValue;    // 最近一框的油門值(0 或 48~2047)
  uint32_t periodUs;
};
const char *escEmuStart(uint32_t periodUs);
void escEmuStop();
void escEmuGetStats(EscEmuStats &out);
// DShot 回授自我檢查:用 RMT 接收同一腳位的訊號,解一個訊框回報. 只在 DShot 且馬達停止時用.
// out 放可讀的結果文字. 成功(收到 CRC 正確且值相符的訊框)回 true.
bool escDshotSelfTest(char *out, size_t outSize);
