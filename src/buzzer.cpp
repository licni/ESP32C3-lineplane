// 版本流水號: r6 (2026-10-07) 取消確認改兩短音,每聲 150ms,比按住時的 50ms 長
// 舊: r5 (2026-10-07) 安全開關成功取消後兩長音,同次按壓不再急響
// 舊: r4 (2026-10-07) 安全開關按住時響 50ms/停 50ms,優先於所有狀態提示
// 舊: r3 (2026-09-24) 降落提醒:飛行狀態 landBuzz 為真時響(忽高忽低跟著高油門,逐漸減力響半秒停半秒)
// 舊: r2 (2026-09-14) 電位改用設定 buzzerLow(網頁切換,立即生效);滴聲 80 → 150ms;倒數短音 60 → 120ms,間隔改 剩餘×0.06(0.2~1.2 秒)(GG:太短,不夠急促)
// 舊: r1 (2026-09-14) 初版(試做):開機就緒滴滴,等安全開關長音,倒數越近越急促,最後 3 秒連續長音到馬達啟動
#include "buzzer.h"
#include "pins_config.h"
#include "driver/gpio.h"

static const uint16_t READY_BEEP_MS = 150;     // 滴滴:響 150 停 150 響 150
static const uint16_t READY_GAP_MS = 150;
static const uint16_t ARM_WAIT_ON_MS = 500;    // 等安全開關:長音 0.5 秒
static const uint16_t ARM_WAIT_PERIOD_MS = 2500;   // 響 0.5 + 停 2
static const uint16_t COUNT_BEEP_MS = 120;     // 倒數短音
static const uint16_t SWITCH_BEEP_MS = 50;    // 按住安全開關:每秒 10 聲
static const uint16_t SWITCH_PERIOD_MS = 100;
static const uint16_t CANCEL_LEAD_MS = 100;   // 先短暫靜音,與急促提示分開
static const uint16_t CANCEL_BEEP_MS = 150;   // 取消成功:兩短音,每聲是急響的 3 倍長
static const uint16_t CANCEL_GAP_MS = 150;
static const float COUNT_FINAL_S = 3.0f;       // 最後幾秒改連續長音
// 倒數短音的間隔 = 剩餘秒數 × 0.06,限制在 0.2~1.2 秒:剩 20 秒 1.2 秒一聲,10 秒 0.6 秒,5 秒 0.3 秒,3 秒前 0.2 秒
static const float COUNT_INTERVAL_PER_S = 0.06f;
static const float COUNT_INTERVAL_MIN_S = 0.2f;
static const float COUNT_INTERVAL_MAX_S = 1.2f;

// 固定頻率與解析度,核心會配獨立計時器,不與電變/舵機的 14 bit PWM 共用.
// 開機一次掛好,控制工作只改 duty,不配置硬體也不忙等產生聲波.
static const uint16_t BUZZER_HZ = 2000;
static const uint8_t BUZZER_BITS = 8;
static const uint32_t BUZZER_HIGH = 255;   // ledcWrite 將最大值轉成持續高電位
static uint8_t outputMode = 0;
static bool attached = false;
static bool outOn = false;
static bool readyDone = false;
static uint32_t readyStartMs = 0;
static FlightState lastState = FS_ARMING;
static bool armWaitWas = false;
static uint32_t armWaitStartMs = 0;
static uint32_t nextCountBeepMs = 0;
static uint32_t countBeepEndMs = 0;
static bool switchWasPressed = false;
static uint32_t switchPressMs = 0;
static bool cancelWasHeld = false;
static bool cancelToneActive = false;
static uint32_t cancelToneStartMs = 0;

static void writeOut(bool on, uint8_t mode) {
  if (on == outOn && mode == outputMode) return;
  outOn = on;
  outputMode = mode;
  const uint32_t duty = mode == BUZZER_PASSIVE ? (on ? 128 : 0)
                                              : (on != (mode == BUZZER_ACTIVE_LOW) ? BUZZER_HIGH : 0);
  if (attached) ledcWrite(PIN_BUZZER, duty);
  else digitalWrite(PIN_BUZZER, mode == BUZZER_PASSIVE ? LOW : (duty ? HIGH : LOW));
}

bool buzzerBegin(uint8_t mode) {
  outputMode = 255;   // 強制寫入第一次靜音
  outOn = false;
  digitalWrite(PIN_BUZZER, mode == BUZZER_ACTIVE_LOW ? HIGH : LOW);
  pinMode(PIN_BUZZER, OUTPUT);
  attached = ledcAttach(PIN_BUZZER, BUZZER_HZ, BUZZER_BITS);
  if (!attached) pinMode(PIN_BUZZER, OUTPUT);
  writeOut(false, mode);
  return attached;
}

void buzzerUpdate(uint32_t now, const FlightStatus &f, uint8_t mode) {
  bool on = false;

  // 等安全開關(起飛程序等待中,或上電自動倒數在待機等):從開始等的那一刻起算週期,第一聲馬上響
  const bool armWait = f.armWaitLeftS >= 0;
  if (armWait && !armWaitWas) armWaitStartMs = now;
  armWaitWas = armWait;

  if (f.state == FS_COUNTDOWN) {
    const float remain = f.countdownRemainS;
    if (lastState != FS_COUNTDOWN) {
      nextCountBeepMs = now;   // 進入倒數(含外力介入後重新放穩繼續倒數)第一聲馬上響
      countBeepEndMs = 0;
    }
    if (remain <= COUNT_FINAL_S) {
      on = true;
    } else {
      if ((int32_t)(now - nextCountBeepMs) >= 0) {
        countBeepEndMs = now + COUNT_BEEP_MS;
        const float interval = constrain(remain * COUNT_INTERVAL_PER_S, COUNT_INTERVAL_MIN_S, COUNT_INTERVAL_MAX_S);
        nextCountBeepMs = now + (uint32_t)(interval * 1000.0f);
      }
      on = countBeepEndMs && (int32_t)(now - countBeepEndMs) < 0;
    }
  } else if (armWait) {
    on = (now - armWaitStartMs) % ARM_WAIT_PERIOD_MS < ARM_WAIT_ON_MS;
  } else if (f.landBuzz) {   // 降落減力提醒(風格設定開啟時,節奏由飛行狀態機決定)
    on = true;
  }

  // 開機就緒:離開電變解鎖階段時滴滴兩聲(每次開機一次),蓋過其他聲音
  if (!readyDone && lastState == FS_ARMING && f.state != FS_ARMING) {
    readyDone = true;
    readyStartMs = now ? now : 1;
  }
  if (readyStartMs) {
    const uint32_t t = now - readyStartMs;
    if (t < 2u * READY_BEEP_MS + READY_GAP_MS) {
      on = t < READY_BEEP_MS || t >= (uint32_t)READY_BEEP_MS + READY_GAP_MS;
    } else {
      readyStartMs = 0;
      if (armWait) armWaitStartMs = now;   // 滴滴蓋掉了等開關的第一聲:結束後從頭開始
    }
  }

  // 狀態機真的完成取消/長按停機才播放確認音,不靠蜂鳴器自己推算按住時間.
  if (f.armCancelHeld && !cancelWasHeld) {
    cancelToneActive = true;
    cancelToneStartMs = now;
  }
  cancelWasHeld = f.armCancelHeld;

  // 按住開關急響,成功取消/停機後同次按壓保持靜音,放開再按才恢復急響.
  // 放在就緒滴滴之後覆蓋,每次按下第一聲立即響,不阻塞控制工作.
  if (f.armSwitch) {
    if (!switchWasPressed) switchPressMs = now;
    on = !f.armCancelHeld && (now - switchPressMs) % SWITCH_PERIOD_MS < SWITCH_BEEP_MS;
  }
  switchWasPressed = f.armSwitch;

  // 確認音優先於急響與其他提示;途中放開仍播完兩聲,不阻塞控制迴圈.
  if (cancelToneActive) {
    const uint32_t t = now - cancelToneStartMs;
    const uint32_t secondStart = CANCEL_LEAD_MS + CANCEL_BEEP_MS + CANCEL_GAP_MS;
    if (t < secondStart + CANCEL_BEEP_MS) {
      on = (t >= CANCEL_LEAD_MS && t < CANCEL_LEAD_MS + CANCEL_BEEP_MS) || t >= secondStart;
    } else {
      cancelToneActive = false;
    }
  }

  lastState = f.state;
  writeOut(on, mode);
}

void buzzerDebug(char *out, size_t n) {
  gpio_input_enable((gpio_num_t)PIN_BUZZER);   // 只開輸入緩衝讀電位,不影響輸出
  snprintf(out, n, "buzz mode=%u attached=%d on=%d duty=%lu pin=%d", outputMode, attached, outOn,
           (unsigned long)(attached ? ledcRead(PIN_BUZZER) : 0), gpio_get_level((gpio_num_t)PIN_BUZZER));
}
