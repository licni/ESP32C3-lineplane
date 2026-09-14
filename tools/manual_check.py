# 版本流水號: r2 (2026-09-14) 加安全開關等待上限;出廠值寫成常數(例如 ARM_WAIT_DEFAULT_MIN)時從 settings.h 讀常數值
# 舊: r1 (2026-09-14) 初版:使用說明書的目錄產生與內容核對
# ============================================================================
# docs/使用說明書.md 的維護工具. 改了參數表(src/settings.cpp)或說明書之後跑一次:
#   1. 依 GitHub 錨點規則重新產生目錄(<!-- TOC --> 到 <!-- /TOC --> 之間),重跑不會改動沒變的檔案
#   2. 內部連結 #錨點 都要對得到標題;<img> 圖片檔要存在
#   3. 表格裡每個參數列的出廠值,範圍,細調/粗調,與 settings.cpp 的參數表和出廠預設一致;補償曲線出廠點一致
#   4. Markdown 檢查:表格每列欄數一致,提示框語法,程式碼區塊成對,目錄只有一份
# 用法:python tools/manual_check.py   (全部通過回 0)
# 新增參數時,說明書要補表格列,並把「畫面名稱 → 參數鍵」加進下面的 NAME.
# ============================================================================
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "docs", "使用說明書.md")
text = open(MD, encoding="utf-8").read()
ok = True


def bad(msg):
    global ok
    ok = False
    print("FAIL", msg)


# ---- 標題與錨點(GitHub 規則:轉小寫,去掉標點,空白換成 -)----
PUNCT = re.compile(r"[\u0000-\u001f!-,./:-@\[-\^`{-~\u00a0-\u00bf\u00d7\u00f7\u2000-\u206f\u3000-\u303f\uff00-\uffef]")


def slug(t):
    return PUNCT.sub("", t.strip().lower()).replace(" ", "-")


heads = []
in_code = False
for line in text.split("\n"):
    if line.startswith("```"):
        in_code = not in_code
        continue
    if not in_code:
        m = re.match(r"^(#{2,3}) (.+?)\s*$", line)
        if m:
            heads.append((len(m.group(1)), m.group(2)))
seen, anchors = {}, []
for lv, t in heads:
    s = slug(t)
    n = seen.get(s, 0)
    seen[s] = n + 1
    anchors.append((lv, t, s if n == 0 else f"{s}-{n}"))
anchor_set = {a for _, _, a in anchors}

toc, in_appendix = [], False
for lv, t, a in anchors:
    if t == "目錄":
        continue
    if lv == 2:
        in_appendix = t.startswith("附錄")
        toc.append(f"- [{t}](#{a})")
    elif not in_appendix:
        toc.append(f"  - [{t}](#{a})")
toc_md = "<!-- TOC -->\n" + "\n".join(toc) + "\n<!-- /TOC -->"
if "<!-- /TOC -->" in text:
    new = re.sub(r"<!-- TOC -->.*<!-- /TOC -->", lambda _: toc_md, text, count=1, flags=re.S)
else:
    new = text.replace("<!-- TOC -->", toc_md, 1)
if new != text:
    open(MD, "w", encoding="utf-8", newline="\n").write(new)
    text = new
    print("目錄已更新")
print(f"標題 {len(anchors)} 個,目錄 {len(toc)} 行")

# ---- 內部連結與圖片 ----
links = re.findall(r"\]\(#([^)]+)\)", text)
for l in sorted({l for l in links if l not in anchor_set}):
    bad(f"連結錨點不存在:#{l}")
print(f"內部連結 {len(links)} 個")
for src in re.findall(r'<img src="([^"]+)"', text):
    if not os.path.isfile(os.path.join(ROOT, "docs", src)):
        bad(f"圖片不存在:{src}")

# ---- 參數對照 settings.cpp ----
cpp = open(os.path.join(ROOT, "src", "settings.cpp"), encoding="utf-8").read()
hdr = open(os.path.join(ROOT, "src", "settings.h"), encoding="utf-8").read()
CONST = {m.group(1): m.group(2) for m in re.finditer(r"\bconst\s+\w+\s+([A-Z_]+)\s*=\s*(-?[\d.]+)f?;", hdr)}


def cnum(s):
    return float(CONST.get(s, s).rstrip("f"))


params = {}
for m in re.finditer(r'(SP|PP)\("(\w+)", PARAM_\w+, ([\w.\[\]]+), ([-\w.f]+), ([-\w.f]+), ([\w.f]+), ([\w.f]+)\)', cpp):
    params[m.group(2)] = dict(field=m.group(3), mn=cnum(m.group(4)), mx=cnum(m.group(5)), fine=cnum(m.group(6)), coarse=cnum(m.group(7)))
defaults = {}
for m in re.finditer(r"\b[sp]\.([\w.\[\]]+) = (-?[\d.]+|[A-Z_]+)f?;", cpp):
    if m.group(2)[0].isdigit() or m.group(2)[0] == "-" or m.group(2) in CONST:
        defaults.setdefault(m.group(1), cnum(m.group(2)))

# 說明書(網頁)上的參數名稱 → settings.cpp 參數鍵. 選單類參數(開關,方式)不在這裡.
NAME = {"起飛前水平限制": "startLevel", "啟動手勢力道": "gestureG", "扭轉機尾取消起飛": "twistCancel", "取消後暫停手勢": "twistBlock",
        "安全開關等待上限": "armWait", "倒數秒數": "countdownSec", "外力門檻": "disturbG", "延長秒數": "extendSec", "Z 軸抖動門檻": "earlyLandVib",
        "抖動持續秒數": "earlyLandHold", "正飛水平容許角度": "earlyLandTilt", "起飛後幾秒才啟用": "earlyLandArm",
        "降落觸地衝擊門檻": "touchdownG", "觸地靜止判定": "touchdownStill", "降落保險時間": "landingTimeout", "撞擊門檻": "crashG",
        "角度修正": "pitchTrim", "線長": "lineLength", "單圈秒數": "lapSec", "起飛後幾秒收輪": "gearRetractSec",
        "舵機速度": "gearTravelSec", "舵機行程下限": "gearMinUs", "舵機行程上限": "gearMaxUs", "PWM 頻率": "escPwmHz",
        "馬達極數": "motorPoles", "油門 0% 脈寬": "escMinUs", "油門 100% 脈寬": "escMaxUs", "最高油門保持秒數": "calibHold",
        "緩啟動加力秒數": "takeoffRamp", "起飛後不補償": "noCompSec", "第一段基本油門": "phase1Pct", "第一段持續時間": "phase1Sec",
        "換段加力秒數": "phaseRamp", "第二段基本油門": "phase2Pct", "總飛行時間": "flightSec", "降落減力秒數": "landingRamp",
        "降落油門": "landingPct", "飛行中油門下限": "minPct", "飛行中油門上限": "maxPct", "補速開始角度": "upDb", "減速開始角度": "dnDb"}
FIELD_DEFAULT = {"upDb": "up.deadband", "dnDb": "down.deadband"}
NUM = r"[−-]?\+?\d+(?:\.\d+)?"


def fnum(s):
    return float(s.replace("−", "-").replace("+", ""))


rows, checked = 0, set()
for line in text.split("\n"):
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 3 or cells[0] not in NAME or not re.search(r"\d", cells[1]):
        continue   # 不是參數列(例如兩種啟動方式的對照表)
    key = NAME[cells[0]]
    if key not in params:
        bad(f"settings.cpp 找不到參數 {key}({cells[0]})")
        continue
    p = params[key]
    want = defaults.get(FIELD_DEFAULT.get(key, p["field"]))
    rows += 1
    checked.add(key)
    d = re.search(NUM, re.sub(r"\(\d+:\d{2}\)", "", cells[1]))
    if not d or fnum(d.group(0)) != want:
        bad(f"{cells[0]} 出廠值 {cells[1]!r},原始碼是 {want}")
    rng = cells[2]
    if key == "twistCancel":
        r = re.search(r"~\s*(" + NUM + ")", rng)
        lo, hi = 0.0, fnum(r.group(1)) if r else None
    else:
        r = re.search(r"(" + NUM + r")\s*~\s*(" + NUM + ")", rng)
        lo, hi = (fnum(r.group(1)), fnum(r.group(2))) if r else (None, None)
    if (lo, hi) != (p["mn"], p["mx"]):
        bad(f"{cells[0]} 範圍 {rng!r},原始碼是 {p['mn']:g}~{p['mx']:g}")
    if len(cells) > 3 and re.fullmatch(r"[\d.]+ / [\d.]+", cells[3]):
        fi, co = (float(x) for x in cells[3].split(" / "))
        if (fi, co) != (p["fine"], p["coarse"]):
            bad(f"{cells[0]} 步進 {cells[3]!r},原始碼是 {p['fine']:g} / {p['coarse']:g}")
    for word, k in (("細調", "fine"), ("粗調", "coarse")):
        sm = re.search(word + r" ([\d.]+)", rng)
        if sm and float(sm.group(1)) != p[k]:
            bad(f"{cells[0]} {word} {sm.group(1)},原始碼是 {p[k]:g}")
for name, key in NAME.items():
    if key not in checked:
        bad(f"說明書的表格裡沒有「{name}」")
for side, pts in (("up", [(45, 8), (70, 15), (90, 20)]), ("down", [(-30, -10), (-60, -20), (-90, -25)])):
    for i, (a, c) in enumerate(pts):
        m = re.search(rf"\bp\.{side}\.pts\[{i}\] = \{{(-?\d+), (-?\d+)\}};", cpp)
        if not m or (int(m.group(1)), int(m.group(2))) != (a, c):
            bad(f"補償曲線 {side} 點 {i + 1}:說明書 {a}°/{c}%,原始碼 {m.groups() if m else '找不到'}(說明書 10.4 與附錄 A 要一起改)")
print(f"參數表格 {rows} 列,涵蓋 {len(checked)} / {len(NAME)} 個參數")

# ---- Markdown 檢查 ----
lines = text.split("\n")
i = tables = 0
while i < len(lines):
    if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-| ]+\|$", lines[i + 1]):
        tables += 1
        cols = lines[i].count("|")
        j = i
        while j < len(lines) and lines[j].startswith("|"):
            if lines[j].count("|") != cols:
                bad(f"表格欄數不一致 第 {j + 1} 行")
            j += 1
        i = j
    else:
        i += 1
if sum(1 for l in lines if l.startswith("```")) % 2:
    bad("程式碼區塊 ``` 沒有成對")
for k, l in enumerate(lines):
    if l.startswith("> [!") and not re.match(r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]$", l):
        bad(f"提示框語法 第 {k + 1} 行")
if (text.count("<!-- TOC -->"), text.count("<!-- /TOC -->"), sum(1 for l in lines if l.startswith("- [1. "))) != (1, 1, 1):
    bad("目錄標記或目錄重複")
print(f"表格 {tables} 個")
print("結果:", "全部通過" if ok else "有失敗")
sys.exit(0 if ok else 1)
