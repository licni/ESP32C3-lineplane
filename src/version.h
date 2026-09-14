// 版本流水號: r2 (2026-09-14) 板子改成逐段比版本數字,只有網站版本比較新才提示更新(GG:板子 .12,網站 .11 卻說有新版本)
// 舊: r1 (2026-09-14) 初版:韌體版本號與更新來源
#pragma once
// ============================================================================
// 韌體版本號. 發布新版給使用者時一定要改(tools/publish_firmware.py 會檢查比公開專案上的版本新).
// 格式:年.月.日.當天第幾版,例如 2026.09.14.1. 板子逐段比數字(fwVersionCompare),網站版本比目前新才可以下載安裝;
// 要讓板子換回舊的程式,用新的版本號重新發布. 手動上傳韌體檔不限版本新舊,但要有身分標記(fw_update.h FW_ID_PREFIX).
// ============================================================================
#define FW_VERSION "2026.09.15.1"

// 板子自己下載更新的來源:GG 的公開 GitHub 專案(只放韌體檔,不放原始碼).
// manifest.json 內容:{"version":"…","size":位元組,"sha256":"64 個十六進位","file":"firmware/firmware-版本.bin","notes":"更新說明"}
// manifest.json 放專案首頁;韌體檔放 firmware/ 資料夾(2026.09.14.6 起,之前的版本只認同一層的檔名).
// 用 raw.githubusercontent.com:不會轉址,檔名含版本號避開 CDN 快取.
#define FW_UPDATE_BASE_URL "https://raw.githubusercontent.com/licni/ESP32lineplane-firmware/main/"
#define FW_MANIFEST_NAME "manifest.json"
