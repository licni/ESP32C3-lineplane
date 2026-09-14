// 版本流水號: r21 (2026-09-14) 降落保險時間改從減力走完才開始算(降落最長 = 減力秒數 + 保險時間;GG:減力 20 + 保險 20 時減力一完就關馬達)
// 舊: r20 (2026-09-14) 安全開關等待上限(GG:3 分鐘可調):起飛程序開始後超過上限沒按開關 → 取消回待機(事件 28/3);
//   上電自動倒數等開關逾時 → 這次通電不再自動倒數(事件 28/4). 桌上碰到飛機誤觸發時不會一直鎖著設定
// 舊: r19 (2026-09-14) 安全開關改成「起飛程序照常開始,按下才倒數」(GG):開始不再拒絕(原因 7/8 不再產生),
//   起飛程序中按下一次就記住,放穩(或上電自動倒數放平 1 秒)後開始倒數;上電自動倒數等待中燈慢閃;事件 28
// 舊: r18 (2026-09-14) 撞擊斷電後推飛機不算手勢(原因 9);飛行中油門下限保底 10%
// 舊: r17 (2026-09-14) 安全開關 GPIO21 沒按下不開始起飛程序(手勢拒絕原因 7;自動倒數等按下,原因 8);撞擊斷電改連續 2 拍
// 舊: r16 (2026-09-14) 韌體更新中或新韌體待確認時拒絕起飛(拒絕原因 5/6)
// 舊: r15 (2026-09-14) 上電後直接倒數只給真正的上電重置(GG):OTA/網頁重開/當機重開一律待機,解鎖事件 arg 3
// 舊: r14 (2026-09-14) 網頁「開始起飛程序」按鈕:走啟動手勢同一套判斷,事件記來源(0 推飛機 / 1 序列埠 / 2 網頁)
// 舊: r13 (2026-09-13) 機輪收腳:馬達啟動 N 秒後收,降落/停止/待機放下,提早降落開啟時不收;收放記事件
// 舊: r12 (2026-09-13) 外力大小改用不跟著外力重抓的參考量(原本永遠停在門檻附近);繼續倒數事件 b = 外力最大值
// 舊: r11 (2026-09-13) 等待放穩/倒數中角度超過水平限制持續 0.2 秒 → 取消回待機,記事件
// 舊: r10 (2026-09-13) 起飛前水平限制:手勢推力夠但角度超過 → 拒絕並記事件(5 秒一筆);上電自動倒數角度超過 → 待機等放平 1 秒才倒數
// 舊: r9 (2026-09-13) 扭轉機尾取消手勢起飛:等待放穩/倒數中繞機背軸累積轉角超過設定 → 回待機,封鎖手勢設定秒數
// 舊: r8 (2026-09-13) 事件紀錄:解鎖,手勢,拒絕,倒數,外力,取消,馬達啟動,換段,開始降落(原因),馬達停止(原因與數值/門檻)
// 舊: r7 (2026-09-13) 電變校正/手動輸出中不啟動,並用掉上電自動倒數;校正時解鎖時間從校正結束算
// 舊: r6 (2026-09-13) 兩段共用一條補償曲線(刪除第二段曲線)
// 舊: r5 (2026-09-13) 外力延長有上限:倒數最多到「倒數秒數 +10 秒」(拿在手上一直晃不會無限累加);序列測試用 disturb
// 舊: r4 (2026-09-13) 外力參考修正:開機取第一筆讀值,待機時約 1 秒緩慢跟隨(副廠晶片 1.12g 使待機時假外力 0.13g)
// 舊: r3 (2026-09-13) 回報即時外力大小與 3 秒內最大值,外力超過門檻時刻(設定頁指示燈用)
// 舊: r2 (2026-09-13) 第二段用第二段曲線,換段有過渡時補償也跟著過渡
// 舊: r1 (2026-09-13) 初版:飛行狀態機(解鎖,待機,手勢,放穩,倒數,外力,起飛,換段,補償,降落,觸地,撞擊,緊急停止,燈號)
#include "flight.h"
#include "esc_service.h"
#include "event_log.h"

static const uint32_t ESC_ARM_MS = 3000;            // 上電後給電變最低油門的解鎖時間
static const float SETTLE_REQUIRED_S = 1.0f;        // 放穩要維持多久才開始(或繼續)倒數
static const float ACC_LPF_TAU_S = 0.05f;           // 放穩/外力判斷用的加速度低通
static const float LAND_GYRO_LPF_TAU_S = 0.2f;      // 降落靜止判斷用的角速度低通(濾掉馬達震動)
// 降落中「完全靜止」:空中的飛機一定繞著圓心偏航(單圈 5 秒約 70°/秒),停在地上才會接近 0.
// 馬達還開著降落油門,原本 0.5 秒窗的靜止偵測會被震動破壞,所以改看低通後的角速度.
static const float LAND_STILL_GYRO_DPS = 8.0f;
static const float LAND_STILL_ACC_G = 0.10f;
static const float SPEED_RAMP_MIN_S = 3.0f;         // 起飛時向心力補償的速度爬升時間(模擬用 3 秒)
static const uint32_t REJECT_FLASH_MS = 1000;       // 拒絕啟動時燈急閃多久
static const uint32_t GESTURE_REARM_MS = 1500;      // 一次手勢之後多久才接受下一次
// 外力介入延長的上限:倒數最多到「倒數秒數 + 10 秒」. 沒有上限時,飛機拿在手上一直晃,每次放穩就再加,
// 倒數會累加到非常大(GG 2026-09-13 指出).
static const float COUNTDOWN_EXTEND_LIMIT_S = 10.0f;
// 扭轉機尾取消起飛(GG 2026-09-13):手勢一成立就一路倒數到強迫起飛不好,來不及開手機時要能用手取消.
// 抓著機尾繞機背軸轉超過設定角度 → 回待機,並且一段時間不接受手勢(抬尾巴放下的撞擊不會又觸發).
// 角速度小於這個值不累積:放在地上時陀螺儀零點殘差不會慢慢積到門檻,手扭轉一定比這快很多.
static const float TWIST_RATE_DEADBAND_DPS = 5.0f;

static portMUX_TYPE statusLock = portMUX_INITIALIZER_UNLOCKED;
static FlightStatus status;

static FlightState state = FS_ARMING;
static uint32_t stateStartMs = 0;
static uint32_t nowMsCache = 0;
static SharedSettings fs;       // 待機時每拍更新成目前設定;手勢成立後凍結成這趟飛行的快照
static ProfileSettings fp;      // 這趟飛行的風格快照
static uint8_t fpIndex = 0;
static bool autoStartUsed = false;
static bool bootNoAutoStart = false;   // 這次開機不是上電重置:不給上電自動倒數(flightBegin 決定)
static const uint8_t CRASH_CONFIRM_TICKS = 2;   // 撞擊斷電要連續幾拍超過門檻
static uint8_t crashTicks = 0;

// 安全開關(GG 2026-09-14 r19):起飛程序照常開始,等安全開關按下才倒數. 用途是「人在飛機旁,確定要飛了」.
// 起飛程序中(等待放穩,或上電自動倒數等待中)按下一次就記住:按的時候碰動飛機沒關係,重新放穩就開始倒數.
// 開始當下已經按著也算 —— 飛場上開關壞掉時把兩腳跳線短路(等於一直按著),照樣能飛.
static bool armLatched = false;
static bool armWaitLogged = false;   // 這趟起飛程序已記過「等安全開關」事件
// 等待上限(GG 2026-09-14 r20):開發板放桌上被碰一下(手勢門檻調低時很容易)就進入起飛程序,沒按開關會一直等,設定也一直鎖著.
// 從起飛程序開始(上電自動倒數是解鎖完開始等)累計沒按開關的時間,超過上限就取消. 按過就不再計.
static float armWaitS = 0;

static volatile bool reqCancel = false, reqEstop = false, reqGesture = false, reqDisturb = false, reqTwist = false,
                     reqTilt = false;
static volatile uint8_t reqGestureSource = GESTURE_SRC_SERIAL;

// 扭轉取消
static bool gestureStarted = false;       // 這趟起飛程序是手勢啟動的(上電自動倒數不做扭轉取消)
static float twistDeg = 0;
static uint32_t gestureBlockUntilMs = 0;  // 0 = 沒有封鎖

// 放穩與外力
static float accLpf[3] = {0, 0, 1};
static bool accLpfInit = false;
static float settleRef[3] = {0, 0, 1};
// 量「外力有多大」用的參考. settleRef 在外力期間每拍都重抓(放穩計時要從最後一次晃動算起),拿它量大小只會量到
// 5ms 內的變化,數字永遠停在門檻附近(全功能測試段 1:側推 0.6g 記成 0.31g). magRef:待機類狀態約 1 秒緩慢跟隨,
// 倒數中等於放穩參考,等待放穩中凍結 —— 量到的是「相對飛機原本放著的樣子動了多少」.
static float magRef[3] = {0, 0, 1};
static float settleS = 0;
static float countdownRemain = 0;
static bool resumeCountdown = false;        // 等待放穩是因為倒數中外力介入
static DisturbAction pendingAction = DISTURB_ACT_NONE;
static DisturbAction lastDisturbAction = DISTURB_ACT_NONE;
static float lastDisturbG = 0;
static float distPeakG = 0;          // 3 秒內最大外力(設定頁指示燈用)
static uint32_t distPeakMs = 0;
static uint32_t distOverMs = 0;      // 最近一次外力超過門檻的時刻
static uint32_t lastDisturbMs = 0;

// 啟動拒絕
static RejectReason rejectReason = REJECT_NONE;
static uint32_t rejectMs = 0;
static uint32_t lastGestureMs = 0;

// 飛行
static uint32_t motorStartMs = 0;
static uint32_t motorStopMs = 0;
static float landingStartPct = 0;
static float landingElapsed = 0;
static LandingCause landingCause = LAND_NONE;
static FlightEndReason endReason = END_NONE;
static float gyroLpfMag = 0;
static float landStillS = 0;
static float landAccRef[3] = {0, 0, 1};
static float lastBase = 0, lastComp = 0, lastOut = 0;
static uint8_t phase = 0;
static bool lastGearUp = false;

static void enter(FlightState s) {
  state = s;
  stateStartMs = nowMsCache;
}

static bool motorState(FlightState s) { return s == FS_TAKEOFF || s == FS_FLYING || s == FS_LANDING; }

static float dist3(const float a[3], const float b[3]) {
  const float dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
  return sqrtf(dx * dx + dy * dy + dz * dz);
}

static void captureSettleRef() {
  memcpy(settleRef, accLpf, sizeof(settleRef));
  settleS = 0;
}

// value / limit:造成停止的量測值與門檻,寫進事件紀錄(使用者查「馬達為什麼停」用)
static void finish(FlightEndReason reason, float value, float limit) {
  endReason = reason;
  motorStopMs = nowMsCache;
  enter(FS_DONE);
  eventLog(EV_MOTOR_STOP, reason, value, limit);
}

static void reject(RejectReason r) {
  rejectReason = r;
  rejectMs = nowMsCache ? nowMsCache : 1;
  eventLog(EV_REJECT, r);
}

// --- 起飛前水平限制(GG 2026-09-13)---
// 機頭或滾轉超過設定角度時,啟動手勢推再大力都不啟動;上電自動倒數也不開始,等飛機放平並維持 1 秒才倒數.
static const float AUTO_LEVEL_HOLD_S = 1.0f;
static const uint32_t TILT_LOG_INTERVAL_MS = 5000;   // 拿著飛機走動時可能一直有「推力」,事件紀錄最多 5 秒一筆
// 起飛程序中(等待放穩/倒數)角度超過限制持續這麼久就取消(GG:直接取消). 0.2 秒濾掉單次讀值跳動,人拿起飛機一定超過.
static const float TILT_CANCEL_HOLD_S = 0.2f;
static float tiltOverS = 0;
static bool autoWaitLevel = false;
static float levelHoldS = 0;
static uint32_t lastTiltLogMs = 0;
static uint32_t lastCrashLockLogMs = 0;

static bool withinStartLevel(const FlightInputs &in) {
  return in.imuOk && fabsf(in.pitchDeg) <= fs.startLevelDeg && fabsf(in.rollDeg) <= fs.startLevelDeg;
}

// 起飛程序中安全開關按下 → 記住(開關去抖在 control.cpp:低電位連續 50ms)
static void latchArm(const FlightInputs &in) {
  if (in.armSwitch && !armLatched) {
    armLatched = true;
    eventLog(EV_ARM_SWITCH, 2);
  }
}

static float armWaitLimitS(const FlightInputs &in) {
  return in.armWaitTestS ? (float)in.armWaitTestS : fs.armWaitMin * 60.0f;
}

// 還沒按安全開關:累計等待時間,超過上限回 true(呼叫端負責取消)
static bool armWaitExpired(const FlightInputs &in, float dt) {
  if (armLatched) return false;
  armWaitS += dt;
  return armWaitS >= armWaitLimitS(in);
}

static void rejectTilt(RejectReason r, const FlightInputs &in) {
  rejectReason = r;
  rejectMs = nowMsCache ? nowMsCache : 1;
  if (!lastTiltLogMs || nowMsCache - lastTiltLogMs >= TILT_LOG_INTERVAL_MS || r == REJECT_TILT_WAIT) {
    lastTiltLogMs = nowMsCache ? nowMsCache : 1;
    eventLog(EV_REJECT, r, in.pitchDeg, in.rollDeg);
  }
}

// 手勢成立或上電自動倒數:複製設定快照,檢查能不能飛.
static void tryStart(bool autoStart, const FlightInputs &in) {
  const bool imuOk = in.imuOk;
  const bool dirty = settingsSnapshotForFlight(fs, fp, fpIndex);
  // 自動倒數只給一次機會:就算這次被拒絕,之後存檔也不會突然自己開始倒數.
  if (autoStart) autoStartUsed = true;
  if (in.fwBlock) {   // 韌體更新中,或新韌體還沒確認(沒確認會自動退回重開,飛行中重開等於馬達停)
    reject(in.fwBlock == 1 ? REJECT_FW_UPDATING : REJECT_FW_UNCONFIRMED);
    enter(FS_STANDBY);
    return;
  }
  // 安全開關不在這裡擋(r19):起飛程序照常開始,等開關按下才倒數(見 FS_WAIT_STILL 與上電自動倒數的等待)
  if (dirty) {
    reject(REJECT_UNSAVED);
    enter(FS_STANDBY);
    return;
  }
  if (!imuOk) {
    reject(REJECT_IMU);
    enter(FS_STANDBY);
    return;
  }
  rejectReason = REJECT_NONE;
  endReason = END_NONE;
  landingCause = LAND_NONE;
  gestureStarted = !autoStart;
  twistDeg = 0;
  lastDisturbAction = DISTURB_ACT_NONE;
  resumeCountdown = false;
  armWaitLogged = false;
  armWaitS = 0;
  captureSettleRef();
  if (autoStart) {
    // 上電直接倒數:不等放穩(資深飛友習慣),外力照設定處理. 安全開關已在待機等待時按過.
    armLatched = true;
    countdownRemain = fs.countdownSec;
    enter(FS_COUNTDOWN);
    eventLog(EV_COUNTDOWN, 0, countdownRemain);
  } else {
    armLatched = in.armSwitch;   // 推飛機或按網頁開始的當下已經按著也算
    enter(FS_WAIT_STILL);
  }
}

static float baseThrottle(float t, uint8_t &phaseOut) {
  const float p1 = fp.phase1Pct, p2 = fp.phase2Pct, t1 = fp.phase1Sec;
  phaseOut = t < t1 ? 1 : 2;
  switch (fp.phaseMode) {
    case PHASE_STEP:
      return t < t1 ? p1 : p2;
    case PHASE_SPREAD:
      return t < t1 ? p1 + (p2 - p1) * t / t1 : p2;
    default: {   // PHASE_STEP_RAMP
      if (t < t1) return p1;
      const float r = fp.phaseRampSec > 0 ? min(1.0f, (t - t1) / fp.phaseRampSec) : 1.0f;
      return p1 + (p2 - p1) * r;
    }
  }
}

void flightBegin() {
  // 上電後直接倒數只給真正的上電(GG 2026-09-14):遠端 OTA 更新完重開時旁邊可能沒有人,
  // 網頁重開機或當機重開時飛機可能正拿在手上. 當成「自動倒數已經用過」,手勢與網頁開始按鈕照常可用.
  bootNoAutoStart = !escBootAllowsAutoStart();
  autoStartUsed = bootNoAutoStart;
  settingsCopyShared(fs);
  state = FS_ARMING;
  stateStartMs = millis();
}

FlightOutputs flightUpdate(const FlightInputs &in, float dt) {
  nowMsCache = in.nowMs;
  const uint32_t now = in.nowMs;
  FlightOutputs out = {false, 0, 0, false, false};

  // 待機類狀態:設定即時生效. 手勢成立後 fs 凍結成快照,整趟飛行不變.
  if (state == FS_ARMING || state == FS_STANDBY || state == FS_DONE) settingsCopyShared(fs);

  // --- 共用的量測 ---
  if (!accLpfInit) {
    memcpy(accLpf, in.accG, sizeof(accLpf));
    // 參考也取實際讀值:預設的 (0,0,1) 與副廠晶片靜止讀值(1.12g)差 0.13g,沒超過門檻就永遠不會更新,
    // 設定頁的外力指示會一直顯示假的 0.13g(2026-09-13 截圖發現).
    memcpy(settleRef, in.accG, sizeof(settleRef));
    memcpy(magRef, in.accG, sizeof(magRef));
    accLpfInit = true;
  }
  const float ka = dt / ACC_LPF_TAU_S;
  for (uint8_t i = 0; i < 3; ++i) accLpf[i] += (in.accG[i] - accLpf[i]) * ka;
  const float gyroMag = sqrtf(in.gyroDps[0] * in.gyroDps[0] + in.gyroDps[1] * in.gyroDps[1] + in.gyroDps[2] * in.gyroDps[2]);
  gyroLpfMag += (gyroMag - gyroLpfMag) * (dt / LAND_GYRO_LPF_TAU_S);

  // 放穩:加速度方向相對參考的變化不超過外力門檻. 用外力門檻而不是固定值 —— 戶外有風時調大就能放穩.
  const float settleDev = dist3(accLpf, settleRef);
  const bool disturbedNow = settleDev > fs.disturbG;
  // 外力大小(顯示與紀錄用,不參與判斷)
  if (state == FS_COUNTDOWN) memcpy(magRef, settleRef, sizeof(magRef));
  const float distMag = dist3(accLpf, magRef);
  if (distMag >= distPeakG || now - distPeakMs > 3000) {
    distPeakG = distMag;
    distPeakMs = now;
  }
  if (distMag > fs.disturbG) distOverMs = now ? now : 1;
  // 倒數中外力介入後,等待放穩期間記下外力最大值(放穩繼續倒數時寫進事件紀錄)
  if (state == FS_WAIT_STILL && resumeCountdown && distMag > lastDisturbG) lastDisturbG = distMag;

  // --- 請求 ---
  if (reqEstop) {
    reqEstop = false;
    if (motorState(state)) finish(END_ESTOP, (now - motorStartMs) / 1000.0f, 0);
  }
  if (reqCancel) {
    reqCancel = false;
    if (state == FS_WAIT_STILL || state == FS_COUNTDOWN) {
      endReason = END_CANCELED;
      enter(FS_STANDBY);
      eventLog(EV_CANCEL);
    }
  }

  // --- 扭轉機尾取消手勢起飛(等待放穩與倒數中) ---
  if ((state == FS_WAIT_STILL || state == FS_COUNTDOWN) && gestureStarted) {
    if (in.imuOk && fabsf(in.gyroDps[2]) >= TWIST_RATE_DEADBAND_DPS) twistDeg += in.gyroDps[2] * dt;
    const bool over = fs.twistCancelDeg > 0 && fabsf(twistDeg) >= fs.twistCancelDeg;
    if (over || reqTwist) {
      eventLog(EV_TWIST_CANCEL, fs.twistBlockSec, over ? fabsf(twistDeg) : 0, fs.twistCancelDeg);
      endReason = END_TWIST_CANCEL;
      resumeCountdown = false;
      pendingAction = DISTURB_ACT_NONE;
      gestureBlockUntilMs = (now + fs.twistBlockSec * 1000UL) | 1;
      enter(FS_STANDBY);
    }
  }
  reqTwist = false;

  // --- 起飛程序中角度超過水平限制:直接取消(手勢啟動與上電自動倒數都適用) ---
  if (state == FS_WAIT_STILL || state == FS_COUNTDOWN) {
    tiltOverS = (in.imuOk && !withinStartLevel(in)) ? tiltOverS + dt : 0;
    if (tiltOverS >= TILT_CANCEL_HOLD_S || reqTilt) {
      eventLog(EV_TILT_CANCEL, fs.startLevelDeg, in.pitchDeg, in.rollDeg);
      endReason = END_TILT_CANCEL;
      resumeCountdown = false;
      pendingAction = DISTURB_ACT_NONE;
      tiltOverS = 0;
      enter(FS_STANDBY);
    }
  } else {
    tiltOverS = 0;
  }
  reqTilt = false;

  // --- 撞擊斷電:馬達運轉中任何時候 ---
  // 連續 2 拍(10ms)都超過門檻才算(2026-09-14 安全審查):I2C 讀取沒有校驗,單筆錯位資料或感測器飽和的一拍
  // 不該在空中關馬達;真的撞機衝擊持續遠超過 10ms,不會漏.
  if (motorState(state) && fs.crashEnable && in.imuOk && in.accMagG >= fs.crashG) {
    if (++crashTicks >= CRASH_CONFIRM_TICKS) finish(END_CRASH, in.accMagG, fs.crashG);
  } else {
    crashTicks = 0;
  }

  switch (state) {
    case FS_ARMING:
      if (in.escService) {
        // 電變校正中:解鎖時間從校正結束(回到最低油門)才開始算;校正完不自動倒數,
        // 免得手勢關閉時校正一結束馬達就接著倒數啟動. 要飛請重新上電.
        autoStartUsed = true;
        stateStartMs = now;
        break;
      }
      if (now - stateStartMs >= ESC_ARM_MS) {
        // arg:1 = 等啟動手勢,0 = 接著上電自動倒數,2 = 手勢關閉但自動倒數已用過(例如剛校正完),
        //     3 = 手勢關閉但這次不是上電開機(OTA/網頁重開/當機重開),不自動倒數
        eventLog(EV_ARMED, fs.gestureEnable ? 1 : (!autoStartUsed ? 0 : (bootNoAutoStart ? 3 : 2)));
        if (!fs.gestureEnable && !autoStartUsed) {
          // 上電自動倒數:安全開關按過而且飛機放平才倒數;還沒按或沒放平就在待機等(燈慢閃,不用掉自動倒數的機會).
          // 感測器異常時不看水平,交給 tryStart 拒絕.
          armLatched = in.armSwitch;
          armWaitLogged = false;
          armWaitS = 0;
          const bool levelOk = !in.imuOk || withinStartLevel(in);
          if (armLatched && levelOk) {
            tryStart(true, in);
          } else {
            autoWaitLevel = true;
            levelHoldS = 0;
            if (!armLatched) {
              armWaitLogged = true;
              eventLog(EV_ARM_SWITCH, 1);   // 等安全開關(不是拒絕,不急閃)
            } else {
              rejectTilt(REJECT_TILT_WAIT, in);
            }
            enter(FS_STANDBY);
          }
        } else {
          enter(FS_STANDBY);
        }
      }
      break;

    case FS_STANDBY:
    case FS_DONE:
      if (in.escService) {   // 網頁手動輸出中:手勢一律不理(推飛機試轉時很容易誤觸)
        autoStartUsed = true;
        reqGesture = false;
        break;
      }
      if (gestureBlockUntilMs && (int32_t)(now - gestureBlockUntilMs) < 0) {   // 扭轉取消後的封鎖期
        reqGesture = false;
        break;
      }
      gestureBlockUntilMs = 0;
      if (autoWaitLevel) {
        if (fs.gestureEnable || autoStartUsed) {
          autoWaitLevel = false;   // 改成手勢啟動,或手動輸出用掉了自動倒數
        } else {
          // 安全開關按過就記住;飛機放平維持 1 秒(開關按下前就放平也算)才倒數
          latchArm(in);
          if (armWaitExpired(in, dt)) {
            // 等開關超過上限:不再等,這次通電不再自動倒數(和取消一樣,要飛請拔電再接電)
            eventLog(EV_ARM_SWITCH, 4, armWaitLimitS(in));
            autoWaitLevel = false;
            autoStartUsed = true;
            endReason = END_ARM_TIMEOUT;
            break;
          }
          const bool levelOk = !in.imuOk || withinStartLevel(in);
          levelHoldS = levelOk ? levelHoldS + dt : 0;
          if (armLatched && levelHoldS >= AUTO_LEVEL_HOLD_S) {
            autoWaitLevel = false;
            tryStart(true, in);
            break;
          }
        }
      }
      if (fs.gestureEnable) {
        // 撞擊斷電後推飛機不算手勢(GG 2026-09-14 安全審查 A3):撞機後撿飛機,拉線,扶正時很容易推到門檻.
        // 要再飛:網頁「開始起飛程序」(兩下確認,一定是人刻意操作)或重新上電. 推到時記拒絕原因 9(最多 5 秒一筆).
        const bool crashLock = state == FS_DONE && endReason == END_CRASH;
        const bool physPush = in.imuOk && in.pushG >= fs.gestureG;
        if (crashLock && physPush && !reqGesture && now - lastGestureMs >= GESTURE_REARM_MS) {
          lastGestureMs = now;
          rejectReason = REJECT_CRASH_LOCK;
          rejectMs = now ? now : 1;
          if (!lastCrashLockLogMs || now - lastCrashLockLogMs >= TILT_LOG_INTERVAL_MS) {
            lastCrashLockLogMs = now ? now : 1;
            eventLog(EV_REJECT, REJECT_CRASH_LOCK, in.pushG);
          }
        }
        // 推力夠就算有推(不管角度),角度超過就拒絕並記原因;序列埠模擬手勢與網頁開始按鈕也一樣檢查角度
        const bool pushed = reqGesture || (physPush && !crashLock);
        if (pushed && now - lastGestureMs >= GESTURE_REARM_MS) {
          lastGestureMs = now;
          if (in.imuOk && !withinStartLevel(in)) {
            rejectTilt(REJECT_TILT, in);
          } else {
            eventLog(EV_GESTURE, reqGesture ? reqGestureSource : GESTURE_SRC_PUSH, in.pushG);   // arg:0 推飛機 / 1 序列埠 / 2 網頁按鈕
            tryStart(false, in);
          }
        }
      }
      reqGesture = false;
      break;

    case FS_WAIT_STILL:
      if (!in.imuOk) {
        reject(REJECT_IMU);
        endReason = END_CANCELED;
        enter(FS_STANDBY);
        break;
      }
      latchArm(in);
      if (armWaitExpired(in, dt)) {
        // 起飛程序開始後超過等待上限還沒按安全開關:取消回待機(設定解鎖). 要飛再推一下或按網頁開始.
        eventLog(EV_ARM_SWITCH, 3, armWaitLimitS(in));
        endReason = END_ARM_TIMEOUT;
        enter(FS_STANDBY);
        break;
      }
      if (settleS >= SETTLE_REQUIRED_S) {
        if (!armLatched) {
          // 已放穩,等安全開關按下才開始倒數(r19). 按開關碰動飛機的話,重新放穩 1 秒後開始.
          if (!armWaitLogged) {
            armWaitLogged = true;
            eventLog(EV_ARM_SWITCH, 0);
          }
          break;
        }
        if (!resumeCountdown) countdownRemain = fs.countdownSec;
        else if (pendingAction == DISTURB_ACT_EXTEND)
          countdownRemain = min(countdownRemain + fs.extendSec, fs.countdownSec + COUNTDOWN_EXTEND_LIMIT_S);
        else if (pendingAction == DISTURB_ACT_RESET) countdownRemain = fs.countdownSec;
        // 繼續倒數時 b = 剛才外力的最大值
        eventLog(EV_COUNTDOWN, resumeCountdown ? (uint8_t)pendingAction : 0, countdownRemain, resumeCountdown ? lastDisturbG : 0);
        resumeCountdown = false;
        pendingAction = DISTURB_ACT_NONE;
        captureSettleRef();
        enter(FS_COUNTDOWN);
      }
      break;

    case FS_COUNTDOWN:
      if (!in.imuOk) {
        // 倒數中感測器壞了:撞擊斷電與觸地判斷都失效,不啟動馬達.
        reject(REJECT_IMU);
        endReason = END_CANCELED;
        enter(FS_STANDBY);
        break;
      }
      // 序列埠測試用:模擬一次外力介入(數值記成剛好門檻)
      if (reqDisturb && fs.disturbMode != DISTURB_OFF) {
        reqDisturb = false;
        lastDisturbAction = fs.disturbMode == DISTURB_EXTEND ? DISTURB_ACT_EXTEND : DISTURB_ACT_RESET;
        lastDisturbG = fs.disturbG;
        lastDisturbMs = now;
        eventLog(EV_DISTURB, lastDisturbAction, lastDisturbG, fs.disturbG);
        pendingAction = lastDisturbAction;
        resumeCountdown = true;
        enter(FS_WAIT_STILL);
        break;
      }
      if (fs.disturbMode != DISTURB_OFF && disturbedNow) {
        lastDisturbAction = fs.disturbMode == DISTURB_EXTEND ? DISTURB_ACT_EXTEND : DISTURB_ACT_RESET;
        lastDisturbG = settleDev;
        lastDisturbMs = now;
        eventLog(EV_DISTURB, lastDisturbAction, settleDev, fs.disturbG);
        pendingAction = lastDisturbAction;
        resumeCountdown = true;
        enter(FS_WAIT_STILL);
        break;
      }
      countdownRemain -= dt;
      if (countdownRemain <= 0) {
        countdownRemain = 0;
        motorStartMs = now;
        phase = 1;
        enter(FS_TAKEOFF);
        eventLog(EV_MOTOR_START, fpIndex, fp.phase1Pct);
      }
      break;

    default:
      break;
  }

  // 放穩計時(倒數判斷外力之後才更新參考,否則外力那一拍的變化會被當成新參考吃掉)
  if (disturbedNow) captureSettleRef();
  else settleS += dt;
  // 待機類狀態:參考約 1 秒緩慢跟隨目前讀值,設定頁顯示的就是「剛才晃了多少」,而不是跟很久以前比的累積差.
  // 等待放穩與倒數中參考固定不動(外力判斷要看的正是相對放穩那一刻的變化).
  if (state == FS_ARMING || state == FS_STANDBY || state == FS_DONE) {
    const float kr = dt / 1.0f;
    for (uint8_t i = 0; i < 3; ++i) {
      settleRef[i] += (accLpf[i] - settleRef[i]) * kr;
      magRef[i] += (accLpf[i] - magRef[i]) * kr;
    }
  }

  // --- 馬達運轉中的油門 ---
  if (motorState(state)) {
    const float t = (now - motorStartMs) / 1000.0f;
    const float v = 2.0f * PI * fs.lineLengthM / fs.lapSec;

    if (state == FS_TAKEOFF || state == FS_FLYING) {
      const uint8_t prevPhase = phase;
      const float base = baseThrottle(t, phase);
      if (prevPhase == 1 && phase == 2) eventLog(EV_PHASE2, 0, t);
      float comp = 0;
      float pct;
      if (t < fp.takeoffRampSec) {
        // 緩啟動:從 0 慢慢加到當下的基本油門. 還沒到位前不夾下限(夾了會一開始就跳到下限).
        pct = min(base * t / fp.takeoffRampSec, (float)fp.maxPct);
      } else {
        if (state == FS_TAKEOFF) enter(FS_FLYING);
        // 感測器故障時不補償,只照時間軸(規格第 5 節)
        // 兩段飛行共用同一條補償曲線(第二段只是基本油門較高,補償後可能被上限夾住)
        if (in.imuOk && t >= fp.noCompSec) comp = curveCompPct(fp, in.pitchDeg);
        // 下限至少 THROTTLE_FLOOR_PCT(安全審查 B4):設定範圍已經擋住,這裡再保底一次,補償再怎麼減也不會掉到沒動力
        const float floorPct = max((float)fp.minPct, (float)THROTTLE_FLOOR_PCT);
        pct = constrain(base + comp, floorPct, max(floorPct, (float)fp.maxPct));
      }
      lastBase = base;
      lastComp = comp;
      lastOut = pct;
      out.speedMps = v * min(1.0f, t / max(SPEED_RAMP_MIN_S, fp.takeoffRampSec));

      // 開始降落:總時間到,或觸地提早降落(正飛水平 + Z 軸持續抖動)
      if (state == FS_FLYING) {
        LandingCause cause = LAND_NONE;
        if (t >= fp.flightSec) cause = LAND_TIME;
        else if (fs.earlyLandEnable && t >= fs.earlyLandArmSec && in.rollHoldS >= fs.earlyLandHoldSec) cause = LAND_EARLY_ROLL;
        if (cause != LAND_NONE) {
          landingCause = cause;
          landingStartPct = pct;
          landingElapsed = 0;
          landStillS = 0;
          memcpy(landAccRef, accLpf, sizeof(landAccRef));
          enter(FS_LANDING);
          eventLog(EV_LAND_START, cause, t, in.rollHoldS);
        }
      }
    }

    if (state == FS_LANDING) {
      landingElapsed += dt;
      const float r = fp.landingRampSec > 0 ? min(1.0f, landingElapsed / fp.landingRampSec) : 1.0f;
      const float pct = landingStartPct + (fp.landingPct - landingStartPct) * r;
      lastBase = pct;
      lastComp = 0;   // 降落中不補償
      lastOut = pct;
      out.speedMps = landingStartPct > 1 ? v * pct / landingStartPct : 0;

      if (in.imuOk) {
        if (gyroLpfMag < LAND_STILL_GYRO_DPS && dist3(accLpf, landAccRef) < LAND_STILL_ACC_G) {
          landStillS += dt;
        } else {
          landStillS = 0;
          memcpy(landAccRef, accLpf, sizeof(landAccRef));
        }
      }
      // 觸地判斷等減力秒數走完才開始:提早降落觸發當下飛機正貼地彈跳,
      // 若立刻判斷會馬上關馬達,就不是「開始降落程序」了.
      if (landingElapsed >= fp.landingRampSec) {
        if (in.imuOk && in.spikeG >= fs.touchdownG) finish(END_TOUCH_SPIKE, in.spikeG, fs.touchdownG);
        else if (in.imuOk && landStillS >= fs.touchdownStillSec) finish(END_TOUCH_STILL, landStillS, fs.touchdownStillSec);
        else if (in.imuOk && in.rollHoldS >= fs.earlyLandHoldSec) finish(END_TOUCH_ROLL, in.rollHoldS, fs.earlyLandHoldSec);
      }
      // 保險時間從減力走完才開始算(GG 2026-09-14):降落最長 = 減力秒數 + 保險時間.
      // 原本從開始降落算,減力 20 秒 + 保險 20 秒時減力一走完就關馬達,完全沒有等觸地的時間.
      const float landingLimitS = fp.landingRampSec + fs.landingTimeoutSec;
      if (state == FS_LANDING && landingElapsed >= landingLimitS)
        finish(END_LANDING_TIMEOUT, landingElapsed, landingLimitS);
    }
  }

  // --- 機輪收腳(GG 2026-09-13):馬達啟動 N 秒後收;降落減力一開始,馬達停止(含撞擊,緊急停止),待機一律放下.
  // 觸地提早降落開啟時不收:不知道使用者什麼時候要貼地滑行提早降落,輪子必須一直放著.
  const bool gearUp = fs.gearEnable && !fs.earlyLandEnable && (state == FS_TAKEOFF || state == FS_FLYING) &&
                      (now - motorStartMs) >= (uint32_t)fs.gearRetractSec * 1000UL;
  if (gearUp != lastGearUp) {
    eventLog(EV_GEAR, gearUp ? 1 : 0, motorState(state) || state == FS_DONE ? (now - motorStartMs) / 1000.0f : 0);
    lastGearUp = gearUp;
  }
  out.gearUp = gearUp;

  if (motorState(state)) {
    out.motorOn = true;
    out.throttlePct = lastOut;
    out.inFlight = true;
  } else {
    out.motorOn = false;
    out.throttlePct = 0;
    if (state != FS_DONE) lastOut = 0;
  }

  // --- 狀態快照 ---
  portENTER_CRITICAL(&statusLock);
  status.state = state;
  status.stateSeconds = (now - stateStartMs) / 1000.0f;
  status.countdownRemainS = countdownRemain;
  status.flightSeconds = motorState(state) ? (now - motorStartMs) / 1000.0f
                        : (state == FS_DONE && motorStopMs > motorStartMs ? (motorStopMs - motorStartMs) / 1000.0f : 0);
  status.basePct = motorState(state) ? lastBase : 0;
  status.compPct = motorState(state) ? lastComp : 0;
  status.outPct = motorState(state) ? lastOut : 0;
  status.phase = phase;
  status.landingCause = landingCause;
  status.endReason = endReason;
  status.rejectReason = rejectReason;
  status.rejectAgeMs = rejectMs ? now - rejectMs : UINT32_MAX;
  status.disturbAction = lastDisturbAction;
  status.disturbG = lastDisturbG;
  status.disturbAgeMs = lastDisturbMs ? now - lastDisturbMs : UINT32_MAX;
  status.gestureEnabled = fs.gestureEnable;
  status.autoStartUsed = autoStartUsed;
  status.flightProfile = fpIndex;
  status.settleSeconds = settleS;
  status.distG = distMag;
  status.distPeakG = distPeakG;
  status.distOverAgeMs = distOverMs ? now - distOverMs : UINT32_MAX;
  status.twistDeg = (state == FS_WAIT_STILL || state == FS_COUNTDOWN) && gestureStarted ? twistDeg : 0;
  status.autoWaitLevel = autoWaitLevel;
  status.armSwitch = in.armSwitch;
  status.armLatched = armLatched && (state == FS_WAIT_STILL || state == FS_COUNTDOWN || autoWaitLevel);
  status.armWaitLeftS = !armLatched && (state == FS_WAIT_STILL || (state == FS_STANDBY && autoWaitLevel))
                            ? max(0.0f, armWaitLimitS(in) - armWaitS) : -1.0f;
  status.gestureBlockS =
      gestureBlockUntilMs && (int32_t)(now - gestureBlockUntilMs) < 0 ? (gestureBlockUntilMs - now) / 1000.0f : 0;
  portEXIT_CRITICAL(&statusLock);
  return out;
}

void flightGetStatus(FlightStatus &o) {
  portENTER_CRITICAL(&statusLock);
  o = status;
  portEXIT_CRITICAL(&statusLock);
}

const SharedSettings &flightShared() { return fs; }

uint8_t flightLedPattern(uint32_t now, bool imuFault) {
  if (rejectMs && now - rejectMs < REJECT_FLASH_MS) return (now / 50) % 2;   // 拒絕啟動:急閃 1 秒
  if (imuFault && !motorState(state)) return (now / 40) % 2;                 // 感測器故障:極快閃
  switch (state) {
    case FS_ARMING: return 0;
    case FS_STANDBY: return autoWaitLevel ? (now % 1000) < 500 : 1;   // 上電自動倒數等安全開關或放平:慢閃(和等待放穩一樣是等待中)
    case FS_WAIT_STILL: return (now % 1000) < 500;   // 慢閃
    case FS_COUNTDOWN: return (now % 250) < 125;     // 快閃
    case FS_DONE: {
      // 閃 n 下停一下:撞擊 3 下,其他結束 2 下
      const uint8_t n = endReason == END_CRASH ? 3 : 2;
      const uint32_t p = now % 2000;
      return p < (uint32_t)n * 300 && (p % 300) < 150;
    }
    default: return 0;                                // 飛行中熄滅
  }
}

void flightRequestCancel() { reqCancel = true; }
void flightRequestEstop() { reqEstop = true; }
void flightRequestGesture(uint8_t source) {
  reqGestureSource = source;
  reqGesture = true;
}
void flightRequestDisturb() { if (state == FS_COUNTDOWN) reqDisturb = true; }
void flightRequestTwist() { reqTwist = true; }
void flightRequestTilt() { reqTilt = true; }

bool flightSettingsLocked() {
  const FlightState s = state;
  return s == FS_WAIT_STILL || s == FS_COUNTDOWN || motorState(s);
}

bool flightOtaAllowed() {
  const FlightState s = state;
  return s == FS_ARMING || s == FS_STANDBY || s == FS_DONE;
}
