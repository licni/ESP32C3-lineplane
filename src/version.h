// 版本流水號: r1 (2026-09-14) 初版:韌體版本號與更新來源
#pragma once
// ============================================================================
// 韌體版本號. 發布新版給使用者時一定要改(tools/publish_firmware.py 會檢查和公開專案上的版本不同).
// 格式:年.月.日.當天第幾版,例如 2026.09.14.1. 板子只比「相不相同」,不比大小:GG 發布舊版修正也能裝.
// ============================================================================
#define FW_VERSION "2026.09.14.12"

// 板子自己下載更新的來源:GG 的公開 GitHub 專案(只放韌體檔,不放原始碼).
// manifest.json 內容:{"version":"…","size":位元組,"sha256":"64 個十六進位","file":"firmware/firmware-版本.bin","notes":"更新說明"}
// manifest.json 放專案首頁;韌體檔放 firmware/ 資料夾(2026.09.14.6 起,之前的版本只認同一層的檔名).
// 用 raw.githubusercontent.com:不會轉址,檔名含版本號避開 CDN 快取.
#define FW_UPDATE_BASE_URL "https://raw.githubusercontent.com/licni/ESP32lineplane-firmware/main/"
#define FW_MANIFEST_NAME "manifest.json"
