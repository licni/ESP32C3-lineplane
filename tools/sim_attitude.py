# 版本流水號: r1 (2026-09-13) 線控飛行姿態估算模擬:驗證向心力補償的 Mahony 融合
# ============================================================================
# 用途:韌體寫進去之前,先用合成的線控飛行數據(平飛繞圈,連續筋斗,直角筋斗,倒飛,
# 地面滑跑)驗證姿態演算法. 真實姿態由腳本產生,感測器讀值由運動學精確推導,
# 再加上零點誤差,雜訊,馬達震動,餵給與韌體同一套演算法,比較算出的機頭角度與真值.
#
# 座標:機身 FLU(x=機頭,y=左翼,z=機背),世界 ENU(z=上). 逆時針繞圈=偏航率為正.
# 加速度計讀的是比力 f = a - g(靜止水平時讀 z=+1g).
# 機身座標的運動加速度 a = (dV/dt, r*V, -q*V),前提是速度沿機頭方向(無側滑).
#
# 用法: python tools/sim_attitude.py
# ============================================================================
import math
import random

G = 9.80665
LINE_R = 18.0            # 線長(公尺)
LAP_S = 5.2              # 單圈秒數
V0 = 2 * math.pi * LINE_R / LAP_S   # 約 21.7 m/s
TRUTH_DT = 0.001
FILTER_DT = 0.005        # 韌體控制迴圈 200Hz
STEP = int(round(FILTER_DT / TRUTH_DT))
T_END = 350.0
MOTOR_ON_T = 5.0
LAND_T = 330.0           # 開始降落
BLOCK_T0 = 40.0          # 特技動作區塊從這裡開始,每 60 秒重複一輪
BLOCK_LEN = 60.0


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def seg(t, t0, t1):
    return smooth((t - t0) / (t1 - t0))


# --- 飛行腳本:回傳 (pitch 機頭仰角 rad, roll rad, V m/s) -------------------
# 每個 60 秒區塊(區塊內時間 k):
#   0~9   連續三個圓筋斗(每個 3 秒)
#   20~24 直角筋斗
#   35~50 倒飛(含翻入翻出各 1 秒)
#   其餘  平飛
LOOPS = [(0.0, 3.0), (3.0, 3.0), (6.0, 3.0)]
SQUARE_K = 20.0
INVERT_K = (35.0, 50.0)


def block_k(t):
    if t < BLOCK_T0 or t >= LAND_T:
        return None
    return (t - BLOCK_T0) % BLOCK_LEN


def classify(t):
    if 1.0 <= t < MOTOR_ON_T:
        return "地面靜止"
    if MOTOR_ON_T <= t < 9.0:
        return "起飛滑跑"
    if 12.0 <= t < BLOCK_T0:
        return "平飛繞圈"
    k = block_k(t)
    if k is None:
        return None
    if k < 9.0:
        return "連續圓筋斗"
    if SQUARE_K <= k < SQUARE_K + 4.0:
        return "直角筋斗"
    if INVERT_K[0] + 1.0 <= k < INVERT_K[1] - 1.0:
        return "倒飛"
    if INVERT_K[0] <= k < INVERT_K[1]:
        return None
    return "動作間平飛"


def script(t):
    if t < MOTOR_ON_T:                      # 停在地面,後三點仰角 12 度
        return math.radians(12), 0.0, 0.0
    v = V0 * seg(t, MOTOR_ON_T, MOTOR_ON_T + 3.0)
    pitch = math.radians(12) * (1 - seg(t, MOTOR_ON_T + 1.0, MOTOR_ON_T + 3.0))
    roll = 0.0
    if t > 9.0:                             # 平飛亂流擺動 +-3 度
        pitch += math.radians(3) * math.sin(2 * math.pi * 0.5 * t)
    k = block_k(t)
    if k is not None:
        for (t0, d) in LOOPS:               # 圓筋斗:仰角 0→360,爬升掉速 20%
            if t0 <= k < t0 + d:
                ang = 2 * math.pi * smooth((k - t0) / d)
                pitch = ang
                v = V0 * (1 - 0.2 * math.sin(ang / 2) ** 2)
        if SQUARE_K <= k < SQUARE_K + 4.0:  # 直角筋斗:四個 90 度急轉,每個 0.35 秒
                                            # 急轉峰值約 390 度/秒,向心約 9.5g
            kk = k - SQUARE_K
            ang = 0.0
            for c in (0.0, 1.0, 2.0, 3.0):
                ang += (math.pi / 2) * seg(kk, c, c + 0.35)
            pitch = ang
            v = V0 * (1 - 0.25 * math.sin(ang / 2) ** 2)
        if INVERT_K[0] <= k < INVERT_K[1]:  # 倒飛:1 秒翻過去,尾端 1 秒翻回來
            roll = math.pi * (seg(k, INVERT_K[0], INVERT_K[0] + 1.0)
                              - seg(k, INVERT_K[1] - 1.0, INVERT_K[1]))
    if t >= LAND_T:                         # 降落:5 秒減速觸地
        f = seg(t, LAND_T, LAND_T + 5.0)
        v = V0 * (1 - f)
        pitch = math.radians(12) * f
    return pitch, roll, v


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def transpose(a):
    return [[a[j][i] for j in range(3)] for i in range(3)]


def build_truth():
    """產生真值:每個濾波步的 (機頭仰角, 陀螺儀 rad/s, 加速度計 g, 馬達是否運轉)."""
    n = int(T_END / TRUTH_DT) + 2
    mats = []
    vs = []
    psi = 0.0
    for i in range(n):
        t = i * TRUTH_DT
        pitch, roll, v = script(t)
        psi += v / LINE_R * TRUTH_DT            # 繞圈偏航(直角與圓筋斗期間也照轉)
        # 仰角為正=機頭朝上 → 繞 y(左翼)轉負角
        r = mul(rot_z(psi), mul(rot_y(-pitch), rot_x(roll)))
        mats.append(r)
        vs.append(v)
    out = []
    for i in range(1, n - 1, STEP):
        t = i * TRUTH_DT
        r = mats[i]
        rt = transpose(r)
        dr = [[(mats[i + 1][a][b] - mats[i - 1][a][b]) / (2 * TRUTH_DT) for b in range(3)] for a in range(3)]
        w = mul(rt, dr)
        p, q, rr = w[2][1], w[0][2], w[1][0]
        v = vs[i]
        dv = (vs[i + 1] - vs[i - 1]) / (2 * TRUTH_DT)
        up_body = r[2]                          # 世界上方向在機身座標 = R^T(0,0,1) = R 的第三列
        acc = [(dv) / G + up_body[0],
               (rr * v) / G + up_body[1],
               (-q * v) / G + up_body[2]]
        pitch_true = math.asin(max(-1.0, min(1.0, r[2][0])))
        out.append((t, pitch_true, (p, q, rr), acc, t >= MOTOR_ON_T and t < LAND_T + 5.0))
    return out


class Mahony:
    def __init__(self, kp_ground, kp_flight, v_set, comp, use_acc=True):
        self.q = [1.0, 0.0, 0.0, 0.0]
        self.kp_ground = kp_ground
        self.kp_flight = kp_flight
        self.v_set = v_set
        self.comp = comp
        self.use_acc = use_acc
        self.bias = [0.0, 0.0, 0.0]
        self.bias_n = 0
        self.motor_t = None

    def update(self, t, gyro, acc, motor):
        g = [gyro[i] - self.bias[i] for i in range(3)]
        if motor:
            if self.motor_t is None:
                self.motor_t = t
            ramp = min(1.0, (t - self.motor_t) / 3.0)   # 起飛不補償的那幾秒內速度爬升
        else:
            self.motor_t = None
            ramp = 0.0
            # 地上靜止學零點(模擬裡地面階段一定靜止,韌體要另外判斷靜止)
            self.bias_n += 1
            k = 1.0 / min(self.bias_n, 400)
            for i in range(3):
                self.bias[i] += (gyro[i] - self.bias[i]) * k
        ax, ay, az = acc
        if self.comp and motor:
            v = self.v_set * ramp
            ay -= g[2] * v / G
            az -= -g[1] * v / G
        norm = math.sqrt(ax * ax + ay * ay + az * az)
        kp = self.kp_flight if motor else self.kp_ground
        if self.use_acc and norm > 1e-3:
            w = max(0.0, 1.0 - abs(norm - 1.0) / 0.4)
            ax, ay, az = ax / norm, ay / norm, az / norm
            q0, q1, q2, q3 = self.q
            vx = 2 * (q1 * q3 - q0 * q2)
            vy = 2 * (q0 * q1 + q2 * q3)
            vz = q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3
            ex = ay * vz - az * vy
            ey = az * vx - ax * vz
            ez = ax * vy - ay * vx
            g = [g[0] + kp * w * ex, g[1] + kp * w * ey, g[2] + kp * w * ez]
        q0, q1, q2, q3 = self.q
        h = 0.5 * FILTER_DT
        n0 = q0 + (-q1 * g[0] - q2 * g[1] - q3 * g[2]) * h
        n1 = q1 + (q0 * g[0] + q2 * g[2] - q3 * g[1]) * h
        n2 = q2 + (q0 * g[1] - q1 * g[2] + q3 * g[0]) * h
        n3 = q3 + (q0 * g[2] + q1 * g[1] - q2 * g[0]) * h
        s = math.sqrt(n0 * n0 + n1 * n1 + n2 * n2 + n3 * n3)
        self.q = [n0 / s, n1 / s, n2 / s, n3 / s]

    def pitch(self):
        q0, q1, q2, q3 = self.q
        return math.asin(max(-1.0, min(1.0, 2 * (q1 * q3 - q0 * q2))))


def add_noise(truth, seed, realistic):
    rnd = random.Random(seed)
    bias = [math.radians(x) for x in (1.5, -1.2, 0.9)]    # 陀螺儀零點(地上會學掉)
    if realistic:
        drift = [math.radians(x) for x in (0.5, -0.4, 0.45)]   # 升溫後的零點漂移(學不到)
        # MPU6050 規格:刻度誤差 ±3%,軸間耦合 ±2%. 取中間值,每軸不同.
        scale = [[1.025, 0.012, -0.010],
                 [-0.015, 0.975, 0.013],
                 [0.011, -0.012, 1.020]]
    else:
        drift = [math.radians(x) for x in (0.15, -0.1, 0.12)]
        scale = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    noisy = []
    for (t, pt, gyro, acc, motor) in truth:
        warm = min(1.0, max(0.0, (t - MOTOR_ON_T) / 60.0))
        gs = []
        for i in range(3):
            g_true = sum(scale[i][j] * gyro[j] for j in range(3))
            v = g_true + bias[i] + drift[i] * warm + rnd.gauss(0, math.radians(0.3))
            gs.append(max(-math.radians(2000), min(math.radians(2000), v)))
        vib = 0.35 if motor else 0.0
        a_s = [max(-16.0, min(16.0, acc[i] + rnd.gauss(0, 0.03) + rnd.gauss(0, vib))) for i in range(3)]
        noisy.append((t, pt, gs, a_s, motor))
    return noisy


SEGMENT_NAMES = ["地面靜止", "起飛滑跑", "平飛繞圈", "連續圓筋斗", "直角筋斗", "倒飛", "動作間平飛"]


def run(noisy, **kw):
    f = Mahony(**kw)
    stats = {name: [0.0, 0.0, 0] for name in SEGMENT_NAMES}
    for (t, pt, gyro, acc, motor) in noisy:
        f.update(t, gyro, acc, motor)
        name = classify(t)
        if name is None:
            continue
        err = math.degrees(f.pitch() - pt)
        s = stats[name]
        s[0] = max(s[0], abs(err))
        s[1] += err * err
        s[2] += 1
    return {k: (v[0], math.sqrt(v[1] / max(1, v[2]))) for k, v in stats.items()}


def main():
    truth = build_truth()
    variants = [
        ("只用陀螺儀", dict(kp_ground=2.0, kp_flight=0.0, v_set=V0, comp=False)),
        ("不補償 Kp0.5", dict(kp_ground=2.0, kp_flight=0.5, v_set=V0, comp=False)),
        ("補償 Kp0.2", dict(kp_ground=2.0, kp_flight=0.2, v_set=V0, comp=True)),
        ("補償 Kp0.5", dict(kp_ground=2.0, kp_flight=0.5, v_set=V0, comp=True)),
        ("補償 Kp1.0", dict(kp_ground=2.0, kp_flight=1.0, v_set=V0, comp=True)),
        ("補償 Kp0.5 速度低估20%", dict(kp_ground=2.0, kp_flight=0.5, v_set=V0 * 0.8, comp=True)),
        ("補償 Kp0.5 速度高估20%", dict(kp_ground=2.0, kp_flight=0.5, v_set=V0 * 1.2, comp=True)),
    ]
    print(f"飛行速度 {V0:.1f} m/s (線長 {LINE_R}m, 單圈 {LAP_S}s),向心 {V0*V0/LINE_R/G:.2f} g,"
          f"飛行 {LAND_T - MOTOR_ON_T:.0f} 秒")
    print("每格 = 最大誤差 / 均方根誤差 (度)")
    for realistic in (False, True):
        noisy = add_noise(truth, seed=7, realistic=realistic)
        print()
        print("【感測器:" + ("真實規格(刻度誤差,軸間耦合,零點漂移)】" if realistic else "理想(只有小零點漂移)】"))
        print("".ljust(24) + "".join(n.ljust(11) for n in SEGMENT_NAMES))
        for (label, kw) in variants:
            res = run(noisy, **kw)
            print(label.ljust(24) + "".join(f"{res[n][0]:5.1f}/{res[n][1]:4.1f} " for n in SEGMENT_NAMES))


if __name__ == "__main__":
    main()
