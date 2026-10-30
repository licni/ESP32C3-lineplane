# 版本流水號: r2 (2026-10-30) 改成照網頁內容逐項說明(GG:搭配設定器的網頁,各功能怎麼用、何時用,抽象的部分才講物理,要有範例);
#   截圖來自 tools/web_mock.py 假伺服器 + tools/comp_manual_shots.js(Playwright),存在 docs/images/comp_manual/,沒有截圖也能產生(略過圖)
# 舊: r1 (2026-10-30) 補償功能說明書 PDF 初版(原理為主)
# ============================================================================
# 產生 docs/補償功能說明_日期.pdf. 圖:網頁截圖(docs/images/comp_manual)+ 兩張 matplotlib 概念圖. 版面 reportlab platypus,中文字型文泉驛正黑.
# 數值(出廠值,範例)對照 src/settings.cpp;改了出廠值要一起改這裡,並重跑截圖(python3 tools/web_mock.py 8765 & node tools/comp_manual_shots.js).
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
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch   # noqa: E402
from reportlab.lib import colors   # noqa: E402
from reportlab.lib.enums import TA_CENTER   # noqa: E402
from reportlab.lib.pagesizes import A4   # noqa: E402
from reportlab.lib.styles import ParagraphStyle   # noqa: E402
from reportlab.lib.units import mm   # noqa: E402
from reportlab.pdfbase import pdfmetrics   # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont   # noqa: E402
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "docs", "images", "comp_manual")
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FONT = "WQY"
DATE = "2026-10-30"
FW = "2026.10.29.2"
ACCENT = "#c2410c"
GREEN = "#15803d"
RED = "#dc2626"
BLUE = "#2563eb"
GRAY = "#64748b"


def setup_fonts():
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "WenQuanYi Zen Hei"
    plt.rcParams["axes.unicode_minus"] = False
    pdfmetrics.registerFont(TTFont(FONT, FONT_PATH, subfontIndex=0))


def side_factor(pitch):
    return 1.0 if pitch >= 0 else max(0.0, 1.0 + pitch / 45.0)


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


def fig_fade(path):
    fig, ax = plt.subplots(figsize=(5.2, 2.2), dpi=200)
    pitches = list(range(-90, 91))
    ax.plot(pitches, [side_factor(p) for p in pitches], color=GREEN, lw=2.2)
    ax.axvspan(-90, -45, color="#fecaca", alpha=0.4, lw=0)
    ax.text(-67, 0.5, "俯衝\n不補", ha="center", fontsize=8, color=RED)
    ax.text(45, 0.5, "平飛與爬升\n全額", ha="center", fontsize=8, color=GREEN)
    ax.set_xlim(-90, 90)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlabel("機頭角度(°)")
    ax.set_ylabel("側傾補償倍率")
    ax.grid(alpha=0.3)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)



# ============================================================================ PDF
def build(out_path):
    setup_fonts()
    tmp = tempfile.mkdtemp(prefix="comp-manual-")
    figs = {}
    for name, fn in [("pipeline", fig_pipeline), ("geom", fig_geometry), ("fade", fig_fade)]:
        p = os.path.join(tmp, name + ".png")
        fn(p)
        figs[name] = p
    for f in os.listdir(SHOTS) if os.path.isdir(SHOTS) else []:
        if f.endswith(".png"):
            figs[f[:-4]] = os.path.join(SHOTS, f)

    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=13 * mm, bottomMargin=13 * mm,
                            title="線控飛機油門控制器 補償功能說明", author="SuperGG", subject=f"韌體 {FW}")
    st = {
        "title": ParagraphStyle("t", fontName=FONT, fontSize=19, leading=25, alignment=TA_CENTER, spaceAfter=3),
        "sub": ParagraphStyle("s", fontName=FONT, fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.HexColor(GRAY), spaceAfter=8),
        "h1": ParagraphStyle("h1", fontName=FONT, fontSize=14, leading=19, textColor=colors.HexColor(ACCENT), spaceBefore=9, spaceAfter=4),
        "h2": ParagraphStyle("h2", fontName=FONT, fontSize=11.5, leading=16, spaceBefore=6, spaceAfter=3),
        "body": ParagraphStyle("b", fontName=FONT, fontSize=9.6, leading=14.5, spaceAfter=3),
        "li": ParagraphStyle("li", fontName=FONT, fontSize=9.6, leading=14.5, leftIndent=11, bulletIndent=2, spaceAfter=1.5),
        "cap": ParagraphStyle("c", fontName=FONT, fontSize=8.5, leading=12, textColor=colors.HexColor(GRAY), alignment=TA_CENTER, spaceAfter=6),
        "note": ParagraphStyle("n", fontName=FONT, fontSize=9.2, leading=13.5, backColor=colors.HexColor("#fff7ed"),
                               borderColor=colors.HexColor("#fdba74"), borderWidth=0.6, borderPadding=5, spaceBefore=5, spaceAfter=8),
        "ex": ParagraphStyle("ex", fontName=FONT, fontSize=9.2, leading=13.5, backColor=colors.HexColor("#f0fdf4"),
                             borderColor=colors.HexColor("#86efac"), borderWidth=0.6, borderPadding=5, spaceBefore=5, spaceAfter=8),
        "cell": ParagraphStyle("cell", fontName=FONT, fontSize=8.8, leading=12.5),
        "cellh": ParagraphStyle("cellh", fontName=FONT, fontSize=8.8, leading=12.5, textColor=colors.white),
    }

    def P(t, s="body"):
        return Paragraph(t, st[s])

    def LI(items):
        return [Paragraph(t, st["li"], bulletText="•") for t in items]

    def IMG(name, width_mm, cap="", head=None):
        if name not in figs:
            return [P(f"(缺圖 {name})", "cap")]
        from PIL import Image as PILImage
        with PILImage.open(figs[name]) as im:
            w, h = im.size
        img = Image(figs[name], width=width_mm * mm, height=width_mm * mm * h / w)
        items = ([head] if head is not None else []) + [img] + ([P(cap, "cap")] if cap else [Spacer(1, 4)])
        return [KeepTogether(items)]

    def SIDE(name, width_mm, paras, cap=""):
        """圖在左,文字在右."""
        if name not in figs:
            return paras
        from PIL import Image as PILImage
        with PILImage.open(figs[name]) as im:
            w, h = im.size
        img = Image(figs[name], width=width_mm * mm, height=width_mm * mm * h / w)
        left = [img] + ([P(cap, "cap")] if cap else [])
        t = Table([[left, paras]], colWidths=[(width_mm + 3) * mm, (180 - width_mm - 3) * mm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        return [t]

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
    story += [P("線控飛機油門控制器 補償功能說明", "title"),
              P(f"照網頁「角度補償」分頁由上到下:每個功能怎麼用、什麼時候用、範例. 對應韌體 {FW} · {DATE}", "sub")]

    # ---------------- 1 總覽
    story += [P("1. 先看這一段:補償在做什麼", "h1")]
    story += [P("飛行中的油門 = <b>基本油門</b>(計時器頁的時間軸)<b>+ 補償</b>,再夾在油門下限與上限之間. 補償讓飛機在爬升、斜上方與頭頂不掉速,俯衝時不衝過頭. "
                "三個補償來源都在<b>角度補償</b>分頁設定,每組飛行風格各自一套:")]
    story += IMG("pipeline", 165, "圖 1:油門怎麼算. 「補償方式」決定用哪幾個來源.")
    story += LI(["<b>機頭角度曲線</b>:機頭抬起多少就加多少油門,機頭朝下就減. 原本就有的功能,反應最快.",
                 "<b>側傾曲線</b>:飛機飛到斜上方、頭頂時(翼軸往下指向飛手),線拉力會變小,這條曲線依「翼軸仰角」加油門. 出廠 0%,要用的人自己拉.",
                 "<b>線軸 G 回授</b>:量飛手手上的拉力(線軸 G),比目標小就加油門,比目標大就減. 不用拉曲線,但反應比曲線慢.",
                 "補償只在<b>飛行中</b>作用:緩啟動、起飛後「不補償秒數」內、降落中、感測器故障時都不補(照時間軸飛)."])

    # ---------------- 2 角度補償頁
    story += [P("2. 角度補償分頁(由上到下)", "h1")]
    story += [P("2.1 飛行風格列(A~E,測試)", "h2"),
              P("點哪一組就編輯哪一組的曲線與補償方式,★ 是飛行使用的那一組(在計時器頁選). 曲線與補償方式是<b>每組各自</b>的:可以 A 組用曲線、B 組用回授,比賽與練習各存一組. "
                "改完任何東西都要按上方的<b>儲存</b>,有未儲存變更不能起飛.")]

    story += [P("2.2 補償方式卡", "h2")]
    story += IMG("comp_mode_card", 150, "圖 2:補償方式卡(出廠「曲線」時,下面四個回授參數變淡表示不作用). 最下一行是目前的線軸 G 讀值.")
    story += [TBL([["補償方式", "什麼時候選", "注意"],
                   ["曲線(機頭 + 側傾)", "出廠值,原本的飛法. 曲線已經調順、不想碰的人就留這個.", "斜上方沒勁要自己拉側傾曲線(2.4 節)."],
                   ["曲線 + 線軸 G 回授微調", "想讓<b>每個方位的拉力一樣</b>,又保留曲線的快速反應. <b>要試回授先選這個.</b>", "曲線照用,回授只在旁邊微調 ±幅度上限."],
                   ["只用線軸 G 回授", "不想拉曲線,只設一個目標拉力.", "分不出爬升與俯衝,要等速度掉了才補;快速特技會慢半拍."]],
                  [40, 82, 58])]
    story += [Spacer(1, 4), P("四個回授參數(選「曲線」時不作用):")]
    story += [TBL([["參數", "出廠", "怎麼調 / 什麼時候調"],
                   ["目標線軸 G", "3.0 g", "你喜歡的拉力手感. <b>先用「曲線」飛一趟,看紀錄頁「飛行中線軸 G」的低空值,填那個數字.</b> 填太高整趟都在加油門,填太低整趟都在減."],
                   ["回授增益", "10 %/g", "線軸 G 每比目標少 1 g 就加幾 % 油門. 頭頂拉力還是不夠就加大;油門一直來回抽就減小."],
                   ["回授幅度上限", "±30%", "回授最多加減幾 %. 小飛機動力餘裕大,±10~15% 就有感;大飛機 ±30% 起. 第一次試飛建議先 ±15%."],
                   ["線軸 G 平滑秒數", "0.5 秒", "濾掉螺旋槳震動用. 讀值抖就加大;加大後反應會變慢. 平常不用動."]],
                  [30, 16, 134])]
    story += IMG("comp_mode_card_fb", 150, "圖 3:選「曲線 + 線軸 G 回授微調」後,最下一行即時算出微調量. 在地上線軸 G 很小,所以算出來的微調很大,這是正常的,飛行中才作用.")
    story += [P("範例:飛手 A 的飛機 B 組用曲線飛,紀錄頁顯示低空平飛線軸 G 3.4 g,頭頂只剩 2.6 g,覺得頭頂沒勁. 把補償方式改「曲線 + 回授」,目標 3.4,增益 10,幅度 ±15. "
                "下一趟頭頂少 0.8 g 時回授會加 8%,低空平飛(等於目標)不動. 還不夠就把增益改 15.", "ex")]

    story += IMG("curve_main", 160, "圖 4:曲線主圖與右側面板. 直軸是機頭角度,橫軸是實際輸出油門.", head=P("2.3 角度補償曲線:第一段 / 第二段", "h2"))
    story += [P("圖上的東西怎麼看:")]
    story += LI(["<b>紅線 + 紅點</b>:目前機頭角度與這個角度會輸出的油門. 拿著飛機抬頭低頭,紅線就動,在地上就能驗證曲線.",
                 "<b>空心圓點</b>:可調的點(每側 1~4 個). 點一下選中(變紅),直接拖,或用右側面板的 +/−(粗調 5,細調 1). <b>實心小點</b>是補速/減速起點(死區邊界),拖左邊的三角形改.",
                 "<b>粗線</b>是實際輸出,<b>虛線</b>是被上下限夾掉前的原始曲線;<b>灰色區域</b>是上下限以外,不會輸出. 下方三個三角形:下限 / 基本油門 / 上限,也可以拖.",
                 "<b>基本油門標籤</b>:曲線從這條線開始加減. 補償值是加在基本油門上的百分比:75% + 8% = 83%.",
                 "<b>第二段</b>頁籤:同一條曲線套上第二段的基本油門,只能拖基本油門,用來看加力後哪裡會撞上限(圖上紅色粗線)."])
    story += SIDE("curve_panel", 56, [P("右側面板(手機上在圖的下方):"),
                                       *LI(["<b>選取框</b>:正在選的點或把手,直接打數字或 +/−.",
                                            "<b>朝上 / 朝下 / 側傾點數</b>:每側 1~4 點. 改點數時各點會重新平均分布,曲線形狀大致不變. 新手 2~3 點就夠.",
                                            "<b>撞牆檢查</b>:列出補償後超過上限或低於下限的角度;被夾掉的部分等於白補. 第二段基本油門高,更容易撞. 最後一行是兩條曲線同時作用的最壞情況.",
                                            "<b>油門上下限</b>(收合):兩段共用. 下限是補償再怎麼減也不會低於的值(最低 10%),上限是再怎麼加也不會超過的值."])],
                  "圖 5:右側面板")
    story += [P("什麼時候調機頭曲線:", "h2")]
    story += LI(["爬升到頂沒勁、筋斗上半圈掉速 → 朝上的點往右拉(加大補償),一次 3~5%. 先動 +70° 與 +90° 的點.",
                 "筋斗頂端衝過頭、方形特技上邊太快 → 朝上的點往左拉.",
                 "俯衝時線鬆、下來收不住 → 朝下的點往左拉(減速多一點);俯衝沒動力、飛機往內掉 → 往右拉.",
                 "補速起點(出廠 +20°):平飛稍微抬頭就加油門的話把它調大;想早一點補就調小. 減速起點出廠 −3°."])
    story += [P("範例:出廠曲線 +70° 補 15%,第一段 75%,飛手覺得爬升到頂還是慢. 把 +70° 的點從 15 拉到 20,+90° 從 20 拉到 25,撞牆檢查顯示第二段(85%)在 +71° 以上撞上限 100%. "
                "這表示第二段頭頂最多只能到 100%,再拉也沒用;要更多就要降第二段基本油門或接受被夾住.", "ex")]

    story += [P("2.4 側傾補償曲線(翼軸仰角)", "h2")]
    story += SIDE("curve_side", 95, [P("<b>什麼時候用</b>:在斜上方(45°~90° 高度)平飛、頭頂八字、高處的水平圈覺得升力不足、線變軟,但爬升本身沒問題(機頭曲線已經夠). "
                                        "這時機頭角度接近 0,機頭曲線幫不上忙,要靠這條."),
                                      P("<b>怎麼用</b>:直軸是翼軸仰角(低空平飛 0°,45° 高度平飛約 45°,正頭頂 90°,正飛倒飛同值). 出廠全部 0%,把 70° 與 90° 的點往右拉開始試. "
                                        "這條與機頭曲線<b>相加</b>:斜著爬升時兩條都有值,看撞牆檢查最後一行."),
                                      P("<b>兩個自動規則</b>:機頭朝下時這條曲線淡出(0° 全額,−45° 以下 0),俯衝交給朝下曲線減速;快速滾轉時關閉,半滾進倒飛不會突然加油門.")],
                  "圖 6:側傾曲線(範例 45°→+4,70°→+8,90°→+12). 紅線是目前翼軸仰角.")
    story += [P("範例:第一次拉側傾曲線建議 45°→+4%,70°→+8%,90°→+12%(約朝上曲線的一半). 效果:30° 高度平飛 +1.6%,60° 高度 +6.4%,頭頂 +12%;"
                "斜著 45° 爬升到 60° 高度時機頭曲線 +8% 加側傾 +6.4% 合計 +14.4%,第一段 75% 變 89%. 飛幾趟後看紀錄頁的 3D 軌跡與線軸 G,頭頂的線軸 G 還是明顯低於低空再加.", "ex")]

    story += [P("2.5 全部點的數值", "h2")]
    story += SIDE("curve_all_points_side", 95, [P("展開後三側(朝上、朝下、側傾)的起點、點數與每一點的角度 / 補償都能直接打數字,不方便拖曳時用(手機上手指太粗、或要輸入精確值). "
                                                   "角度要由小到大,不能越過相鄰的點,韌體會拒絕並提示.")], "圖 7:側傾那一側的數值表")

    # ---------------- 3 計時器頁
    story += [P("3. 計時器頁裡和補償有關的", "h1")]
    story += SIDE("prof_takeoff", 95, [*LI(["<b>起飛後不補償</b>(出廠 3 秒):馬達起轉後這幾秒內曲線與回授都不作用. 後三點飛機停在地上機頭就是朝上的,不擋掉會被當成爬升而加油門. "
                                               "起飛滑跑加速慢的飛機(重、動力小)建議設成實際飛到巡航速度的秒數,例如 5~6 秒;回授方式在這之後還會再用 2 秒漸入.",
                                               "<b>第一段 / 第二段基本油門</b>:曲線與回授都加在它上面. 基本油門越高,往上補的空間越小(撞上限),往下減的空間越大.",
                                               "時間軸圖上的斜線區就是不補償的那幾秒;虛線是油門上下限."])], "圖 8:計時器頁「起飛」群組")

    # ---------------- 4 監看頁
    story += IMG("mon_attitude", 160, "圖 9:機頭角度卡. 右邊四個讀數與下面一行補償預覽,拿著飛機轉動都會即時變.", head=P("4. 監看頁:在地上驗證設定", "h1"))
    story += LI(["<b>機頭角度 / 滾轉 / 翼軸仰角 / 線軸 G</b>:控制器現在量到的值. 翼軸仰角是側傾曲線的輸入;線軸 G 在地上只有重力的分量(0~1 g),飛行中才是拉力.",
                 "<b>補償預覽</b>那一行:「機頭 +x% + 側傾 +y% = 合計」與兩段的實際油門. 回授的微調飛行中才顯示實際值,在地上不預測(地上的線軸 G 沒有意義).",
                 "<b>圖上的紅線與紅點</b>:目前角度在曲線上的位置,背景是第一段(實線)與第二段(虛線)的油門曲線."])
    story += IMG("mon_h3", 150, "圖 10:3D 半球位置. 飛手在中心,飛機的點在半球面上;箭頭是飛行方向,顏色與文字是這個姿態下曲線會加速還是減速. 拖曳可旋轉.")
    story += [P("怎麼用:拿著飛機(不裝槳)模擬各種姿態:左翼往下壓(翼軸仰角變大)點會往頭頂移動,看補償變成綠色加速;機頭往下壓看變紅色減速;斜著爬看兩條相加. "
                "這樣不用飛就能確認曲線在每個位置的行為對不對. 方位角由陀螺儀積分,在地上會慢慢飄,不用理它.")]
    story += IMG("mon_flying_bar", 165, "圖 11:飛行中最上面的狀態列:油門 = 基本 + 補償,括號內另標線軸 G 回授微調了多少.")

    # ---------------- 5 紀錄頁
    story += IMG("log_chart", 160, "圖 12:紀錄圖表. 上:機頭角度(紅)與油門(橘);中:總 G(灰)、<b>線軸 G(藍)</b>、目標 G(藍虛線);下:Z 軸抖動. 點或拖圖表看那一刻的數值.", head=P("5. 紀錄頁:落地後決定下一趟怎麼調", "h1"))
    story += LI(["<b>藍線</b>是線軸 G:低空平飛的高度就是你的拉力基準,拉起時掉多少就是斜上方少了多少拉力. 目標 G 設成低空平飛的值,回授就會在掉下去時補.",
                 "<b>橘線</b>看補償有沒有作用:拉起時油門應該跟著角度抬高;頭頂平飛時油門有沒有比低空高(側傾曲線或回授在作用).",
                 "上面的統計卡有「飛行中線軸 G x~y g」,最小值在哪裡發生,點圖表找出來."])
    story += SIDE("log_h3", 95, [P("<b>3D 飛行軌跡</b>:目前視窗的軌跡畫在半球上,顏色是油門(藍低、紅高),點圖表某一時刻,軌跡上會有白點. 用來看「哪個位置油門推到多少」:頭頂那一圈如果還是黃綠色,表示補償不夠. "
                                    "方位角會慢慢轉偏,看幾秒內的動作形狀就好."),
                                  P("<b>定目標 G 的步驟</b>:1) 用「曲線」飛一趟 → 2) 看統計「飛行中線軸 G」與藍線低空值 → 3) 目標 G 填低空值,改「曲線 + 回授」,幅度 ±15 → 4) 再飛一趟看藍線有沒有變平,頭頂油門(橘線)有沒有抬高.")],
                  "圖 13:3D 飛行軌跡")

    # ---------------- 6 範例
    story += [KeepTogether([P("6. 三個完整範例", "h1"), TBL([["情境", "設定", "預期結果 / 怎麼確認"],
                   ["小飛機,曲線已順,只有頭頂八字沒勁", "補償方式「曲線」. 側傾曲線 45°→+3,70°→+6,90°→+10. 其他不動.",
                    "頭頂 +10%,低空不變. 監看頁壓左翼看補償變綠;飛完看紀錄頁頭頂那段橘線比低空高 10%."],
                   ["大飛機,動力餘裕小,各方位拉力差很多", "先「曲線」飛一趟得低空線軸 G(例 3.2). 改「曲線 + 回授」,目標 3.2,增益 10,幅度 ±30,起飛後不補償 5 秒.",
                    "斜上方少 1 g 加 10%,少 2 g 加 20%. 紀錄頁藍線應該比上一趟平. 油門抽動就把增益降到 7 或平滑秒數加到 0.8."],
                   ["不想拉曲線,先求穩", "「只用線軸 G 回授」,目標 = 低空值,增益 8,幅度 ±20. 朝上 / 朝下曲線不用管.",
                    "平飛與大圈很準;快速筋斗會慢半拍(要等速度掉了才補). 覺得特技不夠跟手就改回「曲線 + 回授」."]],
                  [42, 68, 70])])]

    # ---------------- 7 物理補充
    story += [P("7. 補充:翼軸仰角與線軸 G 到底是什麼", "h1")]
    story += IMG("geom", 150, "圖 14:左:飛機在半球面上,翼軸(線的方向)與地平線的夾角是翼軸仰角 ε;右:機頭角度是機身相對地平線的俯仰.")
    story += [P("飛機被線拉著在半球面上繞,線拉力 = 離心力 V²/R 減掉重力順著線的分量 g·sin ε. 飛到斜上方 ε 變大,拉力就變小,正頭頂少掉整整 1 g;以線長 18 m、單圈 4 秒為例,低空約 4.5 g,頭頂只剩 3.5 g,"
                "要維持同樣拉力頭頂要快約 10%. 加速度計沿翼軸量到的就是這個拉力(線軸 G),任何動作中都成立,所以回授不需要線長、單圈秒數或油門模型. "
                "爬升時重力還會拖慢飛機,那部分靠機頭曲線.")]
    story += SIDE("fade", 80, [P("側傾補償為什麼要在機頭朝下時淡出:斜上方往下俯衝時,側傾(正)會抵銷朝下曲線(負),出廠值甚至變成加油門. 淡出後俯衝完全交給朝下曲線. "
                                 "快速滾轉時翼軸會掃過鉛直方向,翼軸仰角短暫衝到 90°,所以滾轉率 90~180 °/s 時也淡到 0.")], "圖 15:機頭朝下時側傾補償的倍率")
    story += [P("已知限制:只回授方式分不出爬升與俯衝;只有一個目標 G,第二段多加的基本油門會被回授拉回一些;目標 G 與安裝頁的線長/單圈秒數差很多時,姿態讀值會偏 3~5°(低於出廠死區). "
                "從 2026.10.29.1 升級上來的板子,側傾曲線會是當時複製的朝上曲線,不是 0%,請到角度補償頁檢查.", "note")]
    story += [P(f"文件由 tools/comp_manual_pdf.py 產生(截圖 tools/web_mock.py + tools/comp_manual_shots.js),數值對照韌體 {FW}. 完整使用說明見 docs/使用說明書.md.", "cap")]
    doc.build(story)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", f"補償功能說明_{DATE}.pdf")
    print("寫出", build(out))
