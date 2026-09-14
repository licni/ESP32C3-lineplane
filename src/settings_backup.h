// 版本流水號: r1 (2026-09-14) 初版:設定備份碼(LP + 英數字,每個參數固定位元數,新功能往尾端加,CRC-24)
#pragma once
#include <Arduino.h>
// ============================================================================
// 設定備份碼(GG 2026-09-14,設計見 docs/設定備份碼設計_2026-09-14.md).
// 全部飛行設定(共用,六組風格與名稱,飛行使用哪一組;不含 WiFi)壓成 LP 開頭的英數字短碼,
// 在另一台飛機貼上套用,再按儲存.
// ============================================================================

struct BackupInfo {
  uint8_t generation = 0;   // 短碼的欄位世代
  bool newer = false;       // 短碼來自較新的韌體:尾端不認得的功能已略過
  int8_t badScope = -1;     // 交叉驗證失敗時:-1 共用,0~5 風格
  String clamped;           // 超出目前範圍被夾的參數,JSON 陣列內容:"s:escMinUs","3:minPct","act"
};

// 目前 RAM 的設定產生短碼. 成功回 nullptr.
const char *backupEncode(String &out);
// 解讀短碼並驗證,apply = true 時套到 RAM(未儲存變更). 成功回 nullptr,失敗回錯誤代碼:
//   bkprefix 開頭不是 LP,bkcrc 不完整或有錯字,bkver 格式太新,name/驗證代碼(badScope 指出哪一塊).
const char *backupDecode(const char *text, bool apply, BackupInfo &info);
// 開機檢查編碼表是否裝得下目前的參數範圍(改參數表範圍時提醒要開新世代),結果印在序列埠.
void backupSelfCheck();
