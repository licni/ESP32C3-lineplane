# 版本流水號: r4 (2026-09-14) 每天只留最新一版(GG):同一天的舊 Release/tag/韌體檔刪掉,當天修改合併進最新版的 Release 與 CHANGELOG;--cleanup-only 整理現有版本
# 舊: r3 (2026-09-14) 韌體檔集中放 firmware/ 資料夾,首頁舊檔搬進去;manifest file 帶資料夾
# 舊: r2 (2026-09-14) 發布說明必填:CHANGELOG.md,commit 訊息,GitHub Release;--release-only
# 舊: r1 (2026-09-14) 初版:發布韌體到公開專案 licni/ESP32lineplane-firmware(板子「檢查更新」讀這裡)
# ============================================================================
# 版本號格式 年.月.日.當天第幾版(src/version.h 的 FW_VERSION). 規則:
#  - 說明一定要寫(GG:GitHub 上要說明修正了什麼).
#  - **每天只留最新一版**(GG 2026-09-14):發布 2026.09.14.9 時,2026.09.14.1~8 的 GitHub Release 與 tag 刪除,
#    firmware/ 裡當天的舊檔刪除;CHANGELOG.md 當天只留一個條目,內容是當天所有修改的合併.
#  - firmware/ 只留最近 KEEP_DAYS 天(每天一個檔);更早的版本在 Releases 下載.
#
# 說明分兩份:
#   --notes           板子網頁顯示(manifest notes),最多 400 位元組. 同一天再發布時寫「當天合併後的重點」.
#   --day-notes-file  GitHub Release 與 CHANGELOG 用的「當天所有修改」完整條列(不限長度).
#                     不給時自動合併:這次 --notes 的條目 + 當天之前條目的內容(去掉重複).
#                     自動合併會保留已被取代的舊條目,發布前請看一下,需要時自己寫合併檔.
# 用法:
#   penv python tools/publish_firmware.py --notes "..." [--day-notes-file 當天修改.md]
#   penv python tools/publish_firmware.py --cleanup-only --notes "..." --day-notes-file 當天修改.md   (不重新發布,只整理)
#   加 --no-build 用現有的 .pio/build 檔案;加 --dry-run 只顯示不推送.
# 本機複本在 firmware_release/(主專案 .gitignore 排除). 第一次會自動 clone.
# ============================================================================
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join(ROOT, "firmware_release")
REPO = "licni/ESP32lineplane-firmware"
ENV = "esp32c3_supermini"
FWDIR = "firmware"   # 韌體檔資料夾(manifest.json 留在首頁當板子的入口)
KEEP_DAYS = 3
PIO = os.path.join(os.environ.get("USERPROFILE", ""), ".platformio", "penv", "Scripts", "pio.exe")
VER_RE = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$")


def run(cmd, cwd=None, check=True):
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        sys.exit(f"指令失敗:{' '.join(cmd)}")
    return r


def fw_version():
    with open(os.path.join(ROOT, "src", "version.h"), encoding="utf-8") as f:
        m = re.search(r'#define\s+FW_VERSION\s+"([^"]+)"', f.read())
    if not m:
        sys.exit("src/version.h 找不到 FW_VERSION")
    v = m.group(1)
    if not VER_RE.match(v):
        sys.exit(f"版本號格式不對:{v}(要是 年.月.日.第幾版,例如 2026.09.14.1)")
    return v


def day_of(ver):
    """版本號 → (日期前綴 '2026.09.14', 顯示日期 '2026-09-14', 當天序號). 格式不符回 None."""
    m = VER_RE.match(ver)
    if not m:
        return None
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}", f"{m.group(1)}-{m.group(2)}-{m.group(3)}", int(m.group(4))


def bullets(text):
    return [line if line.startswith("- ") else f"- {line}" for line in (x.strip() for x in text.splitlines()) if line]


def changelog_read():
    path = os.path.join(REL, "CHANGELOG.md")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    entries = []   # [(版本, 內容)]
    for m in re.finditer(r"(?ms)^## (\S+?)(?:(.*?))?\n(.*?)(?=^## |\Z)", text):
        entries.append((m.group(1), m.group(3).strip()))
    return entries


def changelog_write(ver, day_text):
    """當天只留一個條目(內容 = day_text),其他天的條目照舊."""
    day, date, _ = day_of(ver)
    entries = [(v, body) for v, body in changelog_read() if not v.startswith(day + ".")]
    out = "# 更新紀錄\n\n每天只留最新一版,當天的修改都合併在那一版. 最新在最上面.\n\n"
    out += f"## {ver}({date})\n\n{day_text.strip()}\n\n"
    for v, body in entries:
        d = day_of(v)
        out += f"## {v}({d[1] if d else ''})\n\n{body}\n\n"
    with open(os.path.join(REL, "CHANGELOG.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)


def merged_day_text(ver, notes, day_notes_file):
    if day_notes_file:
        with open(day_notes_file, encoding="utf-8-sig") as f:
            return f.read().strip()
    day = day_of(ver)[0]
    lines = bullets(notes)
    for v, body in changelog_read():
        if v.startswith(day + ".") and v != ver:
            for line in bullets(body):
                if line not in lines:
                    lines.append(line)
    return "\n".join(lines)


def release(ver, day_text, asset):
    """GitHub Release「韌體 版本」,說明 = 當天合併的修改,附韌體檔. 已存在就更新說明."""
    tag = f"v{ver}"
    body = day_text + "\n\n---\n板子網頁「系統 → 韌體更新 → 檢查更新」即可更新. 手動更新:下載下面的 .bin,到「手動上傳韌體檔」上傳."
    if run(["gh", "release", "view", tag, "-R", REPO], check=False).returncode == 0:
        run(["gh", "release", "edit", tag, "-R", REPO, "--title", f"韌體 {ver}", "--notes", body, "--latest"])
    else:
        run(["gh", "release", "create", tag, os.path.join(REL, asset), "-R", REPO, "--title", f"韌體 {ver}", "--notes", body, "--latest"])


def prune_releases(ver):
    """每天只留最新一版:刪同一天較舊的 GitHub Release 與 tag(新版 Release 建好之後才呼叫)."""
    day, _, seq = day_of(ver)
    r = run(["gh", "release", "list", "-R", REPO, "--limit", "200", "--json", "tagName"])
    for tag in [x["tagName"] for x in json.loads(r.stdout or "[]")]:
        d = day_of(tag[1:]) if tag.startswith("v") else None
        if d and d[0] == day and d[2] < seq:
            run(["gh", "release", "delete", tag, "-R", REPO, "--yes", "--cleanup-tag"])
            print("  刪除同一天的舊版 Release", tag)


def prune_files():
    """firmware/ 每天只留最新一個檔,而且只留最近 KEEP_DAYS 天(commit 前呼叫)."""
    by_day = {}
    for b in glob.glob(os.path.join(REL, FWDIR, "firmware-*.bin")):
        d = day_of(os.path.basename(b)[len("firmware-"):-len(".bin")])
        if not d:
            continue
        by_day.setdefault(d[0], []).append((d[2], b))
    days = sorted(by_day, reverse=True)
    for i, dd in enumerate(days):
        files = sorted(by_day[dd])
        drop = files if i >= KEEP_DAYS else files[:-1]   # 保留天數內每天留最新一個
        for _, b in drop:
            os.remove(b)
            print("  刪除韌體檔", os.path.basename(b))


def check_notes(notes):
    if not notes:
        sys.exit("一定要寫更新說明(--notes):GitHub 上要說明這版修正了什麼")
    if len(notes.encode("utf-8")) > 400:
        sys.exit(f"--notes 太長:{len(notes.encode('utf-8'))} 位元組,板子最多顯示 400(中文一字 3 位元組). 完整內容放 --day-notes-file")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", default="")
    ap.add_argument("--day-notes-file")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cleanup-only", action="store_true", help="不重新發布,只對目前公開的版本套用每天一版與合併說明")
    a = ap.parse_args()
    notes = a.notes.replace("\\n", "\n").strip()
    check_notes(notes)
    if not os.path.isdir(os.path.join(REL, ".git")):
        if os.path.isdir(REL) and os.listdir(REL):
            sys.exit("firmware_release/ 存在但不是 git 複本,請先處理")
        run(["gh", "repo", "clone", REPO, REL])
    run(["git", "pull", "--ff-only"], cwd=REL)
    mpath = os.path.join(REL, "manifest.json")
    old = {}
    if os.path.exists(mpath):
        with open(mpath, encoding="utf-8") as f:
            old = json.load(f)

    if a.cleanup_only:
        ver = old.get("version", "")
        if not day_of(ver):
            sys.exit(f"公開版本號格式不對:{ver}")
        day_text = merged_day_text(ver, notes, a.day_notes_file)
        print(f"== 整理 {ver}\n{day_text}")
        if a.dry_run:
            return
        old["notes"] = notes
        with open(mpath, "w", encoding="utf-8", newline="\n") as f:
            json.dump(old, f, ensure_ascii=False, indent=2)
            f.write("\n")
        prune_files()
        changelog_write(ver, day_text)
        run(["git", "add", "-A"], cwd=REL)
        run(["git", "commit", "-m", f"整理:每天只留最新一版,{ver} 合併當天修改\n\n{day_text}"], cwd=REL, check=False)
        run(["git", "push"], cwd=REL)
        release(ver, day_text, old["file"])
        prune_releases(ver)
        print(f"== 已整理:{day_of(ver)[1]} 只留 {ver}")
        return

    ver = fw_version()
    print(f"== 發布韌體 {ver}")
    if old.get("version") == ver:
        sys.exit(f"公開專案上已經是 {ver}:請先改 src/version.h 的 FW_VERSION")
    if not a.no_build:
        run([PIO, "run", "-e", ENV], cwd=ROOT)
    src = os.path.join(ROOT, ".pio", "build", ENV, "firmware.bin")
    with open(src, "rb") as f:
        data = f.read()
    if ver.encode() not in data:
        sys.exit(f"編譯出的韌體裡找不到版本字串 {ver}:可能沒有重新編譯,請不要用 --no-build")
    name = f"firmware-{ver}.bin"
    manifest = {"version": ver, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(), "file": f"{FWDIR}/{name}", "notes": notes}
    day_text = merged_day_text(ver, notes, a.day_notes_file)
    print(f"  大小 {len(data)} 位元組,SHA-256 {manifest['sha256']}")
    print(f"  上一版 {old.get('version', '(無)')}")
    print(f"  當天合併說明:\n{day_text}")
    if a.dry_run:
        print("  --dry-run:不寫檔不推送")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    os.makedirs(os.path.join(REL, FWDIR), exist_ok=True)
    for b in glob.glob(os.path.join(REL, "firmware-*.bin")):   # r3 以前放在首頁的舊檔
        shutil.move(b, os.path.join(REL, FWDIR, os.path.basename(b)))
    shutil.copyfile(src, os.path.join(REL, FWDIR, name))
    with open(mpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    # 先推新版並建好 Release,最後才刪同一天的舊 Release:中途失敗時板子與 Releases 仍有可用的版本
    changelog_write(ver, day_text)
    prune_files()
    run(["git", "add", "-A"], cwd=REL)
    run(["git", "commit", "-m", f"韌體 {ver}\n\n{day_text}"], cwd=REL)
    run(["git", "push"], cwd=REL)
    release(ver, day_text, manifest["file"])
    prune_releases(ver)
    print(f"== 已發布 {ver}(當天只留這一版,說明已合併). raw 快取可能要幾分鐘才更新,板子暫時看到舊版屬正常.")


if __name__ == "__main__":
    main()
