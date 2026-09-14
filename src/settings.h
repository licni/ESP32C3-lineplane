// 版本流水號: r17 (2026-09-14) 版面 v9:共用設定尾端加蜂鳴器電位 buzzerActiveLow(+3 預留);舊存檔尾端補預設
// 舊: r16 (2026-09-14) 設定備份碼用的整份設定介面 SettingsImage;備份碼套用的飛行風格要按儲存才寫入(settingsActiveDirty)
// 舊: r15 (2026-09-14) 預留位元組 gearReserved 改為安全開關等待上限 armWaitMin(大小不變,讀到 0 當 3 分鐘)
// 舊: r14 (2026-09-14) 飛行中油門下限最低 THROTTLE_FLOOR_PCT = 10%(版面不變,舊存檔載入時補到 10)
// 舊: r13 (2026-09-13) 版面 v8:共用設定尾端加機輪收腳(啟用,反轉,行程下限/上限,起飛後收輪秒數,舵機速度)
// 舊: r12 (2026-09-13) 預留位元組 reserved1 改為起飛前水平限制 startLevelDeg(大小不變)
// 舊: r11 (2026-09-13) v7 尾端預留兩格改為轉速回傳開關與馬達極數(大小不變)
// 舊: r10 (2026-09-13) 共用設定尾端加扭轉機尾取消起飛(角度,封鎖秒數);版面 v7(共用設定變長,風格不變)
// 舊: r9 (2026-09-13) 協定改 PWM / DShot150 / DShot300(拿掉 600);r8:加 escPwmHz(用預留位元組,版面不變)
// 舊: r7 (2026-09-13) 可調點數改 1~4(存檔保留 5 格,版面仍是 v6)
// 舊: r6 (2026-09-13) 刪除第二段曲線(GG:兩段分開不好設定且易混淆),兩段共用一條;版面 v6(= v4 版面,可讀 v4/v5)
// 舊: r5 (2026-09-13) 第二段有自己的補償曲線(up2/down2),curveCompPct 加段別參數,由第一段複製曲線;版面 v5
// 舊: r4 (2026-09-13) 啟動手勢可關閉(關閉時上電直接倒數),手勢力道下限降到 0.5g;版面 v4
// 舊: r3 (2026-09-13) 換段三種方式;提早降落改為正飛水平 + Z 軸持續抖動(門檻/持續秒數/水平容許角);版面 v3
// 舊: r2 (2026-09-13) 加觸地提早降落(開關/門檻/起飛後啟用秒數),風格加換段方式(線性/階梯);版面改版 v2
// 舊: r1 (2026-09-13) 初版:共用設定 + 六組風格(A~E,TEST),參數表驅動的驗證,NVS 分塊存檔
#pragma once
#include <Arduino.h>
// ============================================================================
// 設定. 兩類:
//   共用設定(安裝與安全):感測器方位,角度修正,電變脈寬,手勢/外力/觸地/撞擊門檻,倒數秒數,飛行速度.
//   風格(飛法)×6:兩段油門與時間,緩啟動/換段/降落的加減力秒數,油門上下限,補償曲線.
// 所有可調參數都登記在參數表(settings.cpp 的 SHARED_PARAMS / PROFILE_PARAMS),範圍與步進只有
// 那一份:網頁從 /api/meta 讀,驗證也查同一張表,兩邊規則不會各自漂移.
//
// 存檔:NVS 命名空間 lpcfg,共用一塊,每組風格各一塊. 只寫有變更的塊,改一組不必重寫六組.
// 每塊前面有 magic/版本/長度,不符就那一塊回預設,其他塊不受影響.
// 結構版面改變時把 SETTINGS_LAYOUT_VERSION 加一(使用者該塊設定會回預設).
//
// 執行緒:只在 Arduino loop 修改. 控制工作飛行中讀的是起飛時複製的快照(第 4 階段),
// 待機時直接讀;C3 單核心且控制工作優先權最高,loop 在改的時候它必定停在節拍等待中.
// ============================================================================

const uint8_t PROFILE_COUNT = 6;          // A B C D E TEST
// 飛行中油門下限的最低值(GG 2026-09-14 安全審查 B4):下限設 0 時補償太負會變成沒動力. 參數範圍,載入舊存檔,狀態機都用它.
const uint8_t THROTTLE_FLOOR_PCT = 10;
// 可調點 1~4(GG 2026-09-13 從 2~5 改). 存檔仍保留 5 格,NVS 版面不變,不必改版轉移;
// 舊存檔若是 5 點,載入時拿掉一個最不影響曲線形狀的點(settings.cpp trimSide).
const uint8_t CURVE_STORE_POINTS = 5;
const uint8_t CURVE_MAX_POINTS = 4;
const uint8_t CURVE_MIN_POINTS = 1;
const uint8_t PROFILE_NAME_BUFFER = 24;   // UTF-8,中文一字 3 位元組,約 7 個中文字
const uint16_t SETTINGS_LAYOUT_VERSION = 9;
const uint8_t ARM_WAIT_DEFAULT_MIN = 3;   // 安全開關等待上限出廠值(GG 2026-09-14:3 分鐘,可調)

enum DisturbMode : uint8_t { DISTURB_EXTEND = 0, DISTURB_RESET = 1, DISTURB_OFF = 2 };
// 換段方式:直接跳 / 直接跳但以換段加力秒數過渡 / 把兩段的油門差平均分攤在第一段時間內
enum PhaseMode : uint8_t { PHASE_STEP = 0, PHASE_STEP_RAMP = 1, PHASE_SPREAD = 2 };
// DShot 只做 150 與 300(GG:600 太高用不到). ESC_PROTO_PWM50 的名稱沿用,實際頻率看 escPwmHz.
enum EscProtocol : uint8_t { ESC_PROTO_PWM50 = 0, ESC_PROTO_DSHOT150 = 1, ESC_PROTO_DSHOT300 = 2 };

struct SharedSettings {
  uint8_t noseAxis;          // ImuAxis:晶片哪一軸朝機頭
  uint8_t upAxis;            // ImuAxis:晶片哪一軸朝機背
  uint8_t noseRight;         // 網頁圖示機頭朝右(0=朝左,逆時針飛)
  uint8_t escProtocol;       // EscProtocol(第 6 階段)
  float pitchTrimDeg;        // 角度修正:加到量測值上,讓飛行時水平讀到 0
  uint16_t escMinUs;         // 油門 0% 的脈寬
  uint16_t escMaxUs;         // 油門 100% 的脈寬
  float gestureG;            // 啟動手勢:機頭方向推力門檻
  uint8_t countdownSec;      // 倒數秒數
  uint8_t disturbMode;       // DisturbMode
  uint8_t extendSec;         // 外力介入時延長幾秒
  uint8_t crashEnable;       // 撞擊斷電開關
  float disturbG;            // 倒數期間外力門檻
  float touchdownG;          // 降落:觸地衝擊門檻
  float touchdownStillSec;   // 降落:完全靜止幾秒視為已觸地
  uint8_t landingTimeoutSec; // 降落:保險時間
  uint8_t earlyLandEnable;   // 飛行中機輪觸地就提早降落(不滿意想停止時用)
  uint8_t earlyLandArmSec;   // 馬達啟動後幾秒才開始偵測(避開起飛滑跑的顛簸)
  uint8_t earlyLandTiltDeg;  // 「正飛水平」的容許角度(機頭與滾轉都要在這個範圍內)
  float crashG;              // 撞擊斷電門檻
  float lineLengthM;         // 線長(姿態向心力補償用)
  float lapSec;              // 單圈秒數(姿態向心力補償用)
  float calibHoldSec;        // 電變校正精靈保持最大油門秒數(第 6 階段)
  float earlyLandVibG;       // 地面滑行抖動門檻(機背軸抖動強度,見 impact.h 的 GroundRollDetector)
  float earlyLandHoldSec;    // 抖動要持續多久才觸發
  uint8_t gestureEnable;     // 1=要做啟動手勢才倒數;0=上電後直接倒數(資深飛友習慣),每次上電只自動啟動一次
  uint8_t startLevelDeg;     // 起飛前水平限制:機頭或滾轉超過這個角度,手勢與上電自動倒數都不啟動(原預留位元組,讀到 0 當 35)
  uint16_t escPwmHz;         // PWM 更新頻率(開機套用). 占用原本的預留位元組,舊存檔讀到 0 時當 50Hz
  // --- v7 起加在尾端(v4~v6 的存檔讀進來時這幾格補預設) ---
  uint8_t twistCancelDeg;    // 手勢起飛後,抓著機尾繞機背軸扭轉超過這個角度就取消起飛(0 = 關閉)
  uint8_t twistBlockSec;     // 取消後幾秒內不接受啟動手勢(抬起尾巴放下時的撞擊不會又觸發)
  uint8_t escRpmTelemetry;   // 雙向 DShot 轉速回傳(只在 DShot300 有效,開機套用;預設關)
  uint8_t motorPoles;        // 馬達極數(轉速換算用,預設 14;0 視為 14)
  // --- v8 起加在尾端:機輪收腳(GG 2026-09-13;v4~v7 的存檔讀進來時補預設) ---
  uint8_t gearEnable;        // 收輪功能(觸地提早降落開啟時不作用)
  uint8_t gearReverse;       // 舵機反轉:0 = 放下在行程下限,收起在上限;1 = 相反
  uint16_t gearMinUs;        // 舵機行程下限
  uint16_t gearMaxUs;        // 舵機行程上限
  uint8_t gearRetractSec;    // 馬達啟動後幾秒收輪
  // 原本是收腳區塊的預留位元組(舊存檔一定是 0,載入時補 3). 起飛程序開始後這麼多分鐘沒按安全開關就自動取消
  uint8_t armWaitMin;
  float gearTravelSec;       // 舵機從一端走到另一端的秒數(0 = 直接跳)
  // --- v9 起加在尾端:蜂鳴器(GG 2026-09-14;v4~v8 的存檔讀進來時補預設) ---
  uint8_t buzzerActiveLow;   // 0 = 高電位響(出廠),1 = 低電位響
  uint8_t reserved9[3];
};

struct CurvePoint {
  int8_t angle;   // 度
  int8_t pct;     // 補償百分比(加在基本油門上)
};

struct CurveSide {
  int8_t deadband;   // 死區邊界角度(朝上為正值,朝下為負值),補償從這裡的 0% 開始
  uint8_t count;     // 可調點數量 1~4
  CurvePoint pts[CURVE_STORE_POINTS];   // 第 5 格不再使用,只為維持存檔版面
};

struct ProfileSettings {
  char name[PROFILE_NAME_BUFFER];
  uint8_t phase1Pct;         // 第一段基本油門
  uint8_t phase2Pct;         // 第二段基本油門
  uint8_t minPct;            // 飛行中油門下限
  uint8_t maxPct;            // 飛行中油門上限
  uint16_t phase1Sec;        // 第一段持續時間(從馬達啟動算)
  uint16_t flightSec;        // 總飛行時間(到了開始降落)
  float takeoffRampSec;      // 緩啟動加力秒數:從 0 加到第一段油門
  float phaseRampSec;        // 換段加力秒數(線性增加時)
  float noCompSec;           // 馬達啟動後幾秒內不補償
  float landingRampSec;      // 降落減力秒數
  uint8_t landingPct;        // 降落時降到的油門
  uint8_t phaseMode;         // PhaseMode
  uint8_t reserved0[2];
  CurveSide up;              // 補償曲線(兩段飛行共用同一條;第二段只是基本油門不同)
  CurveSide down;
};

// --- 目前生效的設定(RAM) -----------------------------------------------------
extern SharedSettings sharedSettings;
extern ProfileSettings profiles[PROFILE_COUNT];
extern uint8_t activeProfile;   // 飛行使用哪一組;選擇時立即存檔,不算「未儲存變更」(備份碼套用的例外,見 settingsActiveDirty)

void settingsBegin();
bool settingsSharedDirty();
bool settingsProfileDirty(uint8_t index);
bool settingsActiveDirty();   // 備份碼套用了不同的飛行風格,還沒按儲存
bool settingsAnyDirty();

// 設定單一參數. scope = -1 共用,0~5 風格. 成功回 nullptr,失敗回錯誤代碼(網頁查表顯示).
const char *settingsSet(int8_t scope, const char *key, const char *valueText);
// 一次設定多個參數(每行 key=value),全部寫完才驗證並整塊套用. text 會被改寫(切詞).
const char *settingsSetMany(int8_t scope, char *text);
const char *settingsSetName(uint8_t index, const char *name);
const char *settingsSelectProfile(uint8_t index);
const char *settingsCopyProfile(uint8_t from, uint8_t to);// 回預設只改 RAM,真正覆蓋是按儲存那一刻;在那之前按「放棄變更」都救得回來.
void settingsDefaults(int8_t scope);
const char *settingsSave();
void settingsRevert();

// 把參數表與目前值組成 JSON(網頁用).
void settingsMetaJson(String &out);
void settingsValuesJson(String &out, uint8_t profileIndex);

// --- 整份設定(設定備份碼 settings_backup.cpp 用) ---------------------------------
struct SettingsImage {
  SharedSettings shared;
  ProfileSettings profiles[PROFILE_COUNT];
  uint8_t active;
};
void settingsGetImage(SettingsImage &out);       // 目前 RAM 的值(飛行風格含還沒儲存的)
void settingsDefaultImage(SettingsImage &out);   // 出廠值
// 參數表查詢:scope -1 共用,0~5 風格. 沒有這個參數回 false.
bool settingsParamRange(bool shared, const char *key, float &minV, float &maxV);
const char *settingsParamKey(bool shared, size_t index);   // 參數表第 index 個的名稱,超過回 nullptr
bool settingsImageGet(const SettingsImage &img, int8_t scope, const char *key, float &v);
// 寫入一個參數:夾到參數表範圍並對齊步進. clamped = 原值超出範圍被夾. 沒有這個參數回 false. 不做交叉驗證,點數鍵直接寫.
bool settingsImagePut(SettingsImage &img, int8_t scope, const char *key, float v, bool &clamped);
const char *settingsImageSetName(SettingsImage &img, uint8_t index, const char *name);
// 交叉驗證整份設定. 失敗回錯誤代碼,badScope = -1 共用或 0~5 風格.
const char *settingsImageValidate(const SettingsImage &img, int8_t &badScope);
// 驗證過的整份設定套到 RAM(變成未儲存變更,飛行風格也是按儲存才寫入).
void settingsApplyImage(const SettingsImage &img);

// 控制工作用(上鎖複製):起飛快照,回傳是否有未儲存變更(共用或任一風格).
bool settingsSnapshotForFlight(SharedSettings &shared, ProfileSettings &profile, uint8_t &profileIndex);
// 控制工作每拍複製共用設定(待機時門檻即時生效).
void settingsCopyShared(SharedSettings &out);

// 補償曲線:回傳某個機頭角度的補償百分比(兩段飛行共用).
float curveCompPct(const ProfileSettings &p, float pitchDeg);
// 百分比換脈寬.
uint16_t pctToUs(float pct);
