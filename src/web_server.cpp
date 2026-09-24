// 版本流水號: r30 (2026-09-24) 狀態 f.lp:降落忽高忽低提醒中
// 舊: r29 (2026-09-15) 安全審查:/api/start 手動輸出/校正中回 startbusy;/api/cancel 不在等待放穩/倒數回 cancelstate
// 舊: r28 (2026-09-15) 套用備份碼可帶 sel/sec 取消不要的項目;檢查/套用回 amask,asec(實際套用),names(碼裡各組名稱)
// 舊: r27 (2026-09-15) 備份分區:GET /api/backup 加 sec(起飛降落與安全/安裝/電變/WiFi),sel 可為 0;檢查/套用回 sec,wifisaved
// 舊: r26 (2026-09-15) 選組備份:GET /api/backup?sel=N(預設只有「測試」組),檢查/套用回 mask(碼裡包含哪幾組)
// 舊: r25 (2026-09-15) /api/wifi 熱點密碼 appw(GET 回傳,POST 可省略沿用);狀態 f 加 tb(起飛油門階段)
// 舊: r24 (2026-09-14) 狀態加 asoff(設定忽略安全開關,網頁置頂警告用;含還沒儲存的值)
// 舊: r23 (2026-09-14) 網頁上傳韌體檢查身分標記:找不到就不切換(fwnotours);完成時回傳檔案版本與是否比目前舊
// 舊: r22 (2026-09-14) 設定備份碼:GET /api/backup(產生),POST /api/backup/check(貼上檢查),/api/backup/apply(套用,要按儲存)
// 舊: r21 (2026-09-14) 狀態 f 加 awl(等安全開關剩餘秒數);/api/fw 加 newer(網站版本比目前新 1 / 相同 0 / 較舊 -1)
// 舊: r20 (2026-09-14) 狀態 f 加 al(這趟起飛程序已按過安全開關)
// 舊: r19 (2026-09-14) 起飛程序與飛行中拒絕:儲存 WiFi 設定,發射功率,保持,檢查更新,校正設定/取消(安全審查 B5);狀態 cal 加時效剩餘秒數
// 舊: r18 (2026-09-14) 狀態 f 加 arm(安全開關按下)
// 舊: r17 (2026-09-14) 韌體更新:/api/fw(狀態),/api/fw/check,/api/fw/install,/api/fw/confirm;網頁上傳接更新保護;狀態加 fw [更新中,待確認,剩餘秒數,檢查狀態,進度,已退回]
// 舊: r16 (2026-09-14) WiFi 設定保護:網頁存檔一律試用,發射功率試用,/api/wifi/keep,狀態加 wt [功率試用剩餘,設定試用中,設定試用剩餘,目前功率]
// 舊: r15 (2026-09-14) 整數參數嚴格檢查(copy/manual/wifi tmo,txp/txpower:「abc」「12abc」拒絕)
// 舊: r14 (2026-09-14) /api/start 網頁開始起飛程序(手勢開啟,待機/結束,不在扭轉封鎖期)
// 舊: r13 (2026-09-13) /api/wifi:熱點名稱後綴 apsfx(GET 回完整名稱,開頭,後綴,上限,目前廣播名稱)
// 舊: r12 (2026-09-13) 機輪收腳:狀態加 gear [位置%,脈寬,試收輪中],/api/geartest
// 舊: r11 (2026-09-13) 狀態加 sim(測試用感測器模擬中),cap(GPIO5 量到的脈寬)
// 舊: r9 (2026-09-13) /api/events 事件紀錄,狀態加 evn(事件總數)
// 舊: r8 (2026-09-13) 狀態加 dsh(DShot 值),proto(開機套用中的協定)
// 舊: r7 (2026-09-13) 電變維護:/api/manual(手動輸出心跳),/api/manual/stop,/api/calib(下次通電校正旗標);狀態加 man,cal
// 舊: r6 (2026-09-13) 刪除第二段曲線相關(cmp2,/api/copycurve)
// 舊: r5 (2026-09-13) 狀態加第二段補償預覽 cmp2,/api/copycurve(第一段曲線複製到第二段)
// 舊: r4 (2026-09-13) 狀態加飛行狀態機欄位,/api/cancel,/api/estop
// 舊: r3 (2026-09-13) 加 /api/log 飛行紀錄(二進位增量),狀態加抖動/水平/手勢推力與試推燈
// 舊: r2 (2026-09-13) 設定 API:參數表,讀值,單項寫入,風格命名/選用/複製,回預設,儲存,放棄變更
// 舊: r1 (2026-09-13) 初版:首頁,狀態,WiFi 設定,發射功率,韌體上傳,重開機
#include "web_server.h"
#include <WebServer.h>
#include <Update.h>
#include "control.h"
#include "esc_output.h"
#include "esc_service.h"
#include "event_log.h"
#include "flight_log.h"
#include "flight.h"
#include "fw_update.h"
#include "gear.h"
#include "settings.h"
#include "settings_backup.h"
#include "test_hooks.h"
#include "wifi_manager.h"
#include "web_page.h"

static WebServer server(80);
static bool started = false;

// 首頁是編譯期常數,掛 ETag 讓重整時回 304(零位元組). ETag 取編譯時間,每次燒錄自動換.
static const char PAGE_ETAG[] = "\"" __DATE__ " " __TIME__ "\"";
static const char BUILD_TEXT[] = __DATE__ " " __TIME__;

static String jsonEscape(const char *s) {
  String out;
  for (; *s; ++s) {
    if (*s == '"' || *s == '\\') {
      out += '\\';
      out += *s;
    } else if ((uint8_t)*s < 0x20) {
      out += ' ';
    } else {
      out += *s;
    }
  }
  return out;
}

// 整數參數要整串是數字(可有負號). String::toInt() 遇到「abc」回 0,「12abc」回 12,錯字會被默默當成數值.
static bool argLong(const char *name, long &out) {
  if (!server.hasArg(name)) return false;
  String s = server.arg(name);
  s.trim();
  if (s.length() == 0 || s.length() > 10) return false;
  for (size_t i = 0; i < s.length(); ++i)
    if (!isdigit((unsigned char)s[i]) && !(i == 0 && s[i] == '-' && s.length() > 1)) return false;
  out = s.toInt();
  return true;
}

static void handleRoot() {
  if (server.header("If-None-Match") == PAGE_ETAG) {
    server.send(304, "text/html", "");
    return;
  }
  server.sendHeader("ETag", PAGE_ETAG);
  server.sendHeader("Cache-Control", "no-cache");
  server.send_P(200, "text/html; charset=utf-8", WEB_PAGE_HTML);
}

static void handleStatus() {
  Telemetry t;
  controlGetTelemetry(t);
  const uint8_t imu = !t.imuPresent ? 0 : (t.imuFault ? 2 : 1);
  const float comp = curveCompPct(profiles[activeProfile], t.pitchDeg);
  FlightStatus f;
  flightGetStatus(f);
  EscRpmStats rs;
  escRpmGetStats(rs);
  PwmCapStats cap;
  testPwmCapGet(cap);
  float wtTxp = 0, wtBootRemain = -1;
  bool wtBoot = false;
  wifiTrialStatus(wtTxp, wtBoot, wtBootRemain);
  FwStatus fw;
  fwUpdateGetStatus(fw);
  char buf[1900];
  snprintf(buf, sizeof(buf),
           "{\"p\":%.2f,\"rp\":%.2f,\"r\":%.1f,\"a\":%.3f,\"g\":[%.1f,%.1f,%.1f],\"b\":[%.2f,%.2f,%.2f],"
           "\"st\":%d,\"sts\":%.1f,\"imu\":%u,\"esc\":%u,\"ex\":%lu,\"late\":%lu,\"up\":%lu,"
           "\"heap\":%lu,\"ws\":%u,\"ip\":\"%s\",\"rssi\":%d,\"cd\":%u,\"ota\":%d,"
           "\"act\":%u,\"dirty\":%d,\"lock\":%d,\"cmp\":%.1f,\"imp\":[%.2f,%u,%ld],"
           "\"vib\":%.2f,\"lvl\":%d,\"hold\":%.1f,\"push\":%.2f,\"glamp\":%d,\"gpeak\":%.2f,\"push3\":%.2f,\"dist\":[%.3f,%.3f,%ld],"
           "\"f\":{\"s\":%u,\"ss\":%.1f,\"cd\":%.1f,\"t\":%.1f,\"base\":%.1f,\"comp\":%.1f,\"out\":%.1f,\"ph\":%u,\"tb\":%d,"
           "\"lc\":%u,\"er\":%u,\"rj\":%u,\"rja\":%ld,\"da\":%u,\"dg\":%.2f,\"dga\":%ld,\"ge\":%d,\"au\":%d,\"fp\":%u,\"set\":%.1f,\"tw\":%.0f,\"gb\":%.1f,\"aw\":%d,\"arm\":%d,\"al\":%d,\"awl\":%ld,\"lp\":%d},"
           "\"man\":%d,\"cal\":[%u,%.1f,%d,%d,%.0f],\"dsh\":%ld,\"proto\":%u,\"hz\":%u,\"evn\":%lu,\"rpm\":[%d,%lu,%lu,%lu,%lu,%lu,%lu,%ld],"
           "\"sim\":%d,\"cap\":[%d,%lu,%lu,%lu,%lu,%lu,%ld],\"gear\":[%.0f,%u,%d],\"wt\":[%.0f,%d,%.0f,%u],\"fw\":[%d,%d,%.0f,%u,%u,%d],\"asoff\":%d}",
           t.pitchDeg, t.rawPitchDeg, t.rollDeg, t.accMagG, t.gyroDps[0], t.gyroDps[1], t.gyroDps[2], t.biasDps[0],
           t.biasDps[1], t.biasDps[2], t.still ? 1 : 0, t.stillSeconds, imu, t.escUs, (unsigned long)t.maxExecUs,
           (unsigned long)t.maxLateMs, (unsigned long)(millis() / 1000), (unsigned long)ESP.getFreeHeap(),
           (unsigned)wifiState(), wifiIpText().c_str(), (int)wifiRssi(), (unsigned)wifiStaCountdownSeconds(),
           controlOtaAllowed() ? 1 : 0, (unsigned)activeProfile, settingsAnyDirty() ? 1 : 0,
           controlSettingsLocked() ? 1 : 0, comp, t.impactPeakG, (unsigned)t.impactMs,
           t.impactAgeMs == UINT32_MAX ? -1L : (long)(t.impactAgeMs / 1000), t.vibG, t.levelOk ? 1 : 0, t.rollHoldS,
           t.pushG, t.gestureLamp ? 1 : 0, t.gesturePeakG, t.pushPeak3sG, f.distG, f.distPeakG,
           f.distOverAgeMs == UINT32_MAX ? -1L : (long)(f.distOverAgeMs / 100), (unsigned)f.state, f.stateSeconds, f.countdownRemainS,
           f.flightSeconds, f.basePct, f.compPct, f.outPct, (unsigned)f.phase, f.takeoffBoost ? 1 : 0, (unsigned)f.landingCause,
           (unsigned)f.endReason, (unsigned)f.rejectReason, f.rejectAgeMs == UINT32_MAX ? -1L : (long)(f.rejectAgeMs / 100),
           (unsigned)f.disturbAction, f.disturbG, f.disturbAgeMs == UINT32_MAX ? -1L : (long)(f.disturbAgeMs / 100),
           f.gestureEnabled ? 1 : 0, f.autoStartUsed ? 1 : 0, (unsigned)f.flightProfile, f.settleSeconds, f.twistDeg, f.gestureBlockS, f.autoWaitLevel ? 1 : 0, f.armSwitch ? 1 : 0, f.armLatched ? 1 : 0,
           f.armWaitLeftS < 0 ? -1L : (long)ceilf(f.armWaitLeftS), f.landPulse ? 1 : 0,
           t.manualActive ? 1 : 0, (unsigned)t.calibState, t.calibRemainS, escCalibPending() ? 1 : 0,
           escBootWasPowerOn() ? 1 : 0, escCalibExpireRemainS(millis()), t.escDshot == 0xFFFF ? -1L : (long)t.escDshot, (unsigned)escActiveProtocol(), (unsigned)escActivePwmHz(), (unsigned long)eventLogTotal(), escRpmActive() ? 1 : 0, (unsigned long)rs.frames,
           (unsigned long)rs.replies, (unsigned long)rs.ok, (unsigned long)rs.bad, (unsigned long)rs.noReply,
           (unsigned long)rs.periodUs, rs.lastOkMs ? (long)(millis() - rs.lastOkMs) : -1L, testSimActive() ? 1 : 0,
           cap.active ? 1 : 0, (unsigned long)cap.pulses, (unsigned long)cap.highUs, (unsigned long)cap.periodUs,
           (unsigned long)cap.minHighUs, (unsigned long)cap.maxHighUs, cap.edgeAgeMs == UINT32_MAX ? -1L : (long)cap.edgeAgeMs,
           gearPosition() * 100.0f, (unsigned)gearCurrentUs(), controlGearTesting() ? 1 : 0, wtTxp, wtBoot ? 1 : 0, wtBootRemain,
           (unsigned)wifiLiveTxPower(), fw.busy ? 1 : 0, fw.pending ? 1 : 0, fw.confirmRemainS, (unsigned)fw.check,
           (unsigned)fw.progress, fw.rolledBack ? 1 : 0, sharedSettings.armSwitchOff ? 1 : 0);
  server.send(200, "application/json", buf);
}

// --- 飛行紀錄 ----------------------------------------------------------------------
// GET /api/log?since=N:二進位回傳第 N 筆之後的紀錄(網頁用增量更新,不必每次整份 48KB).
// 格式:[uint32 起始編號][uint32 筆數][uint16 每筆毫秒][uint16 每筆位元組] + 筆數 × FlightLogSample.
// 板子重開過(since 比目前總數大)或要的資料已被覆寫時,從保留範圍最舊一筆重送,網頁看起始編號對不上就重建.
static void handleLog() {
  uint32_t since = server.hasArg("since") ? strtoul(server.arg("since").c_str(), nullptr, 10) : 0;
  const uint32_t total = flightLogTotal();
  const uint32_t oldest = flightLogOldest();
  if (since > total || since < oldest) since = oldest;
  const uint32_t count = total - since;
  uint8_t header[12];
  const uint16_t sampleMs = FLIGHT_LOG_SAMPLE_MS, sampleSize = sizeof(FlightLogSample);
  memcpy(header, &since, 4);
  memcpy(header + 4, &count, 4);
  memcpy(header + 8, &sampleMs, 2);
  memcpy(header + 10, &sampleSize, 2);
  server.setContentLength(sizeof(header) + count * sampleSize);
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/octet-stream", "");
  server.sendContent((const char *)header, sizeof(header));
  FlightLogSample chunk[128];
  uint32_t i = since;
  while (i < since + count) {
    uint16_t n = 0;
    for (; n < 128 && i < since + count; ++n, ++i) {
      if (!flightLogGet(i, chunk[n])) memset(&chunk[n], 0, sizeof(FlightLogSample));
    }
    server.sendContent((const char *)chunk, n * sampleSize);
  }
}

// --- 事件紀錄 ----------------------------------------------------------------------
// GET /api/events?since=N:第 N 筆之後的事件. 回 {"total":總數,"oldest":最舊保留編號,"ev":[[編號,毫秒,種類,參數,a,b],…]}.
static void handleEvents() {
  uint32_t since = server.hasArg("since") ? strtoul(server.arg("since").c_str(), nullptr, 10) : 0;
  const uint32_t total = eventLogTotal();
  const uint32_t oldest = eventLogOldest();
  if (since > total || since < oldest) since = oldest;
  String json;
  json.reserve(96 + (total - since) * 48);
  json = "{\"total\":" + String(total) + ",\"oldest\":" + String(oldest) + ",\"ev\":[";
  char buf[96];
  bool first = true;
  EventRecord r;
  for (uint32_t i = since; i < total; ++i) {
    if (!eventLogGet(i, r)) continue;
    snprintf(buf, sizeof(buf), "%s[%lu,%lu,%u,%u,%.2f,%.2f]", first ? "" : ",", (unsigned long)i, (unsigned long)r.ms,
             (unsigned)r.type, (unsigned)r.arg, r.a, r.b);
    json += buf;
    first = false;
  }
  json += "]}";
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/json", json);
}

// --- 設定 ------------------------------------------------------------------------
static void sendResult(bool ok, const char *code);

static void handleMeta() {
  String json;
  settingsMetaJson(json);
  server.send(200, "application/json", json);
}

static void handleSettingsGet() {
  const long p = server.hasArg("p") ? server.arg("p").toInt() : activeProfile;
  String json;
  settingsValuesJson(json, (uint8_t)constrain(p, 0, PROFILE_COUNT - 1));
  server.send(200, "application/json", json);
}

// 寫入類請求共用:鎖定時(手勢成立到回待機之間)一律拒絕.
static bool refuseIfLocked() {
  if (!controlSettingsLocked()) return false;
  sendResult(false, "locked");
  return true;
}

static int8_t scopeArg() {
  // p=s 共用,p=0~5 風格
  const String s = server.arg("p");
  if (s == "s") return -1;
  if (s.length() == 1 && s[0] >= '0' && s[0] < '0' + PROFILE_COUNT) return (int8_t)(s[0] - '0');
  return -2;
}

static void handleSet() {
  if (refuseIfLocked()) return;
  if (!server.hasArg("p") || !server.hasArg("k") || !server.hasArg("v")) return sendResult(false, "badform");
  const char *err = settingsSet(scopeArg(), server.arg("k").c_str(), server.arg("v").c_str());
  sendResult(err == nullptr, err ? err : "set");
}

// POST /api/setmany?p=s|0~5,本文 text/plain 每行 key=value. 備份還原用:整批寫完才驗證.
static void handleSetMany() {
  if (refuseIfLocked()) return;
  if (!server.hasArg("p") || !server.hasArg("plain")) return sendResult(false, "badform");
  String body = server.arg("plain");
  if (body.length() > 4000) return sendResult(false, "badform");
  const char *err = settingsSetMany(scopeArg(), (char *)body.c_str());
  sendResult(err == nullptr, err ? err : "set");
}

static void handleName() {
  if (refuseIfLocked()) return;
  const int8_t scope = scopeArg();
  if (scope < 0 || !server.hasArg("name")) return sendResult(false, "badform");
  String name = server.arg("name");
  name.trim();
  const char *err = settingsSetName((uint8_t)scope, name.c_str());
  sendResult(err == nullptr, err ? err : "set");
}

static void handleSelect() {
  if (refuseIfLocked()) return;
  const int8_t scope = scopeArg();
  if (scope < 0) return sendResult(false, "badform");
  const char *err = settingsSelectProfile((uint8_t)scope);
  sendResult(err == nullptr, err ? err : "selected");
}

static void handleCopy() {
  if (refuseIfLocked()) return;
  long from = 0, to = 0;
  if (!argLong("from", from) || !argLong("to", to)) return sendResult(false, "badform");
  const char *err = settingsCopyProfile((uint8_t)constrain(from, 0, 255), (uint8_t)constrain(to, 0, 255));
  sendResult(err == nullptr, err ? err : "copied");
}

static void handleDefaults() {
  if (refuseIfLocked()) return;
  const int8_t scope = scopeArg();
  if (scope < -1) return sendResult(false, "badform");
  settingsDefaults(scope);
  sendResult(true, "defaults");
}

static void handleSave() {
  if (refuseIfLocked()) return;
  const char *err = settingsSave();
  sendResult(err == nullptr, err ? err : "saved");
}

// --- 設定備份碼 -------------------------------------------------------------------
// 有未儲存變更時產生,檢查,套用一律拒絕(GG:先儲存或放棄):備份碼才一定等於飛機實際飛的設定,套用也不會蓋掉還沒存的修改.
// GET /api/backup?sel=N&sec=M:N = 風格(bit i = 第 i 組,0~63),沒給 = 只有「測試」組;
// M = 分區(1 起飛降落與安全,2 安裝,4 電變,8 WiFi,0~15),沒給 = 0. 兩個不可都是 0.
static void handleBackupGet() {
  if (settingsAnyDirty()) return sendResult(false, "bkdirty");
  long sel = 1L << PROFILE_TEST_INDEX, sec = 0;
  if (server.hasArg("sel") && !argLong("sel", sel)) return sendResult(false, "bksel");
  if (server.hasArg("sec") && !argLong("sec", sec)) return sendResult(false, "bksel");
  if (sel < 0 || sel > BACKUP_ALL_PROFILES || sec < 0 || sec > BACKUP_SEC_ALL || (sel == 0 && sec == 0)) return sendResult(false, "bksel");
  String code;
  if (const char *err = backupEncode(code, (uint8_t)sel, (uint8_t)sec)) return sendResult(false, err);
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/json", "{\"ok\":true,\"code\":\"bkmade\",\"text\":\"" + code + "\"}");
}

static void backupCheckOrApply(bool apply) {
  if (apply && refuseIfLocked()) return;
  if (settingsAnyDirty()) return sendResult(false, "bkdirty");
  if (!server.hasArg("text")) return sendResult(false, "badform");
  const String text = server.arg("text");
  if (text.length() > 4000) return sendResult(false, "bkcrc");
  // 套用時可帶 sel/sec:使用者取消碼裡不要的項目(沒帶 = 碼裡有的全部套用)
  long sel = BACKUP_ALL_PROFILES, sec = BACKUP_SEC_ALL;
  if (server.hasArg("sel") && !argLong("sel", sel)) return sendResult(false, "bksel");
  if (server.hasArg("sec") && !argLong("sec", sec)) return sendResult(false, "bksel");
  if (sel < 0 || sel > BACKUP_ALL_PROFILES || sec < 0 || sec > BACKUP_SEC_ALL) return sendResult(false, "bksel");
  BackupInfo info;
  const char *err = backupDecode(text.c_str(), apply, info, (uint8_t)sel, (uint8_t)sec);
  String json = "{\"ok\":";
  json += err ? "false" : "true";
  json += ",\"code\":\"";
  json += err ? err : (apply ? "bkapplied" : "bkok");
  json += "\",\"scope\":" + String(info.badScope) + ",\"gen\":" + String(info.generation) +
          ",\"newer\":" + (info.newer ? "1" : "0") + ",\"mask\":" + String(info.profileMask) + ",\"sec\":" + String(info.sectionMask) +
          ",\"amask\":" + String(info.applyProfileMask) + ",\"asec\":" + String(info.applySectionMask) +
          ",\"names\":[" + info.names + "],\"wifisaved\":" + (info.wifiSaved ? "1" : "0") + ",\"clamp\":[" + info.clamped + "]}";
  server.send(err ? 400 : 200, "application/json", json);
}

static void handleBackupCheck() { backupCheckOrApply(false); }
static void handleBackupApply() { backupCheckOrApply(true); }


// 網頁「開始起飛程序」(GG 2026-09-14):等同做一次啟動手勢,之後照常等待放穩 → 倒數 → 起飛.
// 未儲存變更,感測器,水平限制,扭轉取消封鎖期由狀態機檢查,拒絕原因顯示在狀態列與事件紀錄.
// 網頁端要按兩下確認才送出.
static void handleStart() {
  FlightStatus f;
  flightGetStatus(f);
  if (!flightShared().gestureEnable) return sendResult(false, "startauto");   // 上電自動倒數模式:每次上電只飛一次
  if (f.state != FS_STANDBY && f.state != FS_DONE) return sendResult(false, "startstate");
  if (f.gestureBlockS > 0) return sendResult(false, "startblock");
  if (!controlOtaAllowed()) return sendResult(false, "startbusy");   // 手動輸出/校正中狀態機會靜默丟掉請求,先在這裡回原因
  flightRequestGesture(GESTURE_SRC_WEB);
  sendResult(true, "start");
}

static void handleCancel() {
  FlightStatus f;
  flightGetStatus(f);
  if (f.state != FS_WAIT_STILL && f.state != FS_COUNTDOWN) return sendResult(false, "cancelstate");   // 飛行中要用緊急停止
  flightRequestCancel();
  sendResult(true, "cancel");
}

// 緊急停止:網頁端要連按三下才會送出(避免誤觸),韌體收到就停,不再二次確認.
static void handleEstop() {
  flightRequestEstop();
  sendResult(true, "estop");
}

// --- 電變維護 ----------------------------------------------------------------------
// POST /api/manual us=N:手動輸出心跳(網頁每 0.2 秒送一次,停送 0.5 秒自動回最低油門).
static void handleManual() {
  if (!server.hasArg("us")) return sendResult(false, "badform");
  long us = 0;
  if (!argLong("us", us)) return sendResult(false, "range");
  const char *err = controlManualWrite((uint16_t)constrain(us, 0, 65535));
  sendResult(err == nullptr, err ? err : "manual");
}

static void handleManualStop() {
  controlManualStop();
  sendResult(true, "manualstop");
}

// POST /api/calib on=1|0:下次通電進入電變校正. 開啟要在待機且設定已儲存(校正用存檔裡的脈寬).
static void handleCalib() {
  if (refuseIfLocked()) return;   // 寫 NVS:起飛程序與飛行中不寫快閃(安全審查 B5)
  if (!server.hasArg("on")) return sendResult(false, "badform");
  const bool on = server.arg("on") == "1";
  if (on) {
    if (!controlOtaAllowed()) return sendResult(false, "busy");
    if (settingsAnyDirty()) return sendResult(false, "calibdirty");
    if (sharedSettings.escProtocol != ESC_PROTO_PWM50) return sendResult(false, "calibproto");
  }
  const char *err = escCalibSetPending(on);
  sendResult(err == nullptr, err ? err : (on ? "calibon" : "caliboff"));
}

// POST /api/geartest on=1|0:待機時試收輪(最多 10 秒自動放下),調舵機限位行程用
static void handleGearTest() {
  if (!server.hasArg("on")) return sendResult(false, "badform");
  const char *err = controlGearTest(server.arg("on") == "1");
  sendResult(err == nullptr, err ? err : "geartest");
}

static void handleRevert() {
  if (refuseIfLocked()) return;
  settingsRevert();
  sendResult(true, "reverted");
}

static void handleWifiGet() {
  const WifiConfig &c = wifiConfig();
  // 密碼一併回傳:這是自己裝置的區域設定頁(類似路由器後台),回填才能只改別的欄位而不必重打密碼.
  String json = "{\"ssid\":\"" + jsonEscape(c.ssid) + "\",\"pw\":\"" + jsonEscape(c.password) +
                "\",\"host\":\"" + jsonEscape(c.host) + "\",\"tmo\":" + String(c.staTimeoutSec) +
                ",\"forceap\":" + String(c.forceAp ? 1 : 0) + ",\"txp\":" + String(c.txPowerDbm) +
                ",\"txmin\":" + String(WIFI_TX_POWER_MIN_DBM) + ",\"txmax\":" + String(WIFI_TX_POWER_MAX_DBM) +
                ",\"tmomin\":" + String(WIFI_STA_TIMEOUT_MIN_S) + ",\"tmomax\":" + String(WIFI_STA_TIMEOUT_MAX_S) +
                ",\"apssid\":\"" + jsonEscape(wifiApSsid(true).c_str()) + "\",\"apnow\":\"" + jsonEscape(wifiApSsid(false).c_str()) +
                "\",\"apprefix\":\"" + jsonEscape(WIFI_AP_SSID) + "\",\"apsfx\":\"" + jsonEscape(c.apSuffix) +
                "\",\"appw\":\"" + jsonEscape(c.apPassword) + "\",\"apsfxmax\":" + String(WIFI_AP_SUFFIX_MAX_BYTES) + ",\"build\":\"" + BUILD_TEXT + "\"}";
  server.send(200, "application/json", json);
}

static void sendResult(bool ok, const char *code) {
  char buf[64];
  snprintf(buf, sizeof(buf), "{\"ok\":%s,\"code\":\"%s\"}", ok ? "true" : "false", code);
  server.send(ok ? 200 : 400, "application/json", buf);
}

static void handleWifiSet() {
  // 起飛程序與飛行中不寫快閃(寫入時處理器暫停,安全審查 B5)
  if (refuseIfLocked()) return;
  // 欄位不齊就整批拒絕:缺欄位時 arg() 回空字串,空 SSID 會被默默寫進去,下次上電莫名退回熱點.
  const char *fields[] = {"ssid", "pw", "host", "tmo", "forceap", "txp"};
  for (const char *f : fields) {
    if (!server.hasArg(f)) return sendResult(false, "badform");
  }
  const String ssid = server.arg("ssid"), pw = server.arg("pw");
  String host = server.arg("host");
  host.trim();
  if (ssid.length() >= WIFI_SSID_BUFFER) return sendResult(false, "ssidlong");
  if (pw.length() >= WIFI_PASS_BUFFER) return sendResult(false, "pwlong");
  if (host.length() >= MDNS_HOST_BUFFER) return sendResult(false, "hostbad");
  WifiConfig c = {};
  strncpy(c.ssid, ssid.c_str(), sizeof(c.ssid) - 1);
  strncpy(c.password, pw.c_str(), sizeof(c.password) - 1);
  strncpy(c.host, host.c_str(), sizeof(c.host) - 1);
  long tmo = 0, txp = 0;
  if (!argLong("tmo", tmo)) return sendResult(false, "tmo");
  if (!argLong("txp", txp)) return sendResult(false, "txp");
  c.staTimeoutSec = (uint8_t)constrain(tmo, 0, 255);
  c.forceAp = server.arg("forceap") == "1";
  c.txPowerDbm = (uint8_t)constrain(txp, 0, 255);
  // 熱點名稱後綴與熱點密碼(可省略:沒送就沿用目前的,舊的測試腳本照樣能用)
  if (server.hasArg("apsfx")) {
    const String sfx = server.arg("apsfx");
    if (sfx.length() > WIFI_AP_SUFFIX_MAX_BYTES) return sendResult(false, "apsfxlong");
    strncpy(c.apSuffix, sfx.c_str(), sizeof(c.apSuffix) - 1);
  } else {
    strncpy(c.apSuffix, wifiConfig().apSuffix, sizeof(c.apSuffix) - 1);
  }
  if (server.hasArg("appw")) {
    const String appw = server.arg("appw");
    if (appw.length() >= WIFI_PASS_BUFFER) return sendResult(false, "appwlong");
    strncpy(c.apPassword, appw.c_str(), sizeof(c.apPassword) - 1);
  } else {
    strncpy(c.apPassword, wifiConfig().apPassword, sizeof(c.apPassword) - 1);
  }
  // 網頁存的 WiFi 設定一律「試用」:重開後 WiFi 就緒 3 分鐘內沒在網頁按保持就退回上一次的設定(GG 2026-09-14)
  const char *err = wifiSaveConfig(c, true);
  if (err) return sendResult(false, err);
  sendResult(true, "saved");
}

static void handleTxPower() {
  if (refuseIfLocked()) return;   // 飛行中改發射功率可能斷線,連不上就按不到緊急停止
  // 發射功率即時生效不存檔,方便一邊改一邊比較連線品質;要保留就按儲存 WiFi 設定.
  // 試用 15 秒:調太大連不上時按不到「保持」,自動退回(GG 2026-09-14)
  long dbm = -1;
  if (!argLong("txp", dbm)) dbm = -1;
  if (!wifiTryTxPower((uint8_t)constrain(dbm, 0, 255)) || dbm < 0) return sendResult(false, "txp");
  sendResult(true, "applied");
}

static void handleWifiKeep() {
  if (refuseIfLocked()) return;   // 寫 NVS;試用計時在起飛程序與飛行中暫停,落地後再按
  wifiKeep();
  sendResult(true, "kept");
}

static void handleTimingReset() {
  controlResetTimingStats();
  sendResult(true, "reset");
}

static void handleReboot() {
  if (!controlOtaAllowed()) return sendResult(false, "busy");
  sendResult(true, "reboot");
  delay(300);
  ESP.restart();
}

// --- 網頁韌體更新 ---------------------------------------------------------------
// 讓沒有開發環境的使用者也能更新:瀏覽器選 firmware.bin 上傳. 只在待機狀態允許.
static bool updateRefused = false;
static const char *uploadErr = nullptr;   // 身分標記檢查失敗的錯誤代碼
static char uploadVer[24] = "";

static void handleUpdateUpload() {
  HTTPUpload &up = server.upload();
  if (up.status == UPLOAD_FILE_START) {
    // 板子自己下載更新進行中也不接受上傳(兩邊會搶同一個分區)
    updateRefused = !controlOtaAllowed() || fwUpdateBlockReason() == 1;
    if (updateRefused) return;
    uploadErr = nullptr;
    uploadVer[0] = 0;
    fwIdScanReset();
    Serial.printf("WEB OTA start %s\n", up.filename.c_str());
    fwUpdateStarted(FWS_WEB_UPLOAD);   // 寫入期間拒絕起飛與手動輸出
    if (!Update.begin(UPDATE_SIZE_UNKNOWN)) Update.printError(Serial);
  } else if (up.status == UPLOAD_FILE_WRITE) {
    if (updateRefused || Update.hasError()) return;
    fwIdScanFeed(up.buf, up.currentSize);
    if (Update.write(up.buf, up.currentSize) != up.currentSize) Update.printError(Serial);
  } else if (up.status == UPLOAD_FILE_END) {
    if (updateRefused) return;
    const char *ver = fwIdScanVersion();
    if (!ver && !Update.hasError()) {
      // 格式,晶片,檢查碼都可能是對的(別的 ESP32-C3 程式),但不是這個控制器的韌體:不切換開機分區
      Serial.println(F("WEB OTA refused: firmware id not found"));
      Update.abort();
      uploadErr = "fwnotours";
      fwUpdateFlashed(false);
      return;
    }
    if (Update.end(true)) {
      strlcpy(uploadVer, ver, sizeof(uploadVer));
      Serial.printf("WEB OTA done %u bytes, version %s\n", (unsigned)up.totalSize, uploadVer);
      fwUpdateFlashed(true, uploadVer);
    } else {
      Update.printError(Serial);
      fwUpdateFlashed(false);
    }
  } else if (up.status == UPLOAD_FILE_ABORTED) {
    if (updateRefused) return;
    Update.abort();
    fwUpdateFlashed(false);
  }
}

// --- 板子自己下載更新(公開 GitHub 專案)與新韌體確認 -------------------------------------
static String jsonText(const char *s) {   // 字串跳脫,換行保留成 \n(更新說明可以分行)
  String out;
  for (; *s; ++s) {
    if (*s == '"' || *s == '\\') {
      out += '\\';
      out += *s;
    } else if (*s == '\n') {
      out += "\\n";
    } else if ((uint8_t)*s < 0x20) {
      out += ' ';
    } else {
      out += *s;
    }
  }
  return out;
}

// GET /api/fw:目前版本,更新中,待確認(剩餘秒數),上次更新被退回,檢查結果(遠端版本,大小,說明),下載進度
static void handleFwGet() {
  FwStatus s;
  fwUpdateGetStatus(s);
  String j;
  j.reserve(900);
  j = "{\"ver\":\"" FW_VERSION "\",\"build\":\"";
  j += BUILD_TEXT;
  j += "\",\"busy\":" + String(s.busy ? 1 : 0) + ",\"pending\":" + String(s.pending ? 1 : 0) + ",\"remain\":" + String(s.confirmRemainS, 0) +
       ",\"rb\":" + String(s.rolledBack ? 1 : 0) + ",\"rbver\":\"" + jsonText(s.rolledBackFrom) + "\",\"check\":" + String(s.check) +
       ",\"err\":\"" + jsonText(s.err) + "\",\"prog\":" + String(s.progress) + ",\"rver\":\"" + jsonText(s.remoteVersion) +
       "\",\"newer\":" + String(s.remoteNewer) + ",\"rsize\":" + String(s.remoteSize) + ",\"notes\":\"" + jsonText(s.notes) +
       "\",\"src\":\"" FW_UPDATE_BASE_URL "\"}";
  server.send(200, "application/json", j);
}

static void handleFwCheck() {
  if (refuseIfLocked()) return;   // 起飛程序與飛行中不開下載工作(TLS 佔記憶體與 CPU)
  const char *err = fwUpdateCheckStart();
  sendResult(!err, err ? err : "fwchecking");
}

static void handleFwInstall() {
  if (!server.hasArg("ver")) return sendResult(false, "badform");
  const char *err = fwUpdateInstallStart(server.arg("ver").c_str());
  sendResult(!err, err ? err : "fwinstalling");
}

// 網頁載入後自動呼叫:能走到這裡代表新韌體的 WiFi,網頁伺服器,網頁程式都正常
static void handleFwConfirm() {
  const bool ok = fwUpdateConfirm();
  sendResult(ok, ok ? "fwconfirmed" : "fwconfirmfail");
}

static void handleUpdateDone() {
  if (updateRefused) return sendResult(false, "busy");
  if (uploadErr) return sendResult(false, uploadErr);
  if (Update.hasError() || !Update.isFinished()) return sendResult(false, "updatefail");
  // older:上傳的版本比目前舊(允許,等於退回舊版)
  server.send(200, "application/json", String("{\"ok\":true,\"code\":\"updated\",\"ver\":\"") + uploadVer +
                                           "\",\"older\":" + (fwVersionCompare(uploadVer, FW_VERSION) < 0 ? "1" : "0") + "}");
  delay(500);
  ESP.restart();
}

static void registerRoutes() {
  // WebServer 預設丟棄請求標頭,不先登記就讀不到 If-None-Match,ETag 等於無效.
  const char *collect[] = {"If-None-Match"};
  server.collectHeaders(collect, 1);
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/meta", HTTP_GET, handleMeta);
  server.on("/api/log", HTTP_GET, handleLog);
  server.on("/api/events", HTTP_GET, handleEvents);
  server.on("/api/settings", HTTP_GET, handleSettingsGet);
  server.on("/api/set", HTTP_POST, handleSet);
  server.on("/api/name", HTTP_POST, handleName);
  server.on("/api/setmany", HTTP_POST, handleSetMany);
  server.on("/api/select", HTTP_POST, handleSelect);
  server.on("/api/copy", HTTP_POST, handleCopy);
  server.on("/api/defaults", HTTP_POST, handleDefaults);
  server.on("/api/save", HTTP_POST, handleSave);
  server.on("/api/revert", HTTP_POST, handleRevert);
  server.on("/api/backup", HTTP_GET, handleBackupGet);
  server.on("/api/backup/check", HTTP_POST, handleBackupCheck);
  server.on("/api/backup/apply", HTTP_POST, handleBackupApply);
  server.on("/api/start", HTTP_POST, handleStart);
  server.on("/api/cancel", HTTP_POST, handleCancel);  server.on("/api/estop", HTTP_POST, handleEstop);
  server.on("/api/wifi", HTTP_GET, handleWifiGet);
  server.on("/api/wifi", HTTP_POST, handleWifiSet);
  server.on("/api/txpower", HTTP_POST, handleTxPower);
  server.on("/api/wifi/keep", HTTP_POST, handleWifiKeep);
  server.on("/api/timing/reset", HTTP_POST, handleTimingReset);
  server.on("/api/reboot", HTTP_POST, handleReboot);
  server.on("/api/manual", HTTP_POST, handleManual);
  server.on("/api/manual/stop", HTTP_POST, handleManualStop);
  server.on("/api/calib", HTTP_POST, handleCalib);
  server.on("/api/geartest", HTTP_POST, handleGearTest);
  server.on("/update", HTTP_POST, handleUpdateDone, handleUpdateUpload);
  server.on("/api/fw", HTTP_GET, handleFwGet);
  server.on("/api/fw/check", HTTP_POST, handleFwCheck);
  server.on("/api/fw/install", HTTP_POST, handleFwInstall);
  server.on("/api/fw/confirm", HTTP_POST, handleFwConfirm);
  server.onNotFound([]() { server.send(404, "text/plain", "Not found"); });
}

// 瀏覽器會投機性地先開 socket 卻不送資料. 內建 WebServer 一次只服務一條連線,那條閒置連線
// 會佔住名額 HTTP_MAX_DATA_WAIT = 5 秒,期間所有請求排隊,網頁數字就凍住(參考專案實測 5008ms).
// 連著卻一直沒資料可讀超過 0.4 秒就主動放掉;真正的請求在握手後幾毫秒內就到.
static const uint32_t IDLE_CLIENT_MS = 400;
static uint32_t idleSinceMs = 0;

void webTick() {
  if (!started) {
    if (wifiState() == WIFI_STATE_CONNECTING) return;
    registerRoutes();
    server.begin();
    started = true;
  }
  server.handleClient();
  auto &client = server.client();
  if (client.connected() && client.available() == 0) {
    const uint32_t now = millis();
    if (idleSinceMs == 0) idleSinceMs = now;
    else if (now - idleSinceMs >= IDLE_CLIENT_MS) {
      client.stop();
      idleSinceMs = 0;
    }
  } else {
    idleSinceMs = 0;
  }
}
