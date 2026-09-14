# 版本流水號: r1 (2026-09-14) 初版:韌體檔不帶本機路徑
# ============================================================================
# PlatformIO 建置前腳本(platformio.ini 的 extra_scripts = pre:tools/pio_strip_paths.py).
# Arduino 核心的 log/assert 會把原始檔完整路徑(__FILE__)編進韌體,路徑裡有電腦的使用者名稱,
# 韌體檔發布出去就帶出個資. 用 -ffile-prefix-map 把本機路徑換成短前綴,不影響程式行為.
# 驗證:韌體檔搜尋 "Users/" 應該找不到.
# ============================================================================
import os

Import("env")  # noqa: F821


def fwd(p):
    return os.path.normpath(p).replace("\\", "/").rstrip("/")


# 越具體的放越後面:GCC 多個對映都符合時用最後一個
pairs = [
    (os.path.expanduser("~"), "~"),
    (env.subst("$PROJECT_CORE_DIR"), "pio"),        # noqa: F821
    (env.subst("$PROJECT_PACKAGES_DIR"), "pkg"),    # noqa: F821
    (env.subst("$PROJECT_DIR"), "."),               # noqa: F821
]
env.Append(CCFLAGS=[f"-ffile-prefix-map={fwd(old)}={new}" for old, new in pairs if old and "$" not in old])  # noqa: F821
