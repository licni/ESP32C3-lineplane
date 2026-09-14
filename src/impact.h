// 版本流水號: r2 (2026-09-13) 加地面滑行抖動判斷
// 舊: r1 (2026-09-13) 初版:衝擊尖峰偵測(分辨機輪觸地的短尖峰與特技動作的持續 G 力)
#pragma once
#include <Arduino.h>
// ============================================================================
// 衝擊尖峰偵測. 為什麼不能只看 G 力大小:特技直角彎持續 8~10g,比機輪觸地(約 2~5g)還大.
// 分辨依據是持續時間 —— 觸地是幾十毫秒的尖峰,動作是幾百毫秒以上的持續力.
//
//   基準 = |a| 的一階低通(時間常數 0.3 秒);超出量 = |a| - 基準.
//   超出量 > 1.0g 開始一次尖峰,< 0.5g 結束;結束時回報峰值與持續時間.
//   短尖峰期間凍結基準(不讓衝擊把基準拉高);超過 80ms 已確定是持續力,基準恢復追蹤,
//   否則動作後 G 力維持高檔時這次「尖峰」永遠結束不了,期間真的觸地也抓不到.
//
// 模擬驗證(tools/sim_impact.py,特技飛行 + 馬達震動 0.35g):特技中出現的短尖峰最大 2.3g,
// 人造觸地 2.7g / 3.5g 都抓得到. 所以觸地門檻預設 3.0g.
// ============================================================================

const uint16_t IMPACT_MAX_SPIKE_MS = 80;

struct ImpactEvent {
  float peakG;          // 超出基準的峰值
  uint16_t durationMs;  // 尖峰持續時間
  bool isShort() const { return durationMs <= IMPACT_MAX_SPIKE_MS; }
};

// 地面滑行抖動:機身正飛水平 + 機背軸(Z)持續抖動 → 飛機在地上彈跳,滑行.
// 用於「觸地提早降落」與降落程序的觸地判斷(GG 第三輪回饋:單一衝擊尖峰不可靠,改看持續抖動).
//   抖動 = Z 軸減掉自己的 8Hz 低通後,平方的 0.5 秒平均再開根號(RMS).
//   8Hz 的理由(tools/sim_impact.py 掃描):3Hz 擋不住直角彎 9g 急變化裡的 3~5Hz 成分,
//   筋斗剛回水平時抖動 2.54g 造成誤觸發;8Hz 特技最大 1.04g,地面 10~30Hz 顛簸仍抓得到.
//   持續時間用累加/倍速遞減,短暫掉到門檻下不會整個歸零.
class GroundRollDetector {
 public:
  void reset();
  void update(float accZG, float pitchDeg, float rollDeg, float dt, float vibThresholdG, float tiltDeg);
  float vibG() const { return vibG_; }
  bool level() const { return level_; }
  float holdSeconds() const { return holdS_; }

 private:
  bool initialized_ = false;
  float lpf_ = 1.0f;
  float meanSquare_ = 0.0f;
  float vibG_ = 0.0f;
  float holdS_ = 0.0f;
  bool level_ = false;
};

class ImpactDetector {
 public:
  void reset();
  // 每個控制節拍呼叫一次. 一次尖峰結束的那一拍回傳 true 並填入 event.
  bool update(float accMagG, float dtSeconds, ImpactEvent &event);

 private:
  bool initialized_ = false;
  bool active_ = false;
  float baseG_ = 1.0f;
  float peakG_ = 0.0f;
  float elapsedMs_ = 0.0f;
};
