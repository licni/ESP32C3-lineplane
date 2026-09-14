// 版本流水號: r19 (2026-09-14) 飛行輸入加安全開關等待上限的測試覆寫秒數(序列指令 armwait)
// 舊: r18 (2026-09-14) 安全開關 GPIO21 讀取與去抖(50ms),測試指令可覆寫
// 舊: r17 (2026-09-14) 飛行輸入加韌體更新擋起飛原因;韌體寫入中拒絕手動輸出
// 舊: r16 (2026-09-13) 機輪收腳舵機每拍更新;網頁試收輪(待機限定,10 秒自動放下)
// 舊: r15 (2026-09-13) 感測器正常過之後故障就鎖定到重新上電(恢復回應也不採用,記事件一次)
// 舊: r14 (2026-09-13) 測試掛勾:感測器模擬注入,狀態燈腳位取樣
// 舊: r13 (2026-09-13) 試推燈的水平判斷改用設定的起飛前水平限制(原本寫死 35 度)
// 舊: r12 (2026-09-13) 事件紀錄:感測器故障/恢復,量程飽和,控制迴圈延遲,手動輸出開始/結束,校正完成
// 舊: r11 (2026-09-13) 電變輸出改 escWrite(脈寬,百分比,停止),支援 DShot;遙測加 DShot 值
// 舊: r10 (2026-09-13) 電變校正輸出(開機保持最高油門後回最低),網頁手動輸出(心跳 0.5 秒逾時,限待機,從最低開始)
// 舊: r9 (2026-09-13) 遙測加 3 秒內最大手勢推力
// 舊: r8 (2026-09-13) 移除輸出掃動測試(舵機不動是測試線壞掉,已結案)
// 舊: r6 (2026-09-13) 接上飛行狀態機:電變輸出,狀態燈,姿態飛行增益與向心力補償速度,門檻改用飛行快照
// 舊: r5 (2026-09-13) 加地面滑行抖動判斷,手勢推力與試推燈,飛行紀錄寫入
// 舊: r4 (2026-09-13) 加衝擊尖峰偵測,遙測回報最近一次短尖峰
// 舊: r3 (2026-09-13) 套用角度修正,遙測加原始仰角
// 舊: r2 (2026-09-13) 優先權改系統最高(實測被 WiFi 搶佔)
// 舊: r1 (2026-09-13) 由 main.cpp 拆出:控制工作與遙測快照
#include "control.h"
#include "esc_output.h"
#include "event_log.h"
#include "imu.h"
#include "impact.h"
#include "flight.h"
#include "flight_log.h"
#include "fw_update.h"
#include "gear.h"
#include "pins_config.h"
#include "settings.h"
#include "test_hooks.h"

static const uint32_t CONTROL_PERIOD_MS = 5;         // 200Hz,與 MPU6050 取樣率一致
// 優先權取系統最高(24),高過 WiFi 驅動(23)與網路堆疊(18). 2026-09-13 實測(tools/web_load_test.py):
//   優先權 5 :載入網頁時被搶佔,單輪最長 5ms,節拍延遲 2~5ms;手機連上/斷開熱點時延遲 32ms(WPA2 握手).
//   優先權 24:載入網頁延遲 0ms,連上/斷開 0~16ms(剩下的是 WiFi 關中斷,優先權擋不住);網頁回應速度不變.
// 控制工作每 5ms 只用約 0.9ms,WiFi 仍有八成以上時間. 代價:這個工作裡絕不能出現忙等迴圈.
static const UBaseType_t CONTROL_TASK_PRIORITY = configMAX_PRIORITIES - 1;
static const uint32_t CONTROL_TASK_STACK = 6144;
static const uint8_t IMU_FAULT_READ_ERRORS = 10;     // 連續讀取失敗幾次判定故障(50ms)
static const float DT = CONTROL_PERIOD_MS / 1000.0f;
static const uint32_t GESTURE_LAMP_MS = 1500;        // 試推達標後綠燈亮多久
static const uint32_t LOOP_LATE_EVENT_MS = 20;       // 節拍延遲超過這個值記進事件紀錄
static const uint8_t ARM_DEBOUNCE_TICKS = 10;        // 安全開關低電位連續幾拍算按下(50ms)

static Telemetry telemetry;
static portMUX_TYPE telemetryLock = portMUX_INITIALIZER_UNLOCKED;
static volatile bool imuPresent = false;
static volatile bool timingResetRequest = false;

// --- 電變維護:網頁手動輸出與開機校正 ---
static const uint32_t MANUAL_TIMEOUT_MS = 500;        // 心跳逾時:網頁斷線或關掉,0.5 秒內回最低油門
static const uint16_t MANUAL_START_TOLERANCE_US = 20; // 開始手動輸出時必須在最低油門附近
static portMUX_TYPE manualLock = portMUX_INITIALIZER_UNLOCKED;
static uint16_t manualUs = 0;
static uint32_t manualBeatMs = 0;                     // 最近一次心跳;0 = 沒有手動輸出
static volatile uint8_t calibState = CALIB_NONE;
static volatile uint32_t gearTestUntilMs = 0;          // 網頁試收輪:0 = 沒有
static const uint32_t GEAR_TEST_MS = 10000;
static uint32_t calibStartMs = 0;

// 心跳距今多久. loop 可能在控制工作讀 nowMs 之後才寫入心跳,相減為負時當作剛收到.
static uint32_t beatAge(uint32_t nowMs, uint32_t beatMs) {
  return (int32_t)(nowMs - beatMs) < 0 ? 0 : nowMs - beatMs;
}

static bool manualAliveAt(uint32_t nowMs, uint32_t beatMs) {
  return beatMs != 0 && beatAge(nowMs, beatMs) <= MANUAL_TIMEOUT_MS;
}

static void controlTask(void *) {
  TickType_t lastWake = xTaskGetTickCount();
  uint8_t readErrors = 0;
  bool imuFault = true;
  uint32_t maxExecUs = 0;
  uint32_t maxLateMs = 0;
  uint32_t loopCount = 0;
  ImuReading reading = {};
  ImpactDetector impact;
  ImpactEvent lastImpact = {0, 0};
  uint32_t lastImpactMs = 0;
  GroundRollDetector groundRoll;
  float pushG = 0;
  float gesturePeakG = 0;
  uint32_t gestureHitMs = 0;
  float pushPeak3s = 0;        // 3 秒內最大推力(設定頁試推用)
  uint32_t pushPeakMs = 0;
  FlightOutputs flightOut = {false, 0, 0, false};
  bool ledOn = false;
  FlightState lastFlightState = FS_ARMING;
  bool manualWas = false;
  uint32_t lastLateEventMs = 0;
  uint32_t lastSatEventMs = 0;
  bool imuEverOk = false;          // 這次開機感測器正常過
  bool imuLatched = false;         // 正常過之後又故障:這次通電不再採用
  bool imuRecoverLogged = false;
  uint8_t armLowTicks = 0;

  for (;;) {
    // lastWake 被更新成「這一輪原本該醒來的時刻」,實際醒來時刻與它的差就是延遲.
    xTaskDelayUntil(&lastWake, pdMS_TO_TICKS(CONTROL_PERIOD_MS));
    if (timingResetRequest) {
      timingResetRequest = false;
      maxExecUs = 0;
      maxLateMs = 0;
    }
    const uint32_t lateMs = (uint32_t)(xTaskGetTickCount() - lastWake) * portTICK_PERIOD_MS;
    if (lateMs > maxLateMs) maxLateMs = lateMs;
    // 延遲 20ms 以上(少了 4 拍)記進事件紀錄,最多 5 秒一筆,免得洗版
    if (lateMs >= LOOP_LATE_EVENT_MS && millis() - lastLateEventMs >= 5000) {
      lastLateEventMs = millis();
      eventLog(EV_LOOP_LATE, 0, lateMs);
    }
    const uint32_t startUs = micros();
    const uint32_t nowMs = millis();
    // 待機時是即時設定,手勢成立後是這趟飛行的快照(上一拍更新,差 5ms 無妨)
    const SharedSettings &cfg = flightShared();

    float spikeThisTick = 0;
    if (imuPresent) {
      bool readOk = imuRead(reading);
      testSimApply(reading, readOk, nowMs);   // 測試用感測器模擬(只有 USB 序列指令能開啟)
      if (readOk && imuLatched) {
        // 故障過就不再採用(GG 2026-09-13):接觸不良的感測器時好時壞,恢復後的資料不可信;
        // 飛行中恢復時用含向心力的讀值重新定姿,實測機頭讀值亂擺 +51°~−25° 約 8 秒. 要重新上電才恢復使用.
        readErrors = 0;
        if (!imuRecoverLogged) {
          eventLog(EV_IMU_OK, 1);   // arg 1 = 感測器又有回應,但這次通電不採用
          imuRecoverLogged = true;
        }
      } else if (readOk) {
        readErrors = 0;
        if (imuFault) {   // 只會發生在開機後還沒正常讀到過的時候
          imuFault = false;
          attitudeReset();
          if (imuRecoverLogged) eventLog(EV_IMU_OK, 0);   // 開機時記過故障才記恢復
          imuRecoverLogged = false;
        }
        imuEverOk = true;
        if (reading.saturated && nowMs - lastSatEventMs >= 2000) {
          lastSatEventMs = nowMs;
          eventLog(EV_SATURATED, flightOut.motorOn ? 1 : 0, reading.accMagG);
        }
        // 姿態:飛行中用飛行增益並扣向心力(速度由狀態機依時間軸給),不學陀螺儀零點
        attitudeUpdate(reading, DT, flightOut.speedMps, flightOut.inFlight);
        ImpactEvent ev;
        if (impact.update(reading.accMagG, DT, ev) && ev.isShort()) {
          lastImpact = ev;
          lastImpactMs = nowMs;
          spikeThisTick = ev.peakG;
        }
      } else if (!readOk && readErrors < 255 && ++readErrors >= IMU_FAULT_READ_ERRORS) {
        if (!imuFault || (!imuEverOk && !imuRecoverLogged)) eventLog(EV_IMU_FAULT, flightOut.motorOn ? 1 : 0);
        if (!imuEverOk) imuRecoverLogged = true;   // 開機階段:之後讀到了要記恢復
        imuFault = true;
        if (imuEverOk) imuLatched = true;
        impact.reset();
        groundRoll.reset();
      }
    }
    const bool imuOk = imuPresent && !imuFault;

    const float rawPitch = attitudePitchDeg();
    const float pitch = constrain(rawPitch + cfg.pitchTrimDeg, -90.0f, 90.0f);
    const float roll = attitudeRollDeg();

    bool gestureLevel = false;
    if (imuOk) {
      groundRoll.update(reading.accG[2], pitch, roll, DT, cfg.earlyLandVibG, cfg.earlyLandTiltDeg);
      // 手勢推力:機頭方向的加速度計讀值扣掉重力分量,剩下的就是人推的力.
      // 用未修正的原始仰角:這是物理量換算,角度修正只是給飛行時水平讀 0 用的.
      pushG = reading.accG[0] - sinf(rawPitch * DEG_TO_RAD);
      // 試推燈的「機身大致水平」與起飛前水平限制用同一個角度(狀態機拒絕啟動也看它)
      gestureLevel = fabsf(pitch) <= cfg.startLevelDeg && fabsf(roll) <= cfg.startLevelDeg;
      if (pushG >= pushPeak3s || nowMs - pushPeakMs > 3000) {
        pushPeak3s = pushG;
        pushPeakMs = nowMs;
      }
      if (gestureLevel && pushG >= cfg.gestureG) {
        if (nowMs - gestureHitMs > GESTURE_LAMP_MS || pushG > gesturePeakG) gesturePeakG = pushG;
        gestureHitMs = nowMs;
      }
    }

    // --- 電變維護 ---
    // 校正:開機時已輸出最高油門,保持設定秒數後回最低. 解鎖時間由狀態機從這之後才算.
    if (calibState == CALIB_HOLD_MAX && beatAge(nowMs, calibStartMs) >= (uint32_t)(cfg.calibHoldSec * 1000.0f)) {
      calibState = CALIB_DONE;
      Serial.println(F("ESC calibration: max hold done, output min"));
      eventLog(EV_CALIB_DONE, 0, cfg.escMinUs);
    }
    uint16_t mUs = 0;
    uint32_t mBeat = 0;
    portENTER_CRITICAL(&manualLock);
    mUs = manualUs;
    mBeat = manualBeatMs;
    portEXIT_CRITICAL(&manualLock);
    // 手動輸出只在待機/結束狀態有效(上一拍的狀態);逾時或狀態不對就結束這次手動輸出.
    const bool idleState = lastFlightState == FS_STANDBY || lastFlightState == FS_DONE;
    bool manual = manualAliveAt(nowMs, mBeat) && idleState && calibState != CALIB_HOLD_MAX;
    if (mBeat && !manual) {
      portENTER_CRITICAL(&manualLock);
      if (manualBeatMs == mBeat) manualBeatMs = 0;
      portEXIT_CRITICAL(&manualLock);
    }
    const bool escService = manual || calibState == CALIB_HOLD_MAX;
    if (manual != manualWas) {
      if (manual) eventLog(EV_MANUAL_START);
      else eventLog(EV_MANUAL_END, beatAge(nowMs, mBeat) > MANUAL_TIMEOUT_MS ? 1 : 0);
      manualWas = manual;
    }

    // --- 飛行狀態機 ---
    FlightInputs fin;
    fin.imuOk = imuOk;
    fin.pitchDeg = pitch;
    fin.rollDeg = roll;
    for (uint8_t i = 0; i < 3; ++i) {
      fin.accG[i] = reading.accG[i];
      fin.gyroDps[i] = reading.gyroDps[i];
    }
    fin.accMagG = reading.accMagG;
    fin.pushG = pushG;
    fin.gestureLevel = gestureLevel;
    fin.spikeG = spikeThisTick;
    fin.rollHoldS = imuOk ? groundRoll.holdSeconds() : 0;
    fin.escService = escService;
    fin.fwBlock = fwUpdateBlockReason();   // 韌體更新中或新韌體待確認:拒絕起飛
    // 安全開關 GPIO21:低電位連續 10 拍(50ms)才算按下,放開立即算沒按(去抖只做一邊). 測試指令 armsw 可覆寫.
    {
      const int8_t ov = testArmOverride();
      const bool low = ov >= 0 ? ov == 1 : digitalRead(PIN_ARM_SWITCH) == LOW;
      armLowTicks = low ? (armLowTicks < 255 ? armLowTicks + 1 : 255) : 0;
    }
    fin.armSwitch = armLowTicks >= ARM_DEBOUNCE_TICKS;
    fin.armWaitTestS = testArmWaitOverride();
    fin.nowMs = nowMs;
    flightOut = flightUpdate(fin, DT);

    // --- 電變輸出 --- 百分比依共用設定的 0%/100% 脈寬換算;馬達沒轉時輸出 0% 的脈寬
    const float span = (float)(cfg.escMaxUs - cfg.escMinUs);
    float pct = flightOut.motorOn ? constrain(flightOut.throttlePct, 0.0f, 100.0f) : 0.0f;
    // PWM 用脈寬;DShot 用百分比,馬達停止時送停止指令(解鎖前的 3 秒一直是停止指令)
    if (calibState == CALIB_HOLD_MAX) {
      pct = 100;
      escWrite(cfg.escMaxUs, pct, false);
    } else if (manual && !flightOut.motorOn) {
      const uint16_t us = constrain(mUs, cfg.escMinUs, cfg.escMaxUs);
      pct = span > 0 ? (us - cfg.escMinUs) * 100.0f / span : 0;
      escWrite(us, pct, pct <= 0);
    } else {
      escWrite((uint16_t)lroundf(cfg.escMinUs + span * pct / 100.0f), pct, !flightOut.motorOn);
    }
    const uint16_t escUs = escCurrentUs();

    // --- 機輪收腳 --- 飛行由狀態機決定;待機時網頁「試收輪」可暫時收起(最多 10 秒,離開待機立即放下)
    uint32_t gTest = gearTestUntilMs;
    if (gTest && (!idleState || (int32_t)(nowMs - gTest) >= 0)) {
      gearTestUntilMs = 0;
      gTest = 0;
    }
    gearUpdate(flightOut.gearUp || gTest != 0, cfg, DT);

    // --- 狀態燈 ---
    const bool led = flightLedPattern(nowMs, imuFault) != 0;
    if (led != ledOn) {
      ledOn = led;
      digitalWrite(PIN_STATUS_LED, (led != STATUS_LED_ACTIVE_LOW) ? HIGH : LOW);
    }
    testLedSample(nowMs);
    ++loopCount;

    // --- 飛行紀錄 ---
    const bool gestureLamp = gestureHitMs && nowMs - gestureHitMs <= GESTURE_LAMP_MS;
    FlightStatus fst;
    flightGetStatus(fst);
    lastFlightState = fst.state;
    uint8_t flags = 0;
    if (groundRoll.level()) flags |= LOG_FLAG_LEVEL;
    if (groundRoll.holdSeconds() >= cfg.earlyLandHoldSec) flags |= LOG_FLAG_ROLL_HOLD;
    if (imuFault) flags |= LOG_FLAG_IMU_FAULT;
    if (gestureLamp) flags |= LOG_FLAG_GESTURE;
    flightLogFeed(pitch, pct, reading.accMagG, groundRoll.vibG(), spikeThisTick, pushG, fst.state, flags, nowMs);

    const uint32_t execUs = micros() - startUs;
    if (execUs > maxExecUs) maxExecUs = execUs;

    portENTER_CRITICAL(&telemetryLock);
    telemetry.rawPitchDeg = rawPitch;
    telemetry.pitchDeg = pitch;
    telemetry.rollDeg = roll;
    telemetry.vibG = groundRoll.vibG();
    telemetry.levelOk = groundRoll.level();
    telemetry.rollHoldS = groundRoll.holdSeconds();
    telemetry.pushG = pushG;
    telemetry.gestureLamp = gestureLamp;
    telemetry.gesturePeakG = gesturePeakG;
    telemetry.pushPeak3sG = pushPeak3s;
    telemetry.accMagG = reading.accMagG;
    for (uint8_t i = 0; i < 3; ++i) telemetry.gyroDps[i] = reading.gyroDps[i];
    imuGyroBiasDps(telemetry.biasDps);
    telemetry.still = imuIsStill();
    telemetry.stillSeconds = imuStillSeconds();
    telemetry.imuPresent = imuPresent;
    telemetry.imuFault = imuFault;
    telemetry.escUs = escUs;
    telemetry.escDshot = escCurrentDshot();
    telemetry.loopCount = loopCount;
    telemetry.maxExecUs = maxExecUs;
    telemetry.maxLateMs = maxLateMs;
    telemetry.impactPeakG = lastImpact.peakG;
    telemetry.impactMs = lastImpact.durationMs;
    telemetry.impactAgeMs = lastImpactMs ? nowMs - lastImpactMs : UINT32_MAX;
    telemetry.manualActive = manual;
    telemetry.calibState = calibState;
    telemetry.calibRemainS =
        calibState == CALIB_HOLD_MAX ? max(0.0f, cfg.calibHoldSec - beatAge(nowMs, calibStartMs) / 1000.0f) : 0;
    portEXIT_CRITICAL(&telemetryLock);
  }
}

void controlBegin(bool present, bool calibrate, uint32_t calibStart) {
  imuPresent = present;
  pinMode(PIN_ARM_SWITCH, INPUT_PULLUP);   // 安全開關:沒接或斷線 = 高電位 = 不能起飛
  if (calibrate) {
    calibStartMs = calibStart;
    calibState = CALIB_HOLD_MAX;
  }
  flightBegin();
  xTaskCreate(controlTask, "control", CONTROL_TASK_STACK, nullptr, CONTROL_TASK_PRIORITY, nullptr);
}

void controlGetTelemetry(Telemetry &out) {
  portENTER_CRITICAL(&telemetryLock);
  out = telemetry;
  portEXIT_CRITICAL(&telemetryLock);
}

bool controlImuPresent() { return imuPresent; }
void controlSetImuPresent(bool present) { imuPresent = present; }
void controlResetTimingStats() { timingResetRequest = true; }
static bool manualAliveNow() {
  portENTER_CRITICAL(&manualLock);
  const uint32_t beat = manualBeatMs;
  portEXIT_CRITICAL(&manualLock);
  return manualAliveAt(millis(), beat);
}

const char *controlManualWrite(uint16_t us) {
  FlightStatus f;
  flightGetStatus(f);
  if (f.state != FS_STANDBY && f.state != FS_DONE) return "manualstate";
  if (calibState == CALIB_HOLD_MAX) return "manualstate";
  if (fwUpdateBlockReason() == 1) return "busy";   // 韌體寫入中(寫快閃時控制迴圈會停頓,不可轉馬達)
  SharedSettings s;
  settingsCopyShared(s);
  if (us < s.escMinUs || us > s.escMaxUs) return "range";
  const uint32_t now = millis();
  const char *err = nullptr;
  portENTER_CRITICAL(&manualLock);
  if (!manualAliveAt(now, manualBeatMs) && us > s.escMinUs + MANUAL_START_TOLERANCE_US) {
    err = "manuallow";
  } else {
    manualUs = us;
    manualBeatMs = now ? now : 1;
  }
  portEXIT_CRITICAL(&manualLock);
  return err;
}

void controlManualStop() {
  portENTER_CRITICAL(&manualLock);
  manualBeatMs = 0;
  portEXIT_CRITICAL(&manualLock);
}

// 手動輸出或校正中也不允許:OTA/重開機會讓訊號中斷,電變行為不可預期.
bool controlOtaAllowed() { return flightOtaAllowed() && !manualAliveNow() && calibState != CALIB_HOLD_MAX; }

bool controlSettingsLocked() { return flightSettingsLocked(); }

const char *controlGearTest(bool up) {
  if (!up) {
    gearTestUntilMs = 0;
    return nullptr;
  }
  FlightStatus f;
  flightGetStatus(f);
  if (f.state != FS_STANDBY && f.state != FS_DONE) return "manualstate";
  gearTestUntilMs = (millis() + GEAR_TEST_MS) | 1;
  return nullptr;
}

bool controlGearTesting() { return gearTestUntilMs != 0; }
