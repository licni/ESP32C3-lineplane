# 版本流水號: r2 (2026-09-13) 加地面滑行抖動判斷(正飛水平 + Z 軸持續抖動)與濾波常數掃描
# 舊: r1 (2026-09-13) 觸地尖峰偵測模擬:特技動作不可誤判成觸地,真觸地要抓得到
# ============================================================================
# 為什麼要這個測試:特技直角彎持續 8~10g,比機輪觸地的衝擊(約 2~5g)還大,只看 G 力大小必定誤判.
# 分辨依據是持續時間:觸地是幾十毫秒的尖峰,動作是幾百毫秒的持續力.
#
# 偵測法(與韌體 impact 偵測同一套):
#   基準 = |a| 的一階低通(時間常數 0.3 秒);超出量 = |a| - 基準.
#   超出量 > 1.0g 開始一次尖峰,< 0.5g 結束;結束時回報 (峰值, 持續毫秒).
#   消費端:峰值 >= 門檻 且 持續 <= 80ms 才算觸地.
#
# 用 sim_attitude.py 的飛行真值(含馬達震動 0.35g)跑一遍,再疊上幾個人造觸地衝擊.
# 用法: python tools/sim_impact.py
# ============================================================================
import math
import random

import sim_attitude as sa

DT = sa.FILTER_DT
BASE_TAU = 0.3
START_G = 1.0
END_G = 0.5
MAX_SPIKE_MS = 80


class ImpactDetector:
    def __init__(self):
        self.base = None
        self.active = False
        self.peak = 0.0
        self.start_t = 0.0

    def update(self, t, mag):
        if self.base is None:
            self.base = mag
        excess = mag - self.base
        event = None
        if not self.active and excess > START_G:
            self.active, self.peak, self.start_t = True, excess, t
        elif self.active:
            self.peak = max(self.peak, excess)
            if excess < END_G:
                event = (self.peak, (t - self.start_t) * 1000.0)
                self.active = False
        # 短尖峰期間凍結基準,不讓衝擊本身把基準拉高. 超過 MAX_SPIKE_MS 就已經確定是持續力,
        # 基準恢復追蹤 —— 否則動作後 G 力維持高檔(繞圈 2.7g)時這次「尖峰」永遠結束不了,
        # 期間真的觸地也抓不到(r1 模擬實測卡住 28 秒).
        if not self.active or (t - self.start_t) * 1000.0 > MAX_SPIKE_MS:
            self.base += (mag - self.base) * (DT / BASE_TAU)
        return event


def impact_pulse(t, t0, peak_g, width_s):
    """半正弦衝擊波形(DLPF 44Hz 後大致如此)."""
    if t0 <= t < t0 + width_s:
        return peak_g * math.sin(math.pi * (t - t0) / width_s)
    return 0.0


class GroundRollDetector:
    """地面滑行抖動:機身正飛水平 + 機背軸(Z)持續抖動. 與韌體 impact.cpp 同一套."""
    # 2026-09-13 掃描(門檻 0.8g,水平 20°,持續 1 秒):
    #   LPF 0.05(3Hz)/RMS 0.5 :直角筋斗剛回水平時抖動 2.54g → 誤觸發(9g 急轉含 3~5Hz 成分)
    #   LPF 0.02(8Hz)/RMS 0.5 :特技最大 1.04g 不觸發,地面滑行 3.8 秒觸發  ← 採用
    #   LPF 0.02/RMS 0.25     :特技最大 1.24g,地面 4.0 秒
    #   LPF 0.01(16Hz)        :連地面 10~30Hz 顛簸都濾掉,抓不到
    LPF_TAU = 0.02     # Z 軸低通(約 8Hz):扣掉它剩下的就是抖動,特技動作的慢變化 G 力被濾掉
    RMS_TAU = 0.5      # 抖動強度的平均時間

    def __init__(self):
        self.lpf = None
        self.ms = 0.0
        self.hold = 0.0

    def update(self, az, pitch_deg, roll_deg, vib_thr, tilt_deg):
        if self.lpf is None:
            self.lpf = az
        self.lpf += (az - self.lpf) * (DT / self.LPF_TAU)
        hp = az - self.lpf
        self.ms += (hp * hp - self.ms) * (DT / self.RMS_TAU)
        vib = math.sqrt(self.ms)
        level = abs(pitch_deg) <= tilt_deg and abs(roll_deg) <= tilt_deg
        if vib >= vib_thr and level:
            self.hold += DT
        else:
            self.hold = max(0.0, self.hold - 2 * DT)
        return vib, level, self.hold


def ground_roll_test(noisy):
    print("\n==== 地面滑行抖動判斷(門檻 0.8g,水平容許 20°,持續 1.0 秒) ====")
    thr, tilt, hold_s = 0.8, 20.0, 1.0
    rnd = random.Random(5)
    for label, ground in (("只有特技飛行", None), ("最後 8 秒在地上滑行(10~30Hz 顛簸,1.0g)", 340.0)):
        det = GroundRollDetector()
        max_vib_level = 0.0
        max_vib_any = 0.0
        trigger_t = None
        phase = 0.0
        for (t, pt, _g, acc, motor) in noisy:
            az = acc[2]
            pitch = math.degrees(pt)
            roll = 0.0   # 模擬腳本倒飛以外 roll=0;倒飛段以 pitch 判斷已足夠說明
            k = sa.block_k(t)
            if k is not None and sa.INVERT_K[0] <= k < sa.INVERT_K[1]:
                roll = 180.0
            if ground is not None and t >= ground:
                pitch, roll = 12.0, 0.0
                phase += 2 * math.pi * rnd.uniform(10, 30) * DT
                az = 1.0 + 1.4 * math.sin(phase) + rnd.gauss(0, 0.3)
            vib, level, hold = det.update(az, pitch, roll, thr, tilt)
            if t > sa.MOTOR_ON_T + 10:
                max_vib_any = max(max_vib_any, vib)
                if level:
                    max_vib_level = max(max_vib_level, vib)
                if hold >= hold_s and trigger_t is None:
                    trigger_t = t
        print(f"  【{label}】抖動最大 {max_vib_any:.2f} g(水平時 {max_vib_level:.2f} g),"
              f"觸發:{'無' if trigger_t is None else f't={trigger_t:.2f}s'}")


def main():
    truth = sa.build_truth()
    noisy = sa.add_noise(truth, seed=11, realistic=True)
    # 人造觸地:平飛中輕碰(2.5g/30ms),重碰(5g/40ms),降落觸地(3g/50ms)
    touches = [(30.0, 2.5, 0.03), (120.5, 5.0, 0.04), (332.0, 3.0, 0.05)]
    rnd = random.Random(3)

    for label, add_touch in (("只有特技飛行(不應有觸地)", False), ("加入 3 次人造觸地", True)):
        det = ImpactDetector()
        events = []
        max_mag = 0.0
        for (t, _pt, _g, acc, motor) in noisy:
            mag = math.sqrt(sum(a * a for a in acc))
            if add_touch:
                for (t0, pk, w) in touches:
                    mag += impact_pulse(t, t0, pk, w)
            max_mag = max(max_mag, mag)
            ev = det.update(t, mag)
            if ev:
                events.append((t, ev[0], ev[1]))
        short = [e for e in events if e[2] <= MAX_SPIKE_MS]
        longest = max(e[2] for e in events)
        print(f"\n【{label}】最大 |a| = {max_mag:.1f} g,尖峰事件 {len(events)} 個,其中短尖峰(<= {MAX_SPIKE_MS}ms) {len(short)} 個,"
              f"最長一次 {longest:.0f} ms")
        for (t, pk, ms) in events:
            if ms <= MAX_SPIKE_MS and pk >= 1.8:
                print(f"  短尖峰 t={t:7.2f}s  峰值 {pk:5.2f} g  持續 {ms:3.0f} ms")
        if short:
            print(f"  短尖峰最大峰值 {max(e[1] for e in short):.2f} g(觸地門檻要高於特技中出現的短尖峰)")
    _ = rnd
    ground_roll_test(noisy)


if __name__ == "__main__":
    main()
