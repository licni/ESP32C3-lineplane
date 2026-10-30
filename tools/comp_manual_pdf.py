# 版本流水號: r1 (2026-10-30) 補償功能說明書 PDF(GG:簡單扼要,圖文並茂,著重補償設定邏輯與用法)
# ============================================================================
# 產生 docs/補償功能說明_日期.pdf:機頭角度曲線,側傾曲線,線軸 G 回授三種補償的原理,設定邏輯與調法.
# 圖用 matplotlib 畫成 PNG(暫存資料夾),版面用 reportlab platypus. 中文字型:文泉驛正黑(wqy-zenhei.ttc).
# 數值(出廠值,參數範圍)對照 src/settings.cpp;改了出廠值要一起改這裡.
# 用法:python3 tools/comp_manual_pdf.py [輸出路徑]
# ============================================================================
import math
import os
import sys
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from matplotlib import font_manager as fm   # noqa: E402
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch, Rectangle   # noqa: E402
from reportlab.lib import colors   # noqa: E402
from reportlab.lib.enums import TA_CENTER   # noqa: E402
from reportlab.lib.pagesizes import A4   # noqa: E402
from reportlab.lib.styles import ParagraphStyle   # noqa: E402
from reportlab.lib.units import mm   # noqa: E402
from reportlab.pdfbase import pdfmetrics   # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont   # noqa: E402
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,   # noqa: E402
                                TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FONT = "WQY"
DATE = "2026-10-30"
FW = "2026.10.29.2"
ACCENT = "#c2410c"      # 焦橙(網頁主色)
GREEN = "#15803d"
RED = "#dc2626"
BLUE = "#2563eb"
GRAY = "#64748b"

# --- 出廠值(settings.cpp defaultProfile,B~E 組) ---
UP = [(20, 0), (45, 8), (70, 15), (90, 20)]        # 機頭朝上:死區 + 3 點
DOWN = [(-3, 0), (-30, -10), (-60, -20), (-90, -25)]
SIDE_DEFAULT = [(20, 0), (45, 0), (70, 0), (90, 0)]
SIDE_EXAMPLE = [(20, 0), (45, 8), (70, 15), (90, 20)]
BASE1, BASE2, MINP, MAXP = 75, 85, 30, 100
G_TARGET, G_GAIN, G_LIMIT, G_FILTER = 3.0, 10.0, 30, 0.5


def polyline(pts, x):
    """折線:死區以內 0,超過最後一點維持最後一點(與韌體 sideCompPct 同一套)."""
    xs = [abs(p[0]) for p in pts]
    ys = [p[1] for p in pts]
    ax = abs(x)
    if ax <= xs[0]:
        return 0.0
    for i in range(1, len(xs)):
        if ax <= xs[i]:
            return ys[i - 1] + (ys[i] - ys[i - 1]) * (ax - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1]


def pitch_comp(deg):
    return polyline(UP, deg) if deg >= 0 else polyline(DOWN, deg)


def side_factor(pitch, roll_rate=0):
    pf = 1.0 if pitch >= 0 else max(0.0, 1.0 + pitch / 45.0)
    rf = min(1.0, max(0.0, (180.0 - abs(roll_rate)) / 90.0))
    return pf * rf


def setup_fonts():
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "WenQuanYi Zen Hei"
    plt.rcParams["axes.unicode_minus"] = False
    pdfmetrics.registerFont(TTFont(FONT, FONT_PATH, subfontIndex=0))


# ============================================================================ 圖
def fig_pipeline(path):
    fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 30)
    ax.axis("off")
    boxes = [
        (1, 10, 18, 11, "基本油門\n(時間軸:第一段 / 第二段)", "#fde68a"),
        (22, 19, 19, 9.5, "機頭角度曲線\n-90°~+90°", "#bbf7d0"),
        (22, 1.5, 19, 9.5, "側傾曲線 × 淡出倍率\n翼軸仰角 0~90°", "#bbf7d0"),
        (45, 10, 18, 11, "線軸 G 回授微調\n(目標 G - 線軸 G) × 增益", "#bfdbfe"),
        (67, 10, 14, 11, "夾在油門\n下限~上限", "#e5e7eb"),
        (85, 10, 13, 11, "電變\n油門輸出", "#fecaca"),
    ]
    for x, y, w, h, t, c in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc=c, ec="#374151", lw=1))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=7.8)
    arrow = dict(arrowstyle="-|>", color="#374151", lw=1.2, mutation_scale=12)
    ax.add_patch(FancyArrowPatch((19, 15.5), (45, 15.5), **arrow))
    ax.add_patch(FancyArrowPatch((41, 23.5), (45, 16.5), **arrow))
    ax.add_patch(FancyArrowPatch((41, 6.5), (45, 14.5), **arrow))
    ax.add_patch(FancyArrowPatch((63, 15.5), (67, 15.5), **arrow))
    ax.add_patch(FancyArrowPatch((81, 15.5), (85, 15.5), **arrow))
    ax.text(31.5, 13.0, "＋ 曲線(方式 0,1)", ha="center", fontsize=7.5, color=GREEN)
    ax.text(54, 23.5, "＋ 回授(方式 1,2)", ha="center", fontsize=7.5, color=BLUE)
    ax.set_ylim(0, 30.5)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_geometry(path):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2), dpi=200)
    # 左:半球側視,翼軸仰角
    a1.set_aspect("equal")
    a1.set_xlim(-1.25, 1.25)
    a1.set_ylim(-0.15, 1.3)
    a1.axis("off")
    th = [math.radians(t) for t in range(0, 181)]
    a1.plot([math.cos(t) for t in th], [math.sin(t) for t in th], color=GRAY, lw=1.2)
    a1.plot([-1.2, 1.2], [0, 0], color="#8b5a2b", lw=2)
    a1.plot(0, 0, "o", color="#111", ms=6)
    a1.text(0, -0.1, "飛手", ha="center", fontsize=9)
    eps = math.radians(50)
    px, py = math.cos(eps), math.sin(eps)
    a1.plot([0, px], [0, py], color=GRAY, lw=1, ls="--")
    a1.add_patch(Arc((0, 0), 0.9, 0.9, theta1=0, theta2=50, color=ACCENT, lw=1.5))
    a1.text(0.5, 0.17, "翼軸仰角 ε", color=ACCENT, fontsize=9)
    # 飛機:機身沿切線,翼軸沿線
    tx, ty = -math.sin(eps), math.cos(eps)   # 切線方向(飛行方向)
    a1.plot([px - 0.16 * tx, px + 0.16 * tx], [py - 0.16 * ty, py + 0.16 * ty], color="#111", lw=4, solid_capstyle="round")
    a1.plot([px, px - 0.14 * px], [py, py - 0.14 * py], color="#111", lw=2)   # 內側翼(朝飛手)
    a1.text(px - 0.3, py + 0.18, "飛機", fontsize=9)
    a1.add_patch(FancyArrowPatch((px, py), (px, py - 0.3), arrowstyle="-|>", color=RED, lw=1.5, mutation_scale=12))
    a1.text(px + 0.07, py - 0.38, "重力 g", color=RED, fontsize=8)
    a1.add_patch(FancyArrowPatch((px, py), (px * 1.3, py * 1.3), arrowstyle="-|>", color=BLUE, lw=1.5, mutation_scale=12))
    a1.text(px * 1.3 + 0.03, py * 1.3, "離心力 V²/R", color=BLUE, fontsize=8)
    a1.set_title("半球面:翼軸仰角與線軸 G", fontsize=10)
    a1.text(-0.1, 1.2, "線軸 G = V²/R - g·sin ε", ha="center", fontsize=9, color=BLUE)
    # 右:機頭角度
    a2.set_aspect("equal")
    a2.set_xlim(-1.2, 1.2)
    a2.set_ylim(-0.8, 0.9)
    a2.axis("off")
    a2.plot([-1.1, 1.1], [0, 0], color=GRAY, lw=1, ls="--")
    a2.text(1.1, -0.1, "地平線", ha="right", fontsize=8, color=GRAY)
    p = math.radians(30)
    a2.plot([-0.8 * math.cos(p), 0.8 * math.cos(p)], [-0.8 * math.sin(p), 0.8 * math.sin(p)], color="#111", lw=5, solid_capstyle="round")
    a2.plot([0.5 * math.cos(p), 0.62 * math.cos(p) + 0.1], [0.5 * math.sin(p), 0.62 * math.sin(p) + 0.3], color="#111", lw=2)   # 垂直尾翼
    a2.add_patch(Arc((0, 0), 1.0, 1.0, theta1=0, theta2=30, color=ACCENT, lw=1.5))
    a2.text(0.55, 0.12, "機頭角度 +30°", color=ACCENT, fontsize=9)
    a2.text(-0.95, -0.35, "機頭朝上為正,朝下為負\n爬升時向上 → 加油門\n俯衝時向下 → 減油門", fontsize=8.5, va="top")
    a2.set_title("機頭角度(相對地平線)", fontsize=10)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_pitch_curve(path):
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    degs = list(range(-90, 91))
    comps = [pitch_comp(d) for d in degs]
    ax.axhspan(-3, 20, color="#fde68a", alpha=0.35, lw=0)
    ax.text(27, 8.5, "死區 -3°~+20°\n不補償", fontsize=8, color="#92400e", ha="center", va="center")
    ax.plot(comps, degs, color=ACCENT, lw=2.2)
    for a, c in UP[1:] + DOWN[1:]:
        ax.plot(c, a, "o", color=ACCENT, ms=6, mfc="white")
        ax.annotate(f"{a:+d}° → {c:+d}%", (c, a), textcoords="offset points", xytext=(8, -3 if a > 0 else -10), fontsize=8)
    ax.axvline(0, color=GRAY, lw=0.8)
    ax.axhline(0, color=GRAY, lw=0.8, ls="--")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-95, 95)
    ax.set_xlabel("補償(% 油門,加在基本油門上)")
    ax.set_ylabel("機頭角度(°)")
    ax.set_yticks(range(-90, 91, 30))
    ax.set_title("機頭角度曲線(出廠值,B~E 組)", fontsize=10)
    ax.grid(alpha=0.3)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_side_curve(path):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2), dpi=200, gridspec_kw={"width_ratios": [1.1, 1]})
    degs = list(range(0, 91))
    a1.axhspan(0, 20, color="#fde68a", alpha=0.35, lw=0)
    a1.text(12, 10, "死區 0~20°", fontsize=8, color="#92400e", va="center")
    a1.plot([polyline(SIDE_DEFAULT, d) for d in degs], degs, color=GRAY, lw=2.2, label="出廠:全部 0%(不補償)")
    a1.plot([polyline(SIDE_EXAMPLE, d) for d in degs], degs, color=ACCENT, lw=2.2, ls="--", label="範例:45°→+8,70°→+15,90°→+20")
    for a, c in SIDE_EXAMPLE[1:]:
        a1.plot(c, a, "o", color=ACCENT, ms=6, mfc="white")
    a1.set_xlim(-2, 25)
    a1.set_ylim(0, 92)
    a1.set_xlabel("補償(% 油門)")
    a1.set_ylabel("翼軸仰角(°)")
    a1.set_title("側傾曲線", fontsize=10)
    a1.legend(fontsize=7.5, loc="lower right")
    a1.grid(alpha=0.3)
    pitches = list(range(-90, 91))
    a2.plot(pitches, [side_factor(p) for p in pitches], color=GREEN, lw=2.2)
    a2.axvspan(-90, -45, color="#fecaca", alpha=0.4, lw=0)
    a2.text(-67, 0.5, "俯衝\n不補", ha="center", fontsize=8, color=RED)
    a2.text(45, 0.5, "平飛與爬升\n全額", ha="center", fontsize=8, color=GREEN)
    a2.set_xlim(-90, 90)
    a2.set_ylim(-0.05, 1.1)
    a2.set_xlabel("機頭角度(°)")
    a2.set_ylabel("側傾補償倍率")
    a2.set_title("機頭朝下時側傾補償淡出", fontsize=10)
    a2.grid(alpha=0.3)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_feedback(path):
    fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=200)
    gs = [i / 20 for i in range(0, 141)]
    trim = [max(-G_LIMIT, min(G_LIMIT, (G_TARGET - g) * G_GAIN)) for g in gs]
    ax.plot(gs, trim, color=BLUE, lw=2.2)
    ax.axhline(0, color=GRAY, lw=0.8)
    ax.axvline(G_TARGET, color=ACCENT, lw=1.2, ls="--")
    ax.text(G_TARGET + 0.08, 22, f"目標 G = {G_TARGET:.1f}\n讀值等於目標時不微調", color=ACCENT, fontsize=8.5)
    ax.annotate(f"增益 {G_GAIN:.0f} %/g:\n少 1 g 加 10%", (2.0, 10), textcoords="offset points", xytext=(-40, -70), fontsize=8.5,
                arrowprops=dict(arrowstyle="-|>", color=GRAY))
    ax.text(0.2, G_LIMIT - 4, f"上限 +{G_LIMIT}%", fontsize=8.5, color=BLUE)
    ax.text(6.9, -G_LIMIT + 2, f"下限 -{G_LIMIT}%", fontsize=8.5, color=BLUE, ha="right")
    ax.set_xlim(0, 7)
    ax.set_ylim(-35, 35)
    ax.set_xlabel("線軸 G(低通後,g)")
    ax.set_ylabel("回授微調(% 油門)")
    ax.set_title("線軸 G 回授(出廠值)", fontsize=10)
    ax.grid(alpha=0.3)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_timeline(path):
    fig, ax = plt.subplots(figsize=(7.2, 2.4), dpi=200)
    t = [i / 10 for i in range(0, 121)]
    ramp, nocomp = 2.0, 3.0
    base = [BASE1 * min(1, x / ramp) for x in t]
    ax.plot(t, base, color="#92400e", lw=2, label="基本油門(緩啟動 2 秒)")
    comp = []
    for x in t:
        if x < nocomp:
            comp.append(0)
        else:
            comp.append(10 * min(1, (x - nocomp) / 2.0))
    ax.plot(t, [b + c for b, c in zip(base, comp)], color=BLUE, lw=2, ls="--", label="加回授微調(範例 +10%,2 秒漸入)")
    ax.axvspan(0, nocomp, color="#fde68a", alpha=0.4, lw=0)
    ax.text(nocomp / 2, 20, "起飛後不補償\n(出廠 3 秒)\n曲線與回授都不作用", ha="center", fontsize=8, color="#92400e")
    ax.axvspan(nocomp, nocomp + 2, color="#bfdbfe", alpha=0.4, lw=0)
    ax.text(nocomp + 1, 20, "回授\n漸入", ha="center", fontsize=8, color=BLUE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 100)
    ax.set_xlabel("馬達啟動後秒數")
    ax.set_ylabel("油門 %")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.grid(alpha=0.3)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_hemisphere_ui(path):
    """監看頁 3D 半球位置的示意(與網頁同一種畫法:正交投影)."""
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=200)
    ax.set_aspect("equal")
    ax.axis("off")
    yaw, tilt = math.radians(-30), math.radians(28)

    def proj(eps, az):
        e, a = math.radians(eps), math.radians(az)
        x, y, z = math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)
        x1, y1 = x * math.cos(yaw) - y * math.sin(yaw), x * math.sin(yaw) + y * math.cos(yaw)
        return x1, z * math.cos(tilt) - y1 * math.sin(tilt), y1 * math.cos(tilt) + z * math.sin(tilt)

    def arc(f, n, col, lw=0.8):
        pts = [f(i / n) for i in range(n + 1)]
        for p, q in zip(pts, pts[1:]):
            ax.plot([p[0], q[0]], [p[1], q[1]], color=col, lw=lw if q[2] <= 0 else lw * 0.6, alpha=1 if q[2] <= 0 else 0.5)

    arc(lambda s: proj(0, s * 360), 120, GRAY, 1.3)
    for e in (30, 60):
        arc(lambda s, e=e: proj(e, s * 360), 90, "#cbd5e1")
    for a in range(0, 360, 30):
        arc(lambda s, a=a: proj(s * 90, a), 30, "#cbd5e1")
    ax.plot(0, 0, "o", color="#111", ms=5)
    ax.text(0.05, -0.05, "飛手", fontsize=8)
    zx, zy, _ = proj(90, 0)
    ax.text(zx + 0.04, zy, "頭頂 90°", fontsize=8, color=GRAY)
    for e in (0, 30, 60):
        x, y, _ = proj(e, 0)
        ax.text(x + 0.03, y + (0.0 if e else -0.06), f"{e}°", fontsize=7, color=GRAY)
    # 軌跡範例:水平圈 + 一個筋斗
    pts = []
    for i in range(0, 361, 3):
        az = i
        eps = 12 + (40 * math.sin(math.radians((i - 230) * 3)) if 230 <= i <= 290 else 0)
        pts.append((eps, az, 60 + eps * 0.5))
    for (e1, a1, t1), (e2, a2, t2) in zip(pts, pts[1:]):
        p, q = proj(e1, a1), proj(e2, a2)
        col = plt.cm.coolwarm(min(1, max(0, (t1 - 50) / 50)))
        ax.plot([p[0], q[0]], [p[1], q[1]], color=col, lw=2, alpha=1 if q[2] <= 0 else 0.45)
    # 目前位置與箭頭
    e0, a0 = 40, 150
    P = proj(e0, a0)
    Q = proj(e0 + 10, a0 + 6)
    ax.plot([0, P[0]], [0, P[1]], color=GRAY, lw=0.8, ls=":")
    ax.add_patch(FancyArrowPatch((P[0], P[1]), (Q[0], Q[1]), arrowstyle="-|>", color=GREEN, lw=2.5, mutation_scale=14))
    ax.plot(P[0], P[1], "o", color=GREEN, ms=8, mec="white")
    ax.text(P[0] + 0.06, P[1] + 0.02, "補償 +6.5%(加速)", color=GREEN, fontsize=8.5, fontweight="bold")
    ax.text(1.12, 1.0, "監看頁「3D 半球位置」\n高度角 = 翼軸仰角\n方位角 = 陀螺儀積分\n箭頭 = 飛行方向\n顏色 = 曲線補償\n(綠加速 / 紅減速)", fontsize=8, va="top")
    ax.text(1.12, 0.1, "紀錄頁「3D 飛行軌跡」\n依油門著色\n(藍低 → 紅高)\n白點 = 游標時刻", fontsize=8, va="top")
    ax.set_xlim(-1.2, 1.9)
    ax.set_ylim(-0.4, 1.05)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


# ============================================================================ PDF
def build(out_path):
    setup_fonts()
    tmp = tempfile.mkdtemp(prefix="comp-manual-")
    figs = {}
    for name, fn in [("pipeline", fig_pipeline), ("geom", fig_geometry), ("pitch", fig_pitch_curve), ("side", fig_side_curve),
                     ("fb", fig_feedback), ("tl", fig_timeline), ("h3", fig_hemisphere_ui)]:
        p = os.path.join(tmp, name + ".png")
        fn(p)
        figs[name] = p

    W, H = A4
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
                            title="線控飛機油門控制器 補償功能說明", author="SuperGG", subject=f"韌體 {FW}")
    st = {
        "title": ParagraphStyle("t", fontName=FONT, fontSize=20, leading=26, alignment=TA_CENTER, spaceAfter=4),
        "sub": ParagraphStyle("s", fontName=FONT, fontSize=10.5, leading=15, alignment=TA_CENTER, textColor=colors.HexColor(GRAY), spaceAfter=10),
        "h1": ParagraphStyle("h1", fontName=FONT, fontSize=14, leading=19, textColor=colors.HexColor(ACCENT), spaceBefore=10, spaceAfter=4),
        "h2": ParagraphStyle("h2", fontName=FONT, fontSize=11.5, leading=16, spaceBefore=7, spaceAfter=3),
        "body": ParagraphStyle("b", fontName=FONT, fontSize=9.6, leading=14.5, spaceAfter=3),
        "li": ParagraphStyle("li", fontName=FONT, fontSize=9.6, leading=14.5, leftIndent=11, bulletIndent=2, spaceAfter=1.5),
        "cap": ParagraphStyle("c", fontName=FONT, fontSize=8.5, leading=12, textColor=colors.HexColor(GRAY), alignment=TA_CENTER, spaceAfter=6),
        "note": ParagraphStyle("n", fontName=FONT, fontSize=9.2, leading=13.5, backColor=colors.HexColor("#fff7ed"),
                               borderColor=colors.HexColor("#fdba74"), borderWidth=0.6, borderPadding=5, spaceBefore=4, spaceAfter=8),
        "cell": ParagraphStyle("cell", fontName=FONT, fontSize=8.8, leading=12.5),
        "cellh": ParagraphStyle("cellh", fontName=FONT, fontSize=8.8, leading=12.5, textColor=colors.white),
    }

    def P(t, s="body"):
        return Paragraph(t, st[s])

    def LI(items):
        return [Paragraph(t, st["li"], bulletText="•") for t in items]

    def IMG(name, width_mm, cap, head=None):
        from PIL import Image as PILImage
        with PILImage.open(figs[name]) as im:
            w, h = im.size
        img = Image(figs[name], width=width_mm * mm, height=width_mm * mm * h / w)
        items = ([head] if head is not None else []) + [img, P(cap, "cap")]
        return [KeepTogether(items)]

    def TBL(rows, widths):
        data = [[Paragraph(c, st["cellh"] if i == 0 else st["cell"]) for c in r] for i, r in enumerate(rows)]
        t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(ACCENT)),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff7ed")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d6d3d1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        return t

    story = []
    # ---------------- 封面兼第 1 頁
    story += [P("線控飛機油門控制器", "title"), P("補償功能說明:角度曲線 · 側傾曲線 · 線軸 G 回授", "title"),
              P(f"對應韌體 {FW} · {DATE} · 設定都在網頁「角度補償」分頁", "sub")]
    story += [P("1. 油門是怎麼算出來的", "h1")]
    story += [P("飛行中每一拍(1 秒 200 次)的油門 = <b>基本油門</b>(計時器頁的時間軸決定)<b>+ 補償</b>,再夾在飛行中油門下限與上限之間送給電變. "
                "補償有三個來源,由每組飛行風格的「<b>補償方式</b>」決定用哪幾個:")]
    story += IMG("pipeline", 170, "圖 1:油門計算流程. 方式 0 只用兩條曲線;方式 1 曲線加回授;方式 2 只用回授.")
    story += [TBL([["補償方式", "用到什麼", "適合誰"],
                   ["0 曲線(出廠)", "機頭角度曲線 + 側傾曲線", "原本的做法. 反應最快(角度一變油門立刻變),要自己拉曲線."],
                   ["1 曲線 + 線軸 G 回授", "兩條曲線,再依線軸 G 微調", "想讓每個方位的拉力一樣,又保留曲線的快速反應. <b>建議從這裡開始試回授.</b>"],
                   ["2 只用線軸 G 回授", "不用曲線,基本油門 + 回授微調", "最少設定. 但分不出爬升與俯衝,要等速度掉了才補,快速動作會慢半拍."]],
                  [38, 52, 88])]
    story += [Spacer(1, 4), P("補償只在<b>飛行中</b>作用:緩啟動期間,起飛後「不補償秒數」內,降落中,以及感測器故障時都不補償(降落與故障時照時間軸走). "
                              "所有補償加起來再怎麼多,油門不會超過上限;再怎麼減,不會低於下限(下限最低 10%).")]

    # ---------------- 2 三個量
    story += [P("2. 控制器量到的三個量", "h1")]
    story += IMG("geom", 160, "圖 2:左:飛機在半球面上,翼軸(線的方向)與地平線的夾角是翼軸仰角 ε;右:機頭角度是機身相對地平線的俯仰.")
    story += [TBL([["量", "是什麼", "用在哪"],
                   ["機頭角度", "機身相對地平線的俯仰,朝上為正,−90°~+90°. 倒飛時也成立.", "機頭角度曲線;側傾淡出倍率"],
                   ["翼軸仰角", "翼軸(線)對地平線的仰角 0~90°. 低空平飛 0°,45° 高度平飛約 45°,正頭頂 90°. 正飛倒飛同值,順逆時針不分.", "側傾曲線;3D 半球的高度角"],
                   ["線軸 G", "加速度計沿翼軸量到的 G 值(低通後). 等於 離心力 V²/R − 重力順著線的分量 g·sin ε,就是飛手手上的拉力手感. 任何動作中都成立.", "線軸 G 回授;紀錄頁藍線"]],
                  [24, 104, 50])]
    story += [Spacer(1, 3), P("為什麼要補償:飛機飛到斜上方時,重力有一部分順著線往飛手拉,線拉力變小(頭頂時少掉整整 1 g). 以線長 18 m、單圈 4 秒為例,"
                              "低空離心力約 4.5 g,頭頂只剩 3.5 g;要維持同樣的拉力,頭頂速度要比低空快約 10%. 爬升時重力又拖慢飛機,所以還要再依機頭角度加油門.")]
    # ---------------- 3 機頭角度曲線
    story += IMG("pitch", 140, "圖 3:出廠曲線. 直軸是機頭角度,橫軸是補償. 死區內不補償,點與點之間直線相連,超過最後一點維持最後一點的值.", head=P("3. 機頭角度曲線(補速 / 減速)", "h1"))
    story += [P("設定邏輯", "h2")]
    story += LI(["朝上(補速)與朝下(減速)各一側,每側有一個<b>起點</b>(死區邊界)與 <b>1~4 個可調點</b>. 角度要由小到大,點不能交叉.",
                 "補償是<b>加在基本油門上的百分比</b>:第一段 75% + 補 8% = 83%. 兩段飛行共用同一條曲線,第二段只是基本油門不同.",
                 "網頁上可直接拖曳點,或用右側面板的 +/−(粗調 5,細調 1). 圖上紅線是目前角度,拿著飛機抬頭低頭就會動.",
                 "「撞牆檢查」會列出補償後超過上限或低於下限的角度區間:超過的部分會被夾掉,等於白補. 第二段基本油門高,更容易撞上限."])
    story += [P("出廠值(B~E 組)", "h2")]
    story += [TBL([["側", "起點", "點 1", "點 2", "點 3"],
                   ["朝上 補速", "+20°(0%)", "+45° → +8%", "+70° → +15%", "+90° → +20%"],
                   ["朝下 減速", "−3°(0%)", "−30° → −10%", "−60° → −20%", "−90° → −25%"]], [28, 30, 40, 40, 40])]
    story += [Spacer(1, 3), P("調法:機頭朝上的補償太少,爬升到頂會沒勁;太多,筋斗頂端會衝. 朝下減速太少,俯衝時線會鬆(速度過快拉力反而大,但落下來收不住);"
                              "太多,俯衝時動力不足. 每次只改一個點,一次改 3~5%,飛一趟看紀錄頁的油門與角度對照.")]
    story += [P("起飛後不補償秒數(計時器頁):後三點飛機停在地上就機頭朝上,起飛滑跑時不能被當成爬升而加油門. 出廠 3 秒;起飛加速慢的飛機建議設成實際加速到巡航的秒數.", "note")]

    # ---------------- 4 側傾曲線
    story += IMG("side", 165, "圖 4:左:側傾曲線,出廠全部 0%(灰線),虛線是一組範例;右:機頭朝下時側傾補償淡出的倍率.", head=P("4. 側傾曲線(翼軸仰角)", "h1"))
    story += [P("設定邏輯", "h2")]
    story += LI(["只有一側(翼軸仰角沒有負值),格式與朝上曲線相同:起點 + 1~4 點,角度由小到大.",
                 "<b>出廠全部 0%</b>:升級後飛法不變. 覺得斜上方(45°~90° 高度)平飛沒勁的飛手,把 70° 與 90° 的點往右拉幾 % 試飛.",
                 "<b>與機頭曲線相加</b>:斜著爬升時兩條都有值,合計會比較大. 撞牆檢查下方有「兩條同時作用的最壞情況」,看合計會不會撞上限.",
                 "<b>機頭朝下時淡出</b>:機頭 0° 時全額,往下到 −45° 線性淡到 0. 原因:斜上方往下俯衝時,側傾補償(正)會抵銷朝下曲線(負),"
                 "甚至變成加油門;淡出後俯衝交給朝下曲線減速.",
                 "<b>快速滾轉時關閉</b>:滾轉角速度 90→180 °/s 淡到 0. 半滾進倒飛時翼軸會掃過鉛直方向,翼軸仰角會短暫衝到 90°,不關會冒出一下 +20%."])
    story += [P("建議的第一組側傾曲線:起點 20°,點 45°→+4%,70°→+8%,90°→+12%,約為朝上曲線的一半. 飛幾趟後看紀錄頁的 3D 軌跡與線軸 G 藍線,頭頂的線軸 G 若還是明顯低於低空,再加.", "note")]
    # ---------------- 5 回授
    story += [KeepTogether([P("5. 線軸 G 回授(任何方位相同的拉力手感)", "h1"),
                            P("曲線是「看角度猜需要多少油門」;回授是「量實際的拉力手感,差多少補多少」. 線軸 G 比目標小就加油門,比目標大就減,比例控制,沒有積分:")])]
    story += IMG("fb", 140, "圖 5:微調量 = (目標 G − 線軸 G) × 增益,夾在 ±幅度上限. 出廠目標 3.0 g,增益 10 %/g,上限 ±30%.")
    story += [TBL([["參數", "出廠", "範圍", "意思 / 調法"],
                   ["補償方式", "曲線", "0 / 1 / 2", "選 1 開始用回授(曲線保留),熟了再試 2."],
                   ["目標線軸 G", "3.0 g", "0.5~10", "飛手喜歡的拉力. <b>先用曲線方式飛一趟,看紀錄頁「飛行中線軸 G」的低空值,設成那個數字.</b> 設太高整趟都會加油門,太低整趟都減."],
                   ["回授增益", "10 %/g", "0~50", "線軸 G 每少 1 g 加幾 % 油門. 大飛機動力餘裕小可加大;增益大又平滑秒數長可能來回抽油門."],
                   ["幅度上限", "±30%", "0~100", "回授最多加減幾 %. 小飛機 ±10~15% 就夠,大飛機 ±30% 起."],
                   ["平滑秒數", "0.5 s", "0.1~3", "線軸 G 的低通時間常數,濾螺旋槳震動. 越大越穩但越慢;0.5 秒配 10 %/g 不會震盪."]],
                  [26, 16, 18, 118])]
    story += [Spacer(1, 4)]
    story += IMG("tl", 140, "圖 6:起飛時序. 不補償秒數內曲線與回授都不作用;過了之後回授在 2 秒內漸入,避免速度還沒到時一次跳 +20~30%.")
    story += [P("使用步驟", "h2")]
    story += LI(["<b>第 1 趟</b>:補償方式維持「曲線」,照原本的曲線飛. 落地後看紀錄頁 G 力面板的<b>藍線(線軸 G)</b>與統計「飛行中線軸 G」:低空平飛的值就是目標值,頭頂掉多少就是回授要補的量.",
                 "<b>第 2 趟</b>:補償方式改「曲線 + 回授」,目標 G 填低空值,幅度先 ±15%. 監看頁飛行中面板會顯示「含線軸 G 微調 +x」. 看頭頂拉力有沒有補上.",
                 "<b>第 3 趟起</b>:頭頂還不夠就加增益或幅度;感覺油門一直在抽,把平滑秒數加大或增益減小. 想試「只回授」再切方式 2."])
    story += [P("已知限制:只回授方式分不出爬升與俯衝(同一高度瞬時線軸 G 相同),要等速度掉了才補,快速動作仍建議保留曲線. 只有一個目標 G,第二段基本油門多加的部分會被回授拉回一些. "
                "目標 G 與安裝頁的線長/單圈秒數不一致時,姿態計算的向心力補償會差幾 %,角度讀值會偏 3~5°,低於出廠死區.", "note")]

    # ---------------- 6 看讀數
    story += IMG("h3", 165, "圖 7:監看頁 3D 半球位置與紀錄頁 3D 飛行軌跡(示意).", head=P("6. 在地上與落地後怎麼看", "h1"))
    story += LI(["<b>監看頁</b>:機頭角度卡顯示機頭角度,滾轉,翼軸仰角,線軸 G;補償預覽一行寫出「機頭 x% + 側傾 y% = 合計」與兩段的實際油門. "
                 "拿著飛機在地上轉動,「3D 半球位置」的點會跟著動,箭頭是飛行方向,顏色與文字是這個姿態下曲線會加速還是減速(回授在地上沒有意義,不預測).",
                 "<b>紀錄頁</b>:板子一直記錄最近 10 分鐘(每 0.1 秒一筆,重新通電清除). G 力面板的藍線是線軸 G,目標線是虛線;「3D 飛行軌跡」依油門著色,點圖表任一時刻,軌跡上會有白點.",
                 "方位角由陀螺儀積分,馬達啟動時歸零,幾分鐘後會慢慢轉偏;看幾秒內的動作形狀,不要拿它對準場地方向."])
    story += [KeepTogether([P("7. 注意事項", "h1")] + LI(["每組飛行風格各自有曲線,補償方式與回授參數;改完要按上方「儲存」,有未儲存變更不能起飛.",
                 "從 2026.10.29.1 升級上來的板子,側傾曲線會是當時複製的朝上曲線(不是 0%),請到角度補償頁檢查;從更早版本升級的會是 0%.",
                 "設定備份碼含全部補償參數(世代 7、8);舊備份碼套用時,新參數保持板上的值.",
                 "感測器故障時所有補償關閉,只照時間軸飛;故障後要重新上電才會再用感測器."]))]
    story += [Spacer(1, 8), P(f"文件由 tools/comp_manual_pdf.py 產生,數值對照韌體 {FW} 的出廠值. 完整使用說明見 docs/使用說明書.md.", "cap")]
    doc.build(story)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", f"補償功能說明_{DATE}.pdf")
    print("寫出", build(out))
