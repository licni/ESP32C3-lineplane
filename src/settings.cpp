// 版本流水號: r25 (2026-09-15) 「測試」組(PROFILE_TEST_INDEX)名稱鎖定:改名回 namelocked,備份碼套用略過這組名稱
// 舊: r24 (2026-09-15) 版面 v10:風格尾端加起飛油門 takeoffPct(10~100)與持續時間 takeoffHold(0~30 秒,0 = 不使用);
//   讀 v4~v9 風格尾端補「不使用」(起飛油門 = 第一段油門),共用設定 v9 版面相同照讀;交叉驗證 takeofftime
// 舊: r23 (2026-09-14) 參數 armSwitchOff 忽略安全開關(0/1,出廠 0,用 v9 預留位元組)
// 舊: r22 (2026-09-14) 出廠值改成 GG 的基準設定(共用 14 項,A 組與第 6 組「測試」的飛法與曲線,第 6 組名稱 TEST → 測試,出廠飛行風格第 6 組)
// 舊: r21 (2026-09-14) 曲線點補償值範圍 ±50 → ±100(GG:基本油門 70% 時只能拉到 20%,要能降到總油門 10%;int8 放得下,版面不變)
// 舊: r20 (2026-09-14) 版面 v9:共用設定尾端加蜂鳴器電位 buzzerLow(0 高電位響 / 1 低電位響);讀 v8 共用設定尾端補預設,風格讀 v4/v6~v9
// 舊: r19 (2026-09-14) 設定備份碼:整份設定 SettingsImage 的讀寫驗證套用;備份碼套用的飛行風格 pendingActive 按儲存才寫入,放棄變更還原
// 舊: r18 (2026-09-14) 加安全開關等待上限 armWait(1~30 分鐘,預設 3,用收腳區塊預留位元組,舊存檔讀到 0 補 3);
//   電變校正最高油門保持出廠 2 → 4 秒(GG:電變自己開機要約 1 秒,4~5 秒剛好等電變開機又不會進設定模式)
// 舊: r17 (2026-09-14) 飛行中油門下限範圍 10~100(安全審查 B4),舊存檔 0~9 載入時補到 10
// 舊: r16 (2026-09-14) 數值文字要整串是數字(「12abc」拒絕,原本會收成 12);風格名稱要是合法 UTF-8 且無控制字元
// 舊: r15 (2026-09-13) 收輪舵機行程預設改小行程 1400~1600µs(GG:避免還沒搞清楚方向就撞壞)
// 舊: r14 (2026-09-13) 版面 v8:機輪收腳 6 個參數(行程下限<上限-100);讀 v7 共用設定尾端補預設,風格讀 v4/v6/v7/v8
// 舊: r13 (2026-09-13) 加起飛前水平限制 startLevel(10~90,預設 35;舊存檔讀到 0 補 35)
// 舊: r12 (2026-09-13) 參數加 escRpm(轉速回傳)與 motorPoles(用 v7 預留位元組)
// 舊: r11 (2026-09-13) 版面 v7:共用設定尾端加扭轉取消起飛兩項,讀 v4~v6 較短的共用設定補預設;風格讀 v4/v6/v7
// 舊: r10 (2026-09-13) 加 escPwmHz(50~400Hz,週期至少比 100% 脈寬多 300µs);舊存檔讀到 0 補 50
// 舊: r9 (2026-09-13) 參數表加 escProtocol(結構早已預留,版面不變)
// 舊: r8 (2026-09-13) 可調點數改 1~4,舊存檔 5 點載入時拿掉最不影響形狀的一點
// 舊: r7 (2026-09-13) 刪除第二段曲線(兩段共用一條),轉移可讀 v4/v5/v6
// 舊: r6 (2026-09-13) 第二段獨立補償曲線(參數 p2upDb/p2up1a...),複製第一段曲線到第二段
// 舊: r5 (2026-09-13) 寫入加鎖,起飛快照 settingsSnapshotForFlight(),控制工作每拍複製共用設定
// 舊: r4 (2026-09-13) 啟動手勢開關,手勢力道下限 0.5g
// 舊: r3 (2026-09-13) 換段三種方式;提早降落改為地面滑行抖動判斷的三個參數
// 舊: r2 (2026-09-13) 加觸地提早降落三項,換段方式(線性/階梯)
// 舊: r1 (2026-09-13) 初版:共用設定 + 六組風格(A~E,TEST),參數表驅動的驗證,NVS 分塊存檔
#include "settings.h"
#include <Preferences.h>
#include "imu.h"

static const char *const PREF_NAMESPACE = "lpcfg";
static const uint32_t BLOB_MAGIC = 0x4C504346;   // "LPCF"

SharedSettings sharedSettings;
ProfileSettings profiles[PROFILE_COUNT];
uint8_t activeProfile = DEFAULT_ACTIVE_PROFILE;
// 備份碼套用的飛行風格:和其他設定一樣按儲存才寫入,放棄變更就不改(-1 = 沒有). 直接選用風格仍立即存檔.
static int8_t pendingActive = -1;

// 控制工作(優先權最高)隨時可能在 loop 改設定改到一半時插進來讀. 所有整塊改寫與控制工作的讀取都包在這把鎖裡,
// 臨界區只有幾十到幾百位元組的複製,微秒等級.
static portMUX_TYPE settingsLock = portMUX_INITIALIZER_UNLOCKED;
#define LOCKED(stmt) do { portENTER_CRITICAL(&settingsLock); stmt; portEXIT_CRITICAL(&settingsLock); } while (0)

// escPwmHz 占用原本 reserved1[3] 的後兩個位元組:位置與結構大小必須沒變,舊存檔才讀得回來
static_assert(offsetof(SharedSettings, escPwmHz) == offsetof(SharedSettings, gestureEnable) + 2, "SharedSettings layout");
// v4~v6 的共用設定到 escPwmHz 為止;v7 在尾端加欄位,舊存檔長度就是 twistCancelDeg 的位置
static const size_t SHARED_V6_SIZE = offsetof(SharedSettings, twistCancelDeg);
static_assert(SHARED_V6_SIZE == offsetof(SharedSettings, gestureEnable) + 4, "SharedSettings v6 size");
static const size_t SHARED_V7_SIZE = offsetof(SharedSettings, gearEnable);
static_assert(SHARED_V7_SIZE == SHARED_V6_SIZE + 4, "SharedSettings v7 size");
static const size_t SHARED_V8_SIZE = offsetof(SharedSettings, buzzerActiveLow);
static_assert(SHARED_V8_SIZE == SHARED_V7_SIZE + 12, "SharedSettings v8 size");
static_assert(sizeof(SharedSettings) == SHARED_V8_SIZE + 4, "SharedSettings v9 size");
// armWaitMin 占用 v8 收腳區塊的預留位元組:位置不可移動
static_assert(offsetof(SharedSettings, armWaitMin) == offsetof(SharedSettings, gearRetractSec) + 1, "SharedSettings armWaitMin");
// 風格 v4,v6~v9 的長度到 takeoffPct 為止;v10 在尾端加起飛油門 8 位元組
static const size_t PROFILE_V9_SIZE = offsetof(ProfileSettings, takeoffPct);
static_assert(sizeof(ProfileSettings) == PROFILE_V9_SIZE + 8, "ProfileSettings v10 size");

static SharedSettings savedShared;
static ProfileSettings savedProfiles[PROFILE_COUNT];

// --- 出廠預設 --------------------------------------------------------------------
static void defaultShared(SharedSettings &s) {
  memset(&s, 0, sizeof(s));
  s.noseAxis = IMU_AXIS_PX;
  s.upAxis = IMU_AXIS_PZ;
  s.noseRight = 0;
  s.escProtocol = ESC_PROTO_PWM50;
  s.pitchTrimDeg = 0;
  s.escMinUs = 1000;
  s.escMaxUs = 2000;
  // 出廠值 = GG 的基準設定(2026-09-14,test_logs/基準設定碼.txt 那組備份碼). 括號是改之前的出廠值.
  s.escPwmHz = 100;        // (50)
  s.gestureEnable = 1;
  s.startLevelDeg = 35;    // 原本手勢寫死的「機身大致水平」35 度
  s.gestureG = 1.0f;       // (2.0)
  s.countdownSec = 20;
  s.disturbMode = DISTURB_EXTEND;
  s.extendSec = 5;
  s.crashEnable = 0;       // (1)
  s.disturbG = 0.05f;      // (0.15)
  s.touchdownG = 3.0f;
  s.touchdownStillSec = 1.0f;
  s.landingTimeoutSec = 20;
  s.crashG = 15.0f;        // (14)
  s.lineLengthM = 18.0f;
  s.lapSec = 4.0f;         // (5.2)
  // 電變校正最高油門保持:控制器開機很快,電變自己開機要約 1 秒,太短電變還沒記住最高點就切到最低;
  // 太久有些電變會進設定模式(多數廠牌說明 3~6 秒,ZTW 3~4 秒).
  s.calibHoldSec = 3.0f;   // (4)
  // 觸地提早降落預設關閉:門檻要看紀錄頁的實飛抖動數值才訂得準. 模擬(tools/sim_impact.py)
  // 特技中水平時抖動最大 1.04g 但撐不過 1 秒,地面滑行約 3.8 秒觸發.
  s.earlyLandEnable = 0;
  s.earlyLandArmSec = 10;
  s.earlyLandTiltDeg = 20;
  s.earlyLandVibG = 1.0f;  // (0.8)
  s.earlyLandHoldSec = 0.7f;   // (1.0)
  s.twistCancelDeg = 15;   // (45) 扭轉機尾取消起飛的角度
  s.twistBlockSec = 5;
  s.armWaitMin = ARM_WAIT_DEFAULT_MIN;   // (3)
  s.escRpmTelemetry = 1;   // (0) 只在 DShot300 作用;不支援雙向訊號的電變可能不解鎖
  s.motorPoles = 14;       // Betaflight 預設
  // 機輪收腳:預設關閉(沒裝收腳的飛機不受影響). 行程預設只開 1400~1600µs 小行程(GG):
  // 還沒搞清楚舵機方向與收腳機構的極限前,全行程 1000~2000 可能頂死撞壞東西,確認後再慢慢加大.
  s.gearEnable = 0;
  s.gearReverse = 0;
  s.gearMinUs = 1400;
  s.gearMaxUs = 1600;
  s.gearRetractSec = 15;   // (5)
  s.gearTravelSec = 0.7f;  // (2.0)
  s.buzzerActiveLow = 0;   // GG 的蜂鳴器是高電位響
  s.armSwitchOff = 0;      // 出廠一定要按安全開關才倒數
}

// 第 6 組出廠名稱「測試」(原本 TEST). 備份碼的「沿用出廠名稱」用的是 settings_backup.cpp 自己凍結的舊名稱表.
static const char *const PROFILE_DEFAULT_NAMES[PROFILE_COUNT] = {"A", "B", "C", "D", "E", "測試"};

static void setSide(CurveSide &s, int8_t deadband, uint8_t count, const CurvePoint pts[4]) {
  s.deadband = deadband;
  s.count = count;
  for (uint8_t i = 0; i < 4; ++i) s.pts[i] = pts[i];
  s.pts[4] = pts[3];   // 第 5 格不再使用
}

static void defaultProfile(ProfileSettings &p, uint8_t index) {
  memset(&p, 0, sizeof(p));
  strncpy(p.name, PROFILE_DEFAULT_NAMES[index], sizeof(p.name) - 1);
  // 出廠值 = GG 的基準設定:B~E 組是原本的出廠值;A 組與第 6 組「測試」是 GG 調過的值(在下面蓋掉)
  p.phase1Pct = 75;
  p.phase2Pct = 85;
  p.minPct = 30;
  p.maxPct = 100;
  p.phase1Sec = 135;
  p.flightSec = 300;
  p.takeoffRampSec = 2.0f;
  p.phaseRampSec = 3.0f;
  p.noCompSec = 3.0f;
  p.landingRampSec = 5.0f;
  p.landingPct = 30;
  p.phaseMode = PHASE_STEP_RAMP;
  p.up.deadband = 20;
  p.up.count = 3;
  p.up.pts[0] = {45, 8};
  p.up.pts[1] = {70, 15};
  p.up.pts[2] = {90, 20};
  p.up.pts[3] = {90, 20};
  p.up.pts[4] = {90, 20};
  p.down.deadband = -3;
  p.down.count = 3;
  p.down.pts[0] = {-30, -10};
  p.down.pts[1] = {-60, -20};
  p.down.pts[2] = {-90, -25};
  p.down.pts[3] = {-90, -25};
  p.down.pts[4] = {-90, -25};
  if (index == 0) {   // A
    p.phase1Pct = 50;
    p.phase2Pct = 80;
    p.minPct = 20;
    p.maxPct = 90;
    p.landingRampSec = 20.0f;
    p.phaseMode = PHASE_STEP;
    const CurvePoint up[4] = {{66, 20}, {90, 35}, {90, 35}, {90, 35}};
    const CurvePoint dn[4] = {{-54, -14}, {-90, -46}, {-90, -46}, {-90, -46}};
    setSide(p.up, 20, 2, up);
    setSide(p.down, -20, 2, dn);
  } else if (index == 5) {   // 測試
    p.phase1Pct = 70;
    p.phase2Pct = 80;
    p.minPct = 10;
    p.phase1Sec = 60;
    p.flightSec = 90;
    p.noCompSec = 10.0f;
    p.landingRampSec = 20.0f;
    p.landingPct = 40;
    p.phaseMode = PHASE_SPREAD;
    const CurvePoint up[4] = {{90, 19}, {90, 20}, {90, 20}, {90, 20}};
    const CurvePoint dn[4] = {{-54, -24}, {-90, -25}, {-90, -25}, {-90, -25}};
    setSide(p.up, 29, 1, up);
    setSide(p.down, -30, 1, dn);
  }
  // 起飛油門出廠不使用(持續時間 0),飛法和加這個功能之前一樣;油門值先放第一段油門,開啟時從這裡調
  p.takeoffPct = p.phase1Pct;
  p.takeoffHoldSec = 0;
}

// --- 參數表 ----------------------------------------------------------------------
enum ParamType : uint8_t { PARAM_U8 = 0, PARAM_I8, PARAM_U16, PARAM_F32 };

struct ParamDef {
  const char *key;
  ParamType type;
  uint16_t offset;
  float minV, maxV;
  float fine, coarse;   // 網頁 +/- 的細調與粗調步進;數值也會對齊到細調步進
};

#define SP(k, t, f, mn, mx, fi, co) {k, t, (uint16_t)offsetof(SharedSettings, f), mn, mx, fi, co}
#define PP(k, t, f, mn, mx, fi, co) {k, t, (uint16_t)offsetof(ProfileSettings, f), mn, mx, fi, co}

static const ParamDef SHARED_PARAMS[] = {
    SP("noseAxis", PARAM_U8, noseAxis, 0, 5, 1, 1),
    SP("upAxis", PARAM_U8, upAxis, 0, 5, 1, 1),
    SP("noseRight", PARAM_U8, noseRight, 0, 1, 1, 1),
    SP("pitchTrim", PARAM_F32, pitchTrimDeg, -30, 30, 0.1f, 1),
    SP("escProtocol", PARAM_U8, escProtocol, 0, 2, 1, 1),   // EscProtocol,開機時套用
    SP("escPwmHz", PARAM_U16, escPwmHz, 50, 400, 10, 50),   // 開機時套用
    SP("escMinUs", PARAM_U16, escMinUs, 800, 1500, 5, 50),
    SP("escMaxUs", PARAM_U16, escMaxUs, 1500, 2200, 5, 50),
    SP("gestureEnable", PARAM_U8, gestureEnable, 0, 1, 1, 1),
    // 下限 0.5g:大飛機人手推不快(GG 實測). 越低越容易在搬運時誤觸發,用設定頁試推燈確認.
    SP("gestureG", PARAM_F32, gestureG, 0.5f, 6, 0.1f, 0.5f),
    SP("startLevel", PARAM_U8, startLevelDeg, 10, 90, 1, 5),
    SP("armWait", PARAM_U8, armWaitMin, 1, 30, 1, 5),       // 分鐘:起飛程序開始後沒按安全開關就自動取消
    SP("countdownSec", PARAM_U8, countdownSec, 5, 120, 1, 5),
    SP("disturbG", PARAM_F32, disturbG, 0.05f, 1.0f, 0.01f, 0.05f),
    SP("disturbMode", PARAM_U8, disturbMode, 0, 2, 1, 1),
    SP("extendSec", PARAM_U8, extendSec, 1, 60, 1, 5),
    SP("touchdownG", PARAM_F32, touchdownG, 1.5f, 10, 0.1f, 0.5f),
    SP("touchdownStill", PARAM_F32, touchdownStillSec, 0.5f, 5, 0.1f, 0.5f),
    SP("landingTimeout", PARAM_U8, landingTimeoutSec, 5, 120, 1, 5),
    SP("crashEnable", PARAM_U8, crashEnable, 0, 1, 1, 1),
    SP("crashG", PARAM_F32, crashG, 6, 16, 0.5f, 1),
    SP("lineLength", PARAM_F32, lineLengthM, 5, 30, 0.1f, 1),
    SP("lapSec", PARAM_F32, lapSec, 2, 10, 0.1f, 0.5f),
    SP("calibHold", PARAM_F32, calibHoldSec, 1, 10, 0.5f, 1),
    SP("earlyLand", PARAM_U8, earlyLandEnable, 0, 1, 1, 1),
    SP("earlyLandArm", PARAM_U8, earlyLandArmSec, 3, 60, 1, 5),
    SP("earlyLandTilt", PARAM_U8, earlyLandTiltDeg, 5, 45, 1, 5),
    SP("earlyLandVib", PARAM_F32, earlyLandVibG, 0.1f, 5, 0.05f, 0.2f),
    SP("earlyLandHold", PARAM_F32, earlyLandHoldSec, 0.2f, 5, 0.1f, 0.5f),
    SP("twistCancel", PARAM_U8, twistCancelDeg, 0, 180, 1, 5),   // 0 = 關閉,開啟時至少 15 度(交叉驗證)
    SP("twistBlock", PARAM_U8, twistBlockSec, 1, 30, 1, 5),
    SP("escRpm", PARAM_U8, escRpmTelemetry, 0, 1, 1, 1),        // 開機時套用,只在 DShot300 有效
    SP("motorPoles", PARAM_U8, motorPoles, 2, 60, 2, 10),
    SP("gearEnable", PARAM_U8, gearEnable, 0, 1, 1, 1),
    SP("gearReverse", PARAM_U8, gearReverse, 0, 1, 1, 1),
    SP("gearMinUs", PARAM_U16, gearMinUs, 500, 1500, 5, 50),
    SP("gearMaxUs", PARAM_U16, gearMaxUs, 1500, 2500, 5, 50),
    SP("gearRetractSec", PARAM_U8, gearRetractSec, 1, 120, 1, 5),
    SP("gearTravelSec", PARAM_F32, gearTravelSec, 0, 10, 0.1f, 0.5f),
    SP("buzzerLow", PARAM_U8, buzzerActiveLow, 0, 1, 1, 1),   // 立即生效
    SP("armSwitchOff", PARAM_U8, armSwitchOff, 0, 1, 1, 1),   // 1 = 忽略安全開關(網頁要打勾確認)
};

static const ParamDef PROFILE_PARAMS[] = {
    PP("phase1Pct", PARAM_U8, phase1Pct, 0, 100, 1, 5),
    PP("phase1Sec", PARAM_U16, phase1Sec, 10, 1200, 5, 30),
    PP("phase2Pct", PARAM_U8, phase2Pct, 0, 100, 1, 5),
    PP("flightSec", PARAM_U16, flightSec, 30, 1800, 5, 30),
    PP("takeoffRamp", PARAM_F32, takeoffRampSec, 0, 10, 0.1f, 0.5f),
    PP("takeoffPct", PARAM_U8, takeoffPct, THROTTLE_FLOOR_PCT, 100, 1, 5),
    PP("takeoffHold", PARAM_F32, takeoffHoldSec, 0, 30, 0.5f, 1),   // 0 = 不使用起飛油門
    PP("phaseRamp", PARAM_F32, phaseRampSec, 0, 30, 0.5f, 1),
    PP("noCompSec", PARAM_F32, noCompSec, 0, 30, 0.5f, 1),
    PP("minPct", PARAM_U8, minPct, THROTTLE_FLOOR_PCT, 100, 1, 5),   // 最低 10%(安全審查 B4)
    PP("maxPct", PARAM_U8, maxPct, 0, 100, 1, 5),
    PP("landingRamp", PARAM_F32, landingRampSec, 0, 30, 0.5f, 1),
    PP("landingPct", PARAM_U8, landingPct, 0, 100, 1, 5),
    PP("phaseMode", PARAM_U8, phaseMode, 0, 2, 1, 1),
    PP("upDb", PARAM_I8, up.deadband, 0, 89, 1, 5),
    PP("upN", PARAM_U8, up.count, CURVE_MIN_POINTS, CURVE_MAX_POINTS, 1, 1),
    PP("up1a", PARAM_I8, up.pts[0].angle, 1, 90, 1, 5), PP("up1p", PARAM_I8, up.pts[0].pct, -100, 100, 1, 5),
    PP("up2a", PARAM_I8, up.pts[1].angle, 1, 90, 1, 5), PP("up2p", PARAM_I8, up.pts[1].pct, -100, 100, 1, 5),
    PP("up3a", PARAM_I8, up.pts[2].angle, 1, 90, 1, 5), PP("up3p", PARAM_I8, up.pts[2].pct, -100, 100, 1, 5),
    PP("up4a", PARAM_I8, up.pts[3].angle, 1, 90, 1, 5), PP("up4p", PARAM_I8, up.pts[3].pct, -100, 100, 1, 5),
    PP("dnDb", PARAM_I8, down.deadband, -89, 0, 1, 5),
    PP("dnN", PARAM_U8, down.count, CURVE_MIN_POINTS, CURVE_MAX_POINTS, 1, 1),
    PP("dn1a", PARAM_I8, down.pts[0].angle, -90, -1, 1, 5), PP("dn1p", PARAM_I8, down.pts[0].pct, -100, 100, 1, 5),
    PP("dn2a", PARAM_I8, down.pts[1].angle, -90, -1, 1, 5), PP("dn2p", PARAM_I8, down.pts[1].pct, -100, 100, 1, 5),
    PP("dn3a", PARAM_I8, down.pts[2].angle, -90, -1, 1, 5), PP("dn3p", PARAM_I8, down.pts[2].pct, -100, 100, 1, 5),
    PP("dn4a", PARAM_I8, down.pts[3].angle, -90, -1, 1, 5), PP("dn4p", PARAM_I8, down.pts[3].pct, -100, 100, 1, 5),
};

static const size_t SHARED_PARAM_COUNT = sizeof(SHARED_PARAMS) / sizeof(SHARED_PARAMS[0]);
static const size_t PROFILE_PARAM_COUNT = sizeof(PROFILE_PARAMS) / sizeof(PROFILE_PARAMS[0]);

static float readParam(const uint8_t *base, const ParamDef &d) {
  const uint8_t *p = base + d.offset;
  switch (d.type) {
    case PARAM_U8: return *p;
    case PARAM_I8: return (int8_t)*p;
    case PARAM_U16: { uint16_t v; memcpy(&v, p, 2); return v; }
    default: { float v; memcpy(&v, p, 4); return v; }
  }
}

static void writeParam(uint8_t *base, const ParamDef &d, float v) {
  uint8_t *p = base + d.offset;
  switch (d.type) {
    case PARAM_U8: *p = (uint8_t)lroundf(v); break;
    case PARAM_I8: *p = (uint8_t)(int8_t)lroundf(v); break;
    case PARAM_U16: { const uint16_t x = (uint16_t)lroundf(v); memcpy(p, &x, 2); break; }
    default: memcpy(p, &v, 4); break;
  }
}

static const ParamDef *findParam(const ParamDef *table, size_t count, const char *key) {
  for (size_t i = 0; i < count; ++i)
    if (strcmp(table[i].key, key) == 0) return &table[i];
  return nullptr;
}

// --- 補償曲線 --------------------------------------------------------------------
static float sideCompPct(const CurveSide &s, float pitch, bool upSide) {
  // 朝上:角度由小到大;朝下:角度由大到小(-3 → -90). 統一換成「離水平越遠越大」的距離來算.
  const float sign = upSide ? 1.0f : -1.0f;
  const float x = pitch * sign;
  float prevA = s.deadband * sign, prevP = 0;
  if (x <= prevA) return 0;
  for (uint8_t i = 0; i < s.count && i < CURVE_MAX_POINTS; ++i) {
    const float a = s.pts[i].angle * sign, p = s.pts[i].pct;
    if (x <= a) return a > prevA ? prevP + (p - prevP) * (x - prevA) / (a - prevA) : p;
    prevA = a;
    prevP = p;
  }
  return prevP;   // 超過最後一點:維持最後一點的值
}

float curveCompPct(const ProfileSettings &p, float pitchDeg) {
  return pitchDeg >= 0 ? sideCompPct(p.up, pitchDeg, true) : sideCompPct(p.down, pitchDeg, false);
}

uint16_t pctToUs(float pct) {
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return (uint16_t)lroundf(sharedSettings.escMinUs + (sharedSettings.escMaxUs - sharedSettings.escMinUs) * pct / 100.0f);
}

// 點數改變時把各點重新平均分布在死區到 ±90 度之間,補償值沿用舊曲線在新位置的值,
// 曲線形狀大致不變,也保證角度一定由小到大.
static void respaceSide(CurveSide &s, bool upSide, uint8_t newCount) {
  const CurveSide old = s;
  const float sign = upSide ? 1.0f : -1.0f;
  const float start = s.deadband * sign;
  const float span = 90.0f - start;
  s.count = newCount;
  for (uint8_t i = 0; i < CURVE_STORE_POINTS; ++i) {
    const uint8_t k = i < newCount ? i + 1 : newCount;
    const float dist = start + span * k / newCount;
    int8_t angle = (int8_t)lroundf(dist * sign);
    s.pts[i].angle = angle;
    s.pts[i].pct = (int8_t)lroundf(sideCompPct(old, angle, upSide));
  }
}

// --- 交叉驗證 --------------------------------------------------------------------
static const char *validateShared(const SharedSettings &s) {
  if (s.noseAxis / 2 == s.upAxis / 2) return "axis";
  if (s.escMaxUs < s.escMinUs + 100) return "escrange";
  // 週期要比最長脈寬多留 300µs 低電位,電變才分得出一個個脈衝(400Hz 週期 2500µs 配 2200µs 剛好)
  if (s.escPwmHz < 50 || 1000000UL / s.escPwmHz < (uint32_t)s.escMaxUs + 300) return "pwmhz";
  // 太小的角度放飛機時稍微轉一下就取消,不合理
  if (s.twistCancelDeg != 0 && s.twistCancelDeg < 15) return "twistdeg";
  if (s.gearMaxUs < s.gearMinUs + 100) return "gearrange";
  return nullptr;
}

// 舊存檔的點數超過上限時(以前可設 5 點),逐次拿掉「去掉後與原曲線差最少」的點:
// 用前後鄰點直線內插,看這點偏離多少. 最後一點不拿,保留曲線延伸到最遠角度的補償值.
static bool trimSide(CurveSide &s, bool upSide) {
  if (s.count <= CURVE_MAX_POINTS) return false;
  if (s.count > CURVE_STORE_POINTS) s.count = CURVE_STORE_POINTS;
  const float sign = upSide ? 1.0f : -1.0f;
  while (s.count > CURVE_MAX_POINTS) {
    uint8_t best = 0;
    float bestErr = 1e9f;
    for (uint8_t j = 0; j + 1 < s.count; ++j) {
      const float pa = j ? s.pts[j - 1].angle * sign : s.deadband * sign, pp = j ? s.pts[j - 1].pct : 0;
      const float na = s.pts[j + 1].angle * sign, np = s.pts[j + 1].pct;
      const float a = s.pts[j].angle * sign;
      const float line = na > pa ? pp + (np - pp) * (a - pa) / (na - pa) : np;
      const float err = fabsf(s.pts[j].pct - line);
      if (err < bestErr) { bestErr = err; best = j; }
    }
    for (uint8_t j = best; j + 1 < CURVE_STORE_POINTS; ++j) s.pts[j] = s.pts[j + 1];
    --s.count;
  }
  for (uint8_t j = s.count; j < CURVE_STORE_POINTS; ++j) s.pts[j] = s.pts[s.count - 1];
  return true;
}

static const char *validateSide(const CurveSide &s, bool upSide) {
  if (s.count < CURVE_MIN_POINTS || s.count > CURVE_MAX_POINTS) return "range";
  const int sign = upSide ? 1 : -1;
  int prev = s.deadband * sign;
  for (uint8_t i = 0; i < s.count; ++i) {
    const int a = s.pts[i].angle * sign;
    if (a <= prev || a > 90) return "order";
    prev = a;
  }
  return nullptr;
}

static const char *validateProfile(const ProfileSettings &p) {
  if (p.minPct >= p.maxPct) return "minmax";
  if (p.phase1Sec >= p.flightSec) return "phasetime";
  // 起飛油門(含換回第一段的過渡)要在第一段時間內結束,不然會蓋到換段
  if (p.takeoffHoldSec > 0 && p.takeoffRampSec + p.takeoffHoldSec + TAKEOFF_BLEND_S > p.phase1Sec) return "takeofftime";
  if (const char *e = validateSide(p.up, true)) return e;
  if (const char *e = validateSide(p.down, false)) return e;
  return nullptr;
}

// --- 存取 ------------------------------------------------------------------------
struct BlobHeader {
  uint32_t magic;
  uint16_t version;
  uint16_t size;
};

// 讀一塊,不限版本:回傳存檔時的版本與長度,原始資料放進 data(長度不可超過 capacity).
// 由呼叫端決定這個版本能不能轉移 —— 改版時不必讓使用者調好的設定全部回預設.
static bool loadBlobAny(Preferences &prefs, const char *key, uint8_t *data, size_t capacity, uint16_t &version,
                        uint16_t &size) {
  if (!prefs.isKey(key)) return false;
  const size_t len = prefs.getBytesLength(key);
  uint8_t buf[512];
  if (len < sizeof(BlobHeader) || len > sizeof(buf) || prefs.getBytes(key, buf, len) != len) return false;
  BlobHeader h;
  memcpy(&h, buf, sizeof(h));
  if (h.magic != BLOB_MAGIC || h.size != len - sizeof(h) || h.size > capacity) return false;
  version = h.version;
  size = h.size;
  memcpy(data, buf + sizeof(h), h.size);
  return true;
}

// 版面沿革(共用設定 v4~v6 都沒變;風格結構只在尾端增減,前面欄位位置從未變動):
//   v4:風格尾端是一條補償曲線(up/down)
//   v5:尾端多了第二段曲線 up2/down2(2026-09-13 加)
//   v6:又刪掉第二段曲線(GG:兩段分開不好設定且易混淆),版面回到與 v4 相同
//   v7:共用設定尾端加扭轉機尾取消起飛(角度,封鎖秒數)+ 2 預留;風格不變
//   v8:共用設定尾端加機輪收腳 12 位元組;風格不變
//   v9:共用設定尾端加蜂鳴器電位 + 3 預留;風格不變
//   v10:風格尾端加起飛油門(油門 + 3 預留 + 持續時間);共用設定不變
// 所以風格 v4/v6~v9 原樣沿用後尾端補「不使用」,v5 取前段;共用設定 v4~v6 較短,尾端補預設. GG 已經在板子上調好參數,改版不可洗掉.
static const size_t CURVE_SIDE_SIZE = sizeof(CurveSide);

static bool loadShared(Preferences &prefs, SharedSettings &out) {
  SharedSettings s;
  defaultShared(s);   // v6 以前的存檔比較短,尾端新欄位保留預設值
  uint16_t ver = 0, size = 0;
  if (!loadBlobAny(prefs, "shared", (uint8_t *)&s, sizeof(s), ver, size)) return false;
  const bool current = (ver == SETTINGS_LAYOUT_VERSION || ver == 9) && size == sizeof(s);   // v10 只改了風格
  const bool old6 = ver >= 4 && ver <= 6 && size == SHARED_V6_SIZE;
  const bool old7 = ver == 7 && size == SHARED_V7_SIZE;
  const bool old8 = ver == 8 && size == SHARED_V8_SIZE;
  if (!current && !old6 && !old7 && !old8) return false;
  if (!current) {
    // loadBlobAny 只蓋掉前 size 個位元組;保險起見尾端再設一次預設
    SharedSettings d;
    defaultShared(d);
    memcpy((uint8_t *)&s + size, (uint8_t *)&d + size, sizeof(s) - size);
  }
  if (s.escPwmHz == 0) s.escPwmHz = 50;   // 加 PWM 頻率之前的存檔,這兩個位元組是預留的 0
  if (s.motorPoles < 2) s.motorPoles = 14; // v7 早期這格是預留的 0
  if (s.startLevelDeg < 10) s.startLevelDeg = 35;   // 以前是預留位元組 0
  if (s.armWaitMin < 1 || s.armWaitMin > 30) s.armWaitMin = ARM_WAIT_DEFAULT_MIN;   // 以前是收腳區塊的預留位元組 0
  if (s.armSwitchOff > 1) s.armSwitchOff = 0;   // 預留位元組不是 0/1 時當成要按開關(安全側)
  if (validateShared(s)) return false;
  if (ver != SETTINGS_LAYOUT_VERSION) Serial.printf("settings shared migrated v%u -> v%u\n", ver, SETTINGS_LAYOUT_VERSION);
  out = s;
  return true;
}

static bool loadProfile(Preferences &prefs, const char *key, ProfileSettings &out) {
  uint8_t raw[512];
  uint16_t ver = 0, size = 0;
  if (!loadBlobAny(prefs, key, raw, sizeof(raw), ver, size)) return false;
  // 風格結構 v4,v6~v9 版面相同(v7~v9 只改了共用設定),v10 尾端多了起飛油門
  const bool current = ver == SETTINGS_LAYOUT_VERSION && size == sizeof(ProfileSettings);
  const bool old9 = (ver == 9 || ver == 8 || ver == 7 || ver == 6 || ver == 4) && size == PROFILE_V9_SIZE;
  const bool v5 = ver == 5 && size == PROFILE_V9_SIZE + 2 * CURVE_SIDE_SIZE;
  if (!current && !old9 && !v5) return false;
  ProfileSettings p;
  memcpy(&p, raw, current ? sizeof(p) : PROFILE_V9_SIZE);   // v5 多出來的第二段曲線在尾端,直接不取
  if (!current) {
    // 加起飛油門之前的存檔:不使用(飛法不變),油門值先放第一段油門
    memset(p.reserved10, 0, sizeof(p.reserved10));
    p.takeoffPct = max(p.phase1Pct, THROTTLE_FLOOR_PCT);
    p.takeoffHoldSec = 0;
  }
  if (p.takeoffPct < THROTTLE_FLOOR_PCT || p.takeoffPct > 100) p.takeoffPct = max(p.phase1Pct, THROTTLE_FLOOR_PCT);
  const bool trimmed = trimSide(p.up, true) | trimSide(p.down, false);   // 用 | 兩側都要做
  if (trimmed) Serial.printf("settings %s curve trimmed to %u points max\n", key, CURVE_MAX_POINTS);
  // 飛行中油門下限改成最低 10% 之前的存檔可能是 0~9:補到 10,其他設定照舊(不可因此整組回預設)
  if (p.minPct < THROTTLE_FLOOR_PCT) {
    Serial.printf("settings %s minPct %u -> %u\n", key, (unsigned)p.minPct, (unsigned)THROTTLE_FLOOR_PCT);
    p.minPct = THROTTLE_FLOOR_PCT;
    if (p.maxPct <= p.minPct) p.maxPct = p.minPct + 1;
  }
  if (validateProfile(p)) return false;
  if (ver != SETTINGS_LAYOUT_VERSION) Serial.printf("settings %s migrated v%u -> v%u\n", key, ver, SETTINGS_LAYOUT_VERSION);
  p.name[PROFILE_NAME_BUFFER - 1] = 0;
  out = p;
  return true;
}

static bool saveBlob(Preferences &prefs, const char *key, const uint8_t *data, size_t size) {
  uint8_t buf[512];
  const size_t total = sizeof(BlobHeader) + size;
  if (total > sizeof(buf)) return false;
  const BlobHeader h = {BLOB_MAGIC, SETTINGS_LAYOUT_VERSION, (uint16_t)size};
  memcpy(buf, &h, sizeof(h));
  memcpy(buf + sizeof(h), data, size);
  return prefs.putBytes(key, buf, total) == total;
}

static void profileKey(uint8_t i, char *out) {
  out[0] = 'p';
  out[1] = (char)('0' + i);
  out[2] = 0;
}

static void applyHardwareSettings() {
  imuSetOrientation(sharedSettings.noseAxis, sharedSettings.upAxis);
}

static void loadAll() {
  defaultShared(sharedSettings);
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) defaultProfile(profiles[i], i);
  activeProfile = DEFAULT_ACTIVE_PROFILE;
  Preferences prefs;
  if (prefs.begin(PREF_NAMESPACE, true)) {
    loadShared(prefs, sharedSettings);
    for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
      char key[3];
      profileKey(i, key);
      loadProfile(prefs, key, profiles[i]);
    }
    // 名稱鎖定之前改過名的存檔:開機一律改回「測試」(存檔裡的舊名稱不動,每次載入都蓋掉,不算未儲存變更)
    memset(profiles[PROFILE_TEST_INDEX].name, 0, PROFILE_NAME_BUFFER);
    strncpy(profiles[PROFILE_TEST_INDEX].name, PROFILE_DEFAULT_NAMES[PROFILE_TEST_INDEX], PROFILE_NAME_BUFFER - 1);
    const uint8_t a = prefs.getUChar("active", DEFAULT_ACTIVE_PROFILE);
    if (a < PROFILE_COUNT) activeProfile = a;
    prefs.end();
  }
  savedShared = sharedSettings;
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) savedProfiles[i] = profiles[i];
}

void settingsBegin() {
  loadAll();
  applyHardwareSettings();
  Serial.printf("settings loaded, active profile %u (%s)\n", (unsigned)activeProfile, profiles[activeProfile].name);
}

bool settingsSharedDirty() { return memcmp(&sharedSettings, &savedShared, sizeof(SharedSettings)) != 0; }
bool settingsProfileDirty(uint8_t i) {
  return i < PROFILE_COUNT && memcmp(&profiles[i], &savedProfiles[i], sizeof(ProfileSettings)) != 0;
}
bool settingsActiveDirty() { return pendingActive >= 0 && pendingActive != activeProfile; }
bool settingsAnyDirty() {
  if (settingsSharedDirty() || settingsActiveDirty()) return true;
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i)
    if (settingsProfileDirty(i)) return true;
  return false;
}

// 數值文字要整串都是數字(前後空白可以). strtof 遇到「12abc」會回 12 並停在 a,r14 以前因此會把 12 當成合法值收下.
static bool parseNumber(const char *text, float &out) {
  char *end = nullptr;
  const float v = strtof(text, &end);
  if (end == text || !isfinite(v)) return false;
  while (*end == ' ' || *end == '\t' || *end == '\r') ++end;
  if (*end) return false;
  out = v;
  return true;
}

const char *settingsSet(int8_t scope, const char *key, const char *valueText) {
  if (scope < -1 || scope >= PROFILE_COUNT) return "scope";
  const bool shared = scope < 0;
  const ParamDef *d = shared ? findParam(SHARED_PARAMS, SHARED_PARAM_COUNT, key)
                             : findParam(PROFILE_PARAMS, PROFILE_PARAM_COUNT, key);
  if (!d) return "key";
  float v = 0;
  if (!parseNumber(valueText, v)) return "value";
  if (v < d->minV - 1e-4f || v > d->maxV + 1e-4f) return "range";
  if (d->fine > 0) v = roundf(v / d->fine) * d->fine;   // 對齊步進,避免 0.30000001 這種值
  v = constrain(v, d->minV, d->maxV);

  if (shared) {
    SharedSettings next = sharedSettings;
    writeParam((uint8_t *)&next, *d, v);
    if (const char *e = validateShared(next)) return e;
    LOCKED(sharedSettings = next);
    if (d->offset == offsetof(SharedSettings, noseAxis) || d->offset == offsetof(SharedSettings, upAxis))
      applyHardwareSettings();
    return nullptr;
  }

  ProfileSettings next = profiles[scope];
  const uint8_t n = (uint8_t)lroundf(v);
  if (strcmp(key, "upN") == 0) respaceSide(next.up, true, n);
  else if (strcmp(key, "dnN") == 0) respaceSide(next.down, false, n);
  else writeParam((uint8_t *)&next, *d, v);
  if (const char *e = validateProfile(next)) return e;
  LOCKED(profiles[scope] = next);
  return nullptr;
}

const char *settingsSetMany(int8_t scope, char *text) {
  // 格式:每行 key=value. 全部寫進副本,最後驗證一次才整塊套用 —— 逐項設定會卡在中間狀態的交叉驗證
  // (例如還原時第一段時間暫時大於總時間,曲線點暫時交錯). 點數鍵直接寫入,不做重新分布.
  if (scope < -1 || scope >= PROFILE_COUNT) return "scope";
  const bool shared = scope < 0;
  SharedSettings ns = sharedSettings;
  ProfileSettings np = shared ? profiles[0] : profiles[scope];
  uint16_t count = 0;
  for (char *save = nullptr, *line = strtok_r(text, "\n", &save); line; line = strtok_r(nullptr, "\n", &save)) {
    char *eq = strchr(line, '=');
    if (!eq) continue;
    *eq = 0;
    const char *key = line;
    char *val = eq + 1;
    size_t vl = strlen(val);
    if (vl && val[vl - 1] == '\r') val[vl - 1] = 0;
    const ParamDef *d = shared ? findParam(SHARED_PARAMS, SHARED_PARAM_COUNT, key)
                               : findParam(PROFILE_PARAMS, PROFILE_PARAM_COUNT, key);
    if (!d) return "key";
    float v = 0;
    if (!parseNumber(val, v)) return "value";
    if (v < d->minV - 1e-4f || v > d->maxV + 1e-4f) return "range";
    if (d->fine > 0) v = roundf(v / d->fine) * d->fine;
    writeParam(shared ? (uint8_t *)&ns : (uint8_t *)&np, *d, constrain(v, d->minV, d->maxV));
    ++count;
  }
  if (!count) return "badform";
  if (shared) {
    if (const char *e = validateShared(ns)) return e;
    LOCKED(sharedSettings = ns);
    applyHardwareSettings();
  } else {
    if (const char *e = validateProfile(np)) return e;
    LOCKED(profiles[scope] = np);
  }
  return nullptr;
}

// 名稱必須是完整的 UTF-8,不可有控制字元. 網頁輸入框送的一定合法,但直接呼叫 API 送亂碼位元組時,
// 設定 JSON 會變成不合法的 UTF-8(全功能輸入測試 2026-09-14 發現),存檔後每次讀設定都帶著壞資料.
static bool nameTextValid(const char *s) {
  for (size_t i = 0; s[i];) {
    const uint8_t c = (uint8_t)s[i];
    if (c < 0x20 || c == 0x7F) return false;
    const size_t len = c < 0x80 ? 1 : (c >> 5) == 0x6 ? 2 : (c >> 4) == 0xE ? 3 : (c >> 3) == 0x1E ? 4 : 0;
    if (!len) return false;
    for (size_t k = 1; k < len; ++k)
      if (((uint8_t)s[i + k] >> 6) != 0x2) return false;   // 遇到結尾 0 也會在這裡擋下
    i += len;
  }
  return true;
}

// 驗證名稱並截斷在 UTF-8 字元邊界上(不留半個中文字),結果寫進 out(補滿 0).
static const char *nameToBuffer(const char *name, char out[PROFILE_NAME_BUFFER]) {
  size_t n = strlen(name);
  if (n == 0 || !nameTextValid(name)) return "name";
  if (n > PROFILE_NAME_BUFFER - 1) {
    n = PROFILE_NAME_BUFFER - 1;
    while (n > 0 && ((uint8_t)name[n] & 0xC0) == 0x80) --n;
  }
  memset(out, 0, PROFILE_NAME_BUFFER);
  memcpy(out, name, n);
  return nullptr;
}

const char *settingsSetName(uint8_t index, const char *name) {
  if (index >= PROFILE_COUNT) return "scope";
  if (index == PROFILE_TEST_INDEX) return "namelocked";   // 「測試」組名稱固定(GG 2026-09-15)
  char buf[PROFILE_NAME_BUFFER];
  if (const char *e = nameToBuffer(name, buf)) return e;
  LOCKED(memcpy(profiles[index].name, buf, PROFILE_NAME_BUFFER));
  return nullptr;
}

const char *settingsSelectProfile(uint8_t index) {
  if (index >= PROFILE_COUNT) return "scope";
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return "savefail";
  const bool ok = prefs.putUChar("active", index) == 1;
  prefs.end();
  if (!ok) return "savefail";
  activeProfile = index;
  pendingActive = -1;   // 直接選用蓋過備份碼還沒儲存的選擇
  return nullptr;
}

const char *settingsCopyProfile(uint8_t from, uint8_t to) {
  if (from >= PROFILE_COUNT || to >= PROFILE_COUNT || from == to) return "scope";
  char name[PROFILE_NAME_BUFFER];
  memcpy(name, profiles[to].name, sizeof(name));   // 目標保留自己的名字,只複製飛法
  LOCKED(profiles[to] = profiles[from]; memcpy(profiles[to].name, name, sizeof(name)));
  return nullptr;
}

void settingsDefaults(int8_t scope) {
  if (scope < 0) {
    SharedSettings d;
    defaultShared(d);
    LOCKED(sharedSettings = d);
    applyHardwareSettings();
  } else if (scope < PROFILE_COUNT) {
    char name[PROFILE_NAME_BUFFER];
    memcpy(name, profiles[scope].name, sizeof(name));
    ProfileSettings d;
    defaultProfile(d, scope);
    memcpy(d.name, name, sizeof(name));
    LOCKED(profiles[scope] = d);
  }
}

const char *settingsSave() {
  Preferences prefs;
  if (!prefs.begin(PREF_NAMESPACE, false)) return "savefail";
  bool ok = true;
  if (settingsSharedDirty()) {
    if (saveBlob(prefs, "shared", (const uint8_t *)&sharedSettings, sizeof(SharedSettings))) { LOCKED(savedShared = sharedSettings); }
    else ok = false;
  }
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    if (!settingsProfileDirty(i)) continue;
    char key[3];
    profileKey(i, key);
    if (saveBlob(prefs, key, (const uint8_t *)&profiles[i], sizeof(ProfileSettings))) { LOCKED(savedProfiles[i] = profiles[i]); }
    else ok = false;
  }
  if (settingsActiveDirty()) {
    if (prefs.putUChar("active", (uint8_t)pendingActive) == 1) {
      LOCKED(activeProfile = (uint8_t)pendingActive);
      pendingActive = -1;
    } else {
      ok = false;
    }
  }
  prefs.end();
  return ok ? nullptr : "savefail";
}

void settingsRevert() {
  LOCKED(sharedSettings = savedShared; for (uint8_t i = 0; i < PROFILE_COUNT; ++i) profiles[i] = savedProfiles[i]);
  pendingActive = -1;
  applyHardwareSettings();
}

// --- 整份設定(設定備份碼用) --------------------------------------------------------
void settingsGetImage(SettingsImage &out) {
  LOCKED(out.shared = sharedSettings; for (uint8_t i = 0; i < PROFILE_COUNT; ++i) out.profiles[i] = profiles[i]);
  out.active = settingsActiveDirty() ? (uint8_t)pendingActive : activeProfile;
}

void settingsDefaultImage(SettingsImage &out) {
  defaultShared(out.shared);
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) defaultProfile(out.profiles[i], i);
  out.active = DEFAULT_ACTIVE_PROFILE;
}

static const ParamDef *imageParam(int8_t scope, const char *key) {
  if (scope < -1 || scope >= PROFILE_COUNT) return nullptr;
  return scope < 0 ? findParam(SHARED_PARAMS, SHARED_PARAM_COUNT, key) : findParam(PROFILE_PARAMS, PROFILE_PARAM_COUNT, key);
}

bool settingsParamRange(bool shared, const char *key, float &minV, float &maxV) {
  const ParamDef *d = imageParam(shared ? -1 : 0, key);
  if (!d) return false;
  minV = d->minV;
  maxV = d->maxV;
  return true;
}

const char *settingsParamKey(bool shared, size_t index) {
  if (shared) return index < SHARED_PARAM_COUNT ? SHARED_PARAMS[index].key : nullptr;
  return index < PROFILE_PARAM_COUNT ? PROFILE_PARAMS[index].key : nullptr;
}

bool settingsImageGet(const SettingsImage &img, int8_t scope, const char *key, float &v) {
  const ParamDef *d = imageParam(scope, key);
  if (!d) return false;
  v = readParam(scope < 0 ? (const uint8_t *)&img.shared : (const uint8_t *)&img.profiles[scope], *d);
  return true;
}

bool settingsImagePut(SettingsImage &img, int8_t scope, const char *key, float v, bool &clamped) {
  const ParamDef *d = imageParam(scope, key);
  if (!d) return false;
  clamped = v < d->minV - 1e-4f || v > d->maxV + 1e-4f;
  if (d->fine > 0) v = roundf(v / d->fine) * d->fine;   // 與 settingsSet 相同的對齊方式
  writeParam(scope < 0 ? (uint8_t *)&img.shared : (uint8_t *)&img.profiles[scope], *d, constrain(v, d->minV, d->maxV));
  return true;
}

const char *settingsImageSetName(SettingsImage &img, uint8_t index, const char *name) {
  if (index >= PROFILE_COUNT) return "scope";
  if (index == PROFILE_TEST_INDEX) return nullptr;   // 名稱鎖定:舊備份碼裡不管寫什麼,都維持「測試」
  return nameToBuffer(name, img.profiles[index].name);
}

const char *settingsImageValidate(const SettingsImage &img, int8_t &badScope) {
  badScope = -1;
  if (const char *e = validateShared(img.shared)) return e;
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    badScope = (int8_t)i;
    if (const char *e = validateProfile(img.profiles[i])) return e;
  }
  badScope = -1;
  if (img.active >= PROFILE_COUNT) return "scope";
  return nullptr;
}

void settingsApplyImage(const SettingsImage &img) {
  LOCKED(sharedSettings = img.shared; for (uint8_t i = 0; i < PROFILE_COUNT; ++i) profiles[i] = img.profiles[i]);
  pendingActive = img.active == activeProfile ? -1 : (int8_t)img.active;
  applyHardwareSettings();
}

bool settingsSnapshotForFlight(SharedSettings &shared, ProfileSettings &profile, uint8_t &index) {
  bool dirty = false;
  portENTER_CRITICAL(&settingsLock);
  shared = sharedSettings;
  index = activeProfile;
  profile = profiles[index];
  dirty = memcmp(&sharedSettings, &savedShared, sizeof(SharedSettings)) != 0 || settingsActiveDirty();
  for (uint8_t i = 0; i < PROFILE_COUNT && !dirty; ++i)
    dirty = memcmp(&profiles[i], &savedProfiles[i], sizeof(ProfileSettings)) != 0;
  portEXIT_CRITICAL(&settingsLock);
  return dirty;
}

void settingsCopyShared(SharedSettings &out) { LOCKED(out = sharedSettings); }

// --- JSON ------------------------------------------------------------------------
static void appendNumber(String &out, float v, const ParamDef &d) {
  if (d.type == PARAM_F32) {
    // 依細調步進決定小數位數
    const uint8_t digits = d.fine >= 1 ? 0 : (d.fine >= 0.1f ? 1 : 2);
    out += String(v, (unsigned int)digits);
  } else {
    out += String((long)lroundf(v));
  }
}

static void appendMeta(String &out, const ParamDef *table, size_t count) {
  out += '{';
  for (size_t i = 0; i < count; ++i) {
    const ParamDef &d = table[i];
    if (i) out += ',';
    out += '"';
    out += d.key;
    out += "\":[";
    out += String(d.minV, 2) + ',' + String(d.maxV, 2) + ',' + String(d.fine, 2) + ',' + String(d.coarse, 2);
    out += ']';
  }
  out += '}';
}

void settingsMetaJson(String &out) {
  out.reserve(3000);
  out = "{\"shared\":";
  appendMeta(out, SHARED_PARAMS, SHARED_PARAM_COUNT);
  out += ",\"profile\":";
  appendMeta(out, PROFILE_PARAMS, PROFILE_PARAM_COUNT);
  out += ",\"profiles\":" + String(PROFILE_COUNT) + ",\"curveMin\":" + String(CURVE_MIN_POINTS) +
         ",\"curveMax\":" + String(CURVE_MAX_POINTS) + '}';
}

static void appendValues(String &out, const uint8_t *base, const ParamDef *table, size_t count) {
  out += '{';
  for (size_t i = 0; i < count; ++i) {
    if (i) out += ',';
    out += '"';
    out += table[i].key;
    out += "\":";
    appendNumber(out, readParam(base, table[i]), table[i]);
  }
  out += '}';
}

static void appendJsonString(String &out, const char *s) {
  out += '"';
  for (; *s; ++s) {
    if (*s == '"' || *s == '\\') out += '\\';
    if ((uint8_t)*s < 0x20) continue;
    out += *s;
  }
  out += '"';
}

void settingsValuesJson(String &out, uint8_t profileIndex) {
  if (profileIndex >= PROFILE_COUNT) profileIndex = activeProfile;
  out.reserve(2500);
  // active 是含還沒儲存的飛行風格(備份碼套用),dirtyActive 表示它和存檔的不同
  const uint8_t act = settingsActiveDirty() ? (uint8_t)pendingActive : activeProfile;
  out = "{\"active\":" + String(act) + ",\"dirtyActive\":" + (settingsActiveDirty() ? "true" : "false") +
        ",\"edit\":" + String(profileIndex) + ",\"names\":[";
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    if (i) out += ',';
    appendJsonString(out, profiles[i].name);
  }
  out += "],\"dirtyShared\":";
  out += settingsSharedDirty() ? "true" : "false";
  out += ",\"dirtyProfiles\":[";
  for (uint8_t i = 0; i < PROFILE_COUNT; ++i) {
    if (i) out += ',';
    out += settingsProfileDirty(i) ? "true" : "false";
  }
  out += "],\"shared\":";
  appendValues(out, (const uint8_t *)&sharedSettings, SHARED_PARAMS, SHARED_PARAM_COUNT);
  out += ",\"profile\":";
  appendValues(out, (const uint8_t *)&profiles[profileIndex], PROFILE_PARAMS, PROFILE_PARAM_COUNT);
  out += '}';
}
