# 版本流水號: r1 (2026-09-14) 初版:使用說明書 Markdown → 網頁(發布成 claude.ai 私人 Artifact 給使用者看)
# ============================================================================
# 讀 docs/使用說明書.md,輸出單一 HTML(樣式 manual_page.css,互動 manual_page.js 內嵌),截圖放同目錄 images/.
# 只處理說明書用到的語法;標題 id 用 GitHub 錨點規則,說明書的內部連結原樣可用. 流程圖用 <pre class="mermaid">,由 Artifact 平台繪製.
# 用法:python tools/manual_page/build.py → 印出輸出路徑;發布時 images/*.png 對應 docs/images/*.png.
# 改說明書後先跑 tools/manual_check.py,再跑這支重新產生.
# ============================================================================
import html
import os
import re
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "docs", "使用說明書.md")
OUT_DIR = os.path.join(tempfile.gettempdir(), "lineplane_manual")
OUT = os.path.join(OUT_DIR, "lineplane_manual.html")

PUNCT = re.compile(r"[\u0000-\u001f!-,./:-@\[-\^`{-~\u00a0-\u00bf\u00d7\u00f7\u2000-\u206f\u3000-\u303f\uff00-\uffef]")


def slug(t):
    return PUNCT.sub("", t.strip().lower()).replace(" ", "-")


def inline(t):
    codes = []

    def keep_code(m):
        codes.append(m.group(1))
        return f"\u0000{len(codes) - 1}\u0000"

    t = re.sub(r"`([^`]+)`", keep_code, t)
    t = html.escape(t, quote=False)

    def link(m):
        text, url = m.group(1), m.group(2)
        if url.startswith("#"):
            return f'<a href="{html.escape(url)}">{text}</a>'
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{text}</a>'

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", t)
    t = re.sub("\u0000(\\d+)\u0000", lambda m: f"<code>{html.escape(codes[int(m.group(1))])}</code>", t)
    return t


LED = [("熄滅", "off", "熄滅"), ("長亮", "on", "長亮"), ("急閃", "reject blink", "急閃"), ("慢閃", "slow blink", "慢閃"),
       ("快閃", "fast blink", "快閃"), ("閃 2 下", "two blink", "閃 2 下停一下"), ("閃 3 下", "three blink", "閃 3 下停一下"),
       ("極快閃", "rapid blink", "極快閃")]


def led_cell(text):
    for key, cls, _ in LED:
        if text.startswith(key):
            return f'<span class="ledcell"><span class="led {cls}" aria-hidden="true"></span><span>{inline(text)}</span></span>'
    return inline(text)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render_table(rows):
    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]]
    led_cols = {i for i, h in enumerate(head) if h in ("燈號", "狀態燈")}
    out = [f'<div class="table-wrap"><table data-cols="{len(head)}">', "<thead><tr>"]
    out += [f"<th>{inline(h)}</th>" for h in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{led_cell(c) if i in led_cols else inline(c)}</td>" for i, c in enumerate(r)) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def render_list(block):
    root = {"indent": -1, "children": []}
    stack = [root]
    for ln in block:
        m = ITEM.match(ln)
        if m:
            indent = len(m.group(1))
            while len(stack) > 1 and stack[-1]["indent"] >= indent:
                stack.pop()
            node = {"indent": indent, "ordered": m.group(2)[0].isdigit(), "text": m.group(3), "children": []}
            stack[-1]["children"].append(node)
            stack.append(node)
        else:
            stack[-1]["text"] += " " + ln.strip()

    def emit(children):
        out, i = [], 0
        while i < len(children):
            ordered = children[i]["ordered"]
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>")
            while i < len(children) and children[i]["ordered"] == ordered:
                c = children[i]
                out.append(f"<li>{inline(c['text'])}{emit(c['children']) if c['children'] else ''}</li>")
                i += 1
            out.append(f"</{tag}>")
        return "".join(out)

    return emit(root["children"])


ALERT = {"WARNING": ("warn-danger", "警告"), "CAUTION": ("warn-caution", "注意"), "IMPORTANT": ("warn-important", "重要"),
         "TIP": ("warn-tip", "提示"), "NOTE": ("warn-note", "說明")}


def is_block_start(line, nxt):
    return (line.startswith("#") or line.startswith("```") or line.startswith(">") or line.startswith("<") or ITEM.match(line)
            or line.strip() == "---" or (line.startswith("|") and nxt is not None and re.match(r"^\|[-| ]+\|$", nxt.strip())))


def render_blocks(lines, headings):
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        nxt = lines[i + 1] if i + 1 < n else None
        if not line.strip() or line.strip() == "---":
            i += 1
            continue
        if line.startswith("<!-- TOC -->"):
            while i < n and not lines[i].startswith("<!-- /TOC -->"):
                i += 1
            i += 1
            continue
        if line.startswith("<!--"):
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            j = i + 1
            body = []
            while j < n and not lines[j].startswith("```"):
                body.append(lines[j])
                j += 1
            text = html.escape("\n".join(body))
            out.append(f'<div class="diagram"><pre class="mermaid">{text}</pre></div>' if lang == "mermaid" else f"<pre><code>{text}</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{2,3}) (.+?)\s*$", line)
        if m:
            level, title = len(m.group(1)), m.group(2)
            if title == "目錄":
                i += 1
                continue
            hid = slug(title)
            nm = re.match(r"^(\d+(?:\.\d+)?)\.?\s+(.*)$", title) or re.match(r"^(附錄 [A-Z])\s+(.*)$", title)
            no, name = (nm.group(1), nm.group(2)) if nm else ("", title)
            headings.append((level, no, name, hid))
            label = f'<span class="no">{html.escape(no)}</span>' if no else ""
            out.append(f'<h{level} id="{html.escape(hid)}">{label}<span class="ht">{inline(name)}</span></h{level}>')
            i += 1
            continue
        if line.startswith("|") and nxt is not None and re.match(r"^\|[-| ]+\|$", nxt.strip()):
            j = i
            rows = []
            while j < n and lines[j].startswith("|"):
                rows.append(lines[j])
                j += 1
            out.append(render_table(rows))
            i = j
            continue
        if line.startswith(">"):
            j = i
            inner = []
            while j < n and lines[j].startswith(">"):
                inner.append(re.sub(r"^> ?", "", lines[j]))
                j += 1
            am = re.match(r"^\[!(\w+)\]$", inner[0].strip()) if inner else None
            if am and am.group(1) in ALERT:
                cls, label = ALERT[am.group(1)]
                out.append(f'<aside class="callout {cls}"><span class="tag">{label}</span>{render_blocks(inner[1:], headings)}</aside>')
            else:
                out.append(f'<blockquote class="screen">{render_blocks(inner, headings)}</blockquote>')
            i = j
            continue
        if line.startswith("<img"):
            src = re.search(r'src="([^"]+)"', line).group(1)
            alt = re.search(r'alt="([^"]*)"', line)
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            cap = ""
            if j < n and re.match(r"^\*[^*].*\*$", lines[j].strip()):
                cap = lines[j].strip()[1:-1]
                i = j + 1
            else:
                i += 1
            out.append(f'<figure class="shot"><img src="{html.escape(src)}" alt="{html.escape(alt.group(1) if alt else "")}" loading="lazy">'
                       + (f"<figcaption>{inline(cap)}</figcaption>" if cap else "") + "</figure>")
            continue
        if ITEM.match(line):
            j = i
            block = []
            while j < n and lines[j].strip() and (ITEM.match(lines[j]) or lines[j].startswith(" ")):
                block.append(lines[j])
                j += 1
            out.append(render_list(block))
            i = j
            continue
        j = i
        para = []
        while j < n and lines[j].strip() and (j == i or not is_block_start(lines[j], lines[j + 1] if j + 1 < n else None)):
            para.append(lines[j].strip())
            j += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
        i = j
    return "".join(out)


md = open(SRC, encoding="utf-8").read().replace("\r\n", "\n")
lines = md.split("\n")
# 開頭:H1 到第一個 ## 之間是刊頭(適用韌體,適用對象,警告)
h1 = next(k for k, l in enumerate(lines) if l.startswith("# "))
first_h2 = next(k for k, l in enumerate(lines) if l.startswith("## "))
head_lines = lines[h1 + 1:first_h2]
meta, rest, k = [], [], 0
while k < len(head_lines):
    l = head_lines[k]
    mm = re.match(r"^\*\*(適用\S+?)\*\*[::](.*)$", l)
    if mm:
        text = mm.group(2).strip()
        while k + 1 < len(head_lines) and head_lines[k + 1].strip() and not head_lines[k + 1].startswith((">", "**", "#")):
            k += 1
            text += " " + head_lines[k].strip()
        meta.append((mm.group(1), text))
    else:
        rest.append(l)
    k += 1
headings = []
head_html = render_blocks(rest, headings)
body_html = render_blocks(lines[first_h2:], headings)
ver = re.search(r"\d{4}\.\d{2}\.\d{2}\.\d+", md).group(0)

rail = "".join(f'<li><a href="#{html.escape(h)}"><span class="no">{html.escape(no)}</span>{inline(name)}</a></li>' for lv, no, name, h in headings if lv == 2)
mob, open_sub = [], False
for lv, no, name, h in headings:
    if lv == 2:
        if open_sub:
            mob.append("</ul></li>")
            open_sub = False
        mob.append(f'<li><a href="#{html.escape(h)}"><span class="no">{html.escape(no)}</span>{inline(name)}</a>')
        nxt_is_sub = False
        idx = headings.index((lv, no, name, h))
        if idx + 1 < len(headings) and headings[idx + 1][0] == 3 and not no.startswith("附錄"):
            mob.append("<ul>")
            open_sub = True
        else:
            mob.append("</li>")
    elif open_sub:
        mob.append(f'<li><a href="#{html.escape(h)}"><span class="no">{html.escape(no)}</span>{inline(name)}</a></li>')
if open_sub:
    mob.append("</ul></li>")
mobile_toc = "".join(mob)

meta_html = "".join(f"<div><dt>{html.escape(k)}</dt><dd>{inline(v)}</dd></div>" for k, v in meta)

CSS = open(os.path.join(HERE, "manual_page.css"), encoding="utf-8").read()
JS = open(os.path.join(HERE, "manual_page.js"), encoding="utf-8").read()

page = f"""<title>線控飛機油門控制器 使用說明書</title>
<meta name="description" content="ESP32-C3 線控特技機油門控制器的使用說明:接線,連線,參數與設計用意,起飛操作,疑難排解.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=B612+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<style>
{CSS}
</style>
<div class="shell">
<nav class="rail" aria-label="章節">
<p class="rail-title">目錄</p>
<ol>{rail}</ol>
</nav>
<main class="doc" id="top">
<header class="masthead">
<p class="kicker"><span>ESP32-C3 SuperMini</span><span>MPU6050</span><span>電動線控特技機</span></p>
<h1>線控飛機油門控制器<span class="h1-sub">使用說明書</span></h1>
<dl class="meta">{meta_html}</dl>
{head_html}
</header>
<details class="toc-mobile" id="toc-mobile">
<summary>目錄 <span class="toc-hint">(點開跳到章節)</span></summary>
<ol>{mobile_toc}</ol>
</details>
<article class="content">
{body_html}
</article>
<footer class="colophon">
<p class="credit"><span>設計開發者 <strong class="gg">SuperGG</strong></span><span>Line 社群 <strong class="line">RotorFlightTW</strong></span></p>
<p>適用韌體 <code>{ver}</code> 以後 · 韌體更新 <a href="https://github.com/licni/ESP32lineplane-firmware" target="_blank" rel="noopener">ESP32lineplane-firmware</a> · 原始碼 <a href="https://github.com/licni/ESP32C3-lineplane" target="_blank" rel="noopener">ESP32C3-lineplane</a>(GPL-3.0)</p>
</footer>
</main>
</div>
<a class="toc-fab" href="#toc-mobile">目錄</a>
<script>
{JS}
</script>
"""
os.makedirs(os.path.join(OUT_DIR, "images"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "docs", "images")):
    shutil.copyfile(os.path.join(ROOT, "docs", "images", f), os.path.join(OUT_DIR, "images", f))   # 本機預覽用
open(OUT, "w", encoding="utf-8", newline="\n").write(page)
print("寫入", OUT, len(page.encode("utf-8")), "位元組;標題", len(headings), "個")
