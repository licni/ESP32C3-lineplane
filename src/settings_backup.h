// 版本流水號: r4 (2026-09-15) 套用時可取消碼裡的項目(filterProfiles/filterSections);BackupInfo 加實際套用的分區與風格,碼裡的名稱
// 舊: r3 (2026-09-15) 分區選擇:起飛降落與安全/安裝/電變/WiFi 各自可選(GG:分享計時器不該蓋掉對方的安裝與電變),
//   風格也各自可選;BackupInfo 加 sectionMask
// 舊: r2 (2026-09-15) 選組備份:產生時指定要包含哪幾組風格(共用設定一律包含);BackupInfo 加 profileMask
// 舊: r1 (2026-09-14) 初版:設定備份碼(LP + 英數字,每個參數固定位元數,新功能往尾端加,CRC-24)
#pragma once
#include <Arduino.h>
// ============================================================================
// 設定備份碼(GG 2026-09-14,設計見 docs/設定備份碼設計_2026-09-14.md).
// 選的內容(六組風格各自可選;共用設定分成起飛降落與安全,安裝,電變三區各自可選;WiFi 可選)
// 壓成 LP 開頭的英數字短碼,在另一台飛機貼上套用,再按儲存. 碼裡沒有的部分套用時不動.
// ============================================================================

const uint8_t BACKUP_ALL_PROFILES = 0x3F;   // 六組全選

// 分區(bit). 共用設定每個參數屬於哪一區看 settings_backup.cpp 的 SHARED_SECTIONS(與網頁分頁一致).
const uint8_t BACKUP_SEC_FLIGHT = 1;    // 設定頁:啟動與倒數,觸地提早降落,降落與撞擊
const uint8_t BACKUP_SEC_INSTALL = 2;   // 安裝頁:感測器方位,角度修正,飛行速度,機輪收腳,蜂鳴器
const uint8_t BACKUP_SEC_ESC = 4;       // 電變頁:輸出協定,PWM 頻率,脈寬,校正保持,轉速回傳,馬達極數
const uint8_t BACKUP_SEC_WIFI = 8;      // 系統頁 WiFi(套用時直接存檔並標記試用,重新開機生效)
const uint8_t BACKUP_SEC_SHARED = BACKUP_SEC_FLIGHT | BACKUP_SEC_INSTALL | BACKUP_SEC_ESC;
const uint8_t BACKUP_SEC_ALL = BACKUP_SEC_SHARED | BACKUP_SEC_WIFI;

struct BackupInfo {
  uint8_t generation = 0;   // 短碼的欄位世代
  bool newer = false;       // 短碼來自較新的韌體:尾端不認得的功能已略過
  int8_t badScope = -1;     // 驗證失敗時:-1 共用,0~5 風格,-2 WiFi
  uint8_t profileMask = BACKUP_ALL_PROFILES;   // 短碼包含哪幾組風格(bit i = 第 i 組);舊格式一律全選
  uint8_t sectionMask = BACKUP_SEC_SHARED;     // 短碼包含哪些分區;舊格式 = 三區共用設定,沒有 WiFi
  uint8_t applyProfileMask = 0;   // 實際套用的風格(碼裡有的 ∩ 使用者要的)
  uint8_t applySectionMask = 0;   // 實際套用的分區
  String names;             // 碼裡各組風格的名稱,JSON 陣列內容(碼裡沒有的組是空字串),網頁顯示勾選用
  bool wifiSaved = false;   // 套用時已把 WiFi 設定存檔(試用,重新開機生效)
  String clamped;           // 超出目前範圍被夾的參數,JSON 陣列內容:"s:escMinUs","3:minPct","act"
};

// 目前的設定產生短碼. profileMask = 風格(0~63),sectionMask = 分區(0~15),兩個不可都是 0.
// 成功回 nullptr,選擇不對回 bksel.
const char *backupEncode(String &out, uint8_t profileMask, uint8_t sectionMask);
// 解讀短碼並驗證,apply = true 時套到 RAM(未儲存變更),含 WiFi 時同時存 WiFi 設定(試用). 成功回 nullptr,失敗回錯誤代碼:
//   bkprefix 開頭不是 LP,bkcrc 不完整或有錯字,bkver 格式太新,name/驗證代碼(badScope 指出哪一塊).
// 套用時:碼裡沒有的風格與分區保持目前的值;不是六組全選的碼不切換飛行使用的風格.
// filterProfiles/filterSections:使用者取消的項目(碼裡有但不要)也當成沒有,保持目前的值. 全部取消回 bknone.
const char *backupDecode(const char *text, bool apply, BackupInfo &info, uint8_t filterProfiles = BACKUP_ALL_PROFILES,
                         uint8_t filterSections = BACKUP_SEC_ALL);
// 開機檢查編碼表是否裝得下目前的參數範圍,每個共用參數都有分區,結果印在序列埠.
void backupSelfCheck();
