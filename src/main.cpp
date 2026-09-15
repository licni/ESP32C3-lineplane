// 版本流水號: r19 (2026-09-14) 載入設定後蜂鳴器腳位依設定的電位先設成不響(buzzerBegin)
// 舊: r18 (2026-09-14) 開機檢查設定備份碼的編碼表(backupSelfCheck)
// 舊: r17 (2026-09-14) 序列指令 armwait <秒>|off(測試用縮短安全開關等待上限,軟體重開保留)
// 舊: r16 (2026-09-14) 感測器改 GPIO5/6 後擋 GPIO5 測試指令 pwmcap/escemu;開機印 I2C 腳位;
//   I2C 匯流排解鎖(開機與 mpu 指令,預防):重開時感測器傳到一半會拉住 SDA,之後讀不到
// 舊: r15 (2026-09-14) 校正旗標時效推進;序列指令 calexp(測試用縮短時效)
// 舊: r14 (2026-09-14) 序列指令 armsw(測試用安全開關覆寫)
// 舊: r13 (2026-09-14) 序列指令 fwurl(測試用更新來源,不存檔);sim pulse 延遲參數
// 舊: r12 (2026-09-14) 韌體更新:開機判斷待確認/退回,loop 推進;序列指令 fw(狀態),fwwin <秒>(測試用縮短確認時限)
// 舊: r11 (2026-09-14) 序列指令 powerontest(下一次軟體重開也允許上電自動倒數,測試用)
// 舊: r10 (2026-09-14) 序列指令 rescuetest(測試連續開關電救援),stadrop(測試斷線重連)
// 舊: r9 (2026-09-14) 序列指令 txp <dBm>:WiFi 發射功率立即生效並存檔(USB 救援)
// 舊: r8 (2026-09-13) 開機初始化機輪收腳舵機(放下位置);pwmcap gear 量 GPIO3
// 舊: r7 (2026-09-13) 測試指令 sim(感測器模擬),pwmcap/pwm(GPIO5 量脈寬),ledcap/led(狀態燈腳位取樣)
// 舊: r6 (2026-09-13) 開機先拉低腳位,載入設定後依協定掛 PWM 或 DShot;序列指令 dshot(回授自我檢查)
// 舊: r5 (2026-09-13) 開機電變校正:上電重置且旗標開啟時,輸出最高油門交給控制工作計時
// 舊: r4 (2026-09-13) 第4階段:序列指令 fs(飛行狀態)/gesture(模擬手勢)/cancel/estop;狀態燈改由控制工作驅動
// 舊: r3 (2026-09-13) 第3階段:開機載入設定,orient 改走設定驗證,加 save 指令
// 舊: r2 (2026-09-13) 第2階段:控制工作拆到 control.cpp,加 WiFi/mDNS/OTA/網頁,序列指令 wifi/net
// 舊: r1 (2026-09-13) 第1階段:電變輸出最低油門,MPU6050姿態,獨立控制工作,序列埠遙測
// ============================================================================
// 線控飛機油門控制器 ESP32-C3 SuperMini
//
// 分工:控制工作(control.cpp,高優先權 200Hz)負責感測器與電變;
//       Arduino loop(本檔)負責序列埠,WiFi,網頁,OTA,永遠不直接碰 I2C 或電變.
// ============================================================================
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include "pins_config.h"
#include "esc_output.h"
#include "esc_service.h"
#include "event_log.h"
#include "imu.h"
#include "control.h"
#include "settings.h"
#include "settings_backup.h"
#include "buzzer.h"
#include "flight.h"
#include "fw_update.h"
#include "wifi_manager.h"
#include "web_server.h"
#include "test_hooks.h"
#include "gear.h"

static const uint16_t SERIAL_TX_BUFFER_BYTES = 2048;
static bool telemetryPrint = false;

static void printTelemetry() {
  Telemetry t;
  controlGetTelemetry(t);
  Serial.printf("P=%+6.1f R=%+6.1f |a|=%.2f g=%+6.1f,%+6.1f,%+6.1f still=%d(%.1fs) bias=%+.2f,%+.2f,%+.2f esc=%u exec=%luus late=%lums%s\n",
                t.pitchDeg, t.rollDeg, t.accMagG, t.gyroDps[0], t.gyroDps[1], t.gyroDps[2], t.still ? 1 : 0,
                t.stillSeconds, t.biasDps[0], t.biasDps[1], t.biasDps[2], t.escUs, (unsigned long)t.maxExecUs,
                (unsigned long)t.maxLateMs, !t.imuPresent ? " NO_IMU" : (t.imuFault ? " IMU_FAULT" : ""));
}

static void printNet() {
  static const char *const names[] = {"connecting", "sta", "ap"};
  const WifiConfig &c = wifiConfig();
  Serial.printf("wifi=%s ip=%s rssi=%d host=%s.local ssid=%s txp=%udBm\n", names[wifiState()], wifiIpText().c_str(),
                (int)wifiRssi(), c.host, c.ssid, (unsigned)c.txPowerDbm);
}

static void printFlight() {
  static const char *const names[] = {"arming", "standby", "wait_still", "countdown", "takeoff", "flying", "landing", "done"};
  FlightStatus f;
  flightGetStatus(f);
  Serial.printf("state=%s %.1fs cd=%.1f t=%.1f base=%.1f comp=%.1f out=%.1f ph=%u land=%u end=%u reject=%u settle=%.1f\n",
                names[f.state], f.stateSeconds, f.countdownRemainS, f.flightSeconds, f.basePct, f.compPct, f.outPct,
                (unsigned)f.phase, (unsigned)f.landingCause, (unsigned)f.endReason, (unsigned)f.rejectReason, f.settleSeconds);
}

static int8_t parseAxis(const String &s) {
  if (s.length() != 2) return -1;
  const char sign = s[0], axis = s[1];
  if ((sign != '+' && sign != '-') || axis < 'x' || axis > 'z') return -1;
  return (int8_t)((axis - 'x') * 2 + (sign == '-' ? 1 : 0));
}

// I2C 匯流排解鎖(2026-09-14):板子在感測器正傳資料時重開(燒錄重置,軟體重開,韌體更新,電壓不足),感測器會一直
// 拉住 SDA 等時脈,之後每次讀取都失敗(ESP_ERR_INVALID_STATE),要感測器斷電才恢復 —— USB 供電的開發板燒錄後遇過.
// 開機先用 GPIO 送最多 16 個 SCL 脈衝讓它把這個位元組送完,再送 STOP. 匯流排正常(SDA 高)時只送 STOP,無害.
// 回傳 true = 開機時匯流排是卡住的.
static bool i2cBusRecover(uint8_t sda, uint8_t scl) {
  pinMode(sda, INPUT_PULLUP);
  pinMode(scl, OUTPUT_OPEN_DRAIN);
  digitalWrite(scl, HIGH);
  delay(1);
  const bool stuck = digitalRead(sda) == LOW;
  for (uint8_t i = 0; i < 16 && digitalRead(sda) == LOW; ++i) {
    digitalWrite(scl, LOW);
    delayMicroseconds(10);
    digitalWrite(scl, HIGH);
    delayMicroseconds(10);
  }
  // STOP:SCL 低時拉低 SDA,放開 SCL,再放開 SDA(SCL 高時 SDA 由低變高)
  digitalWrite(scl, LOW);
  delayMicroseconds(10);
  pinMode(sda, OUTPUT_OPEN_DRAIN);
  digitalWrite(sda, LOW);
  delayMicroseconds(10);
  digitalWrite(scl, HIGH);
  delayMicroseconds(10);
  digitalWrite(sda, HIGH);
  delayMicroseconds(10);
  pinMode(sda, INPUT);
  pinMode(scl, INPUT);
  return stuck;
}

static void scanI2c() {
  uint8_t found = 0;
  for (uint8_t addr = 1; addr < 127; ++addr) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("I2C 0x%02X\n", addr);
      ++found;
    }
  }
  Serial.printf("scan SDA=%u SCL=%u found=%u\n", PIN_I2C_SDA, PIN_I2C_SCL, found);
}

static void scanAllPins() {
  // 找感測器接在哪兩隻腳:逐對換腳位掃描常見位址. 避開 GPIO4(電變)與 GPIO18/19(USB).
  // I2C 是開汲極,掃到沒接 I2C 的腳也只是短暫拉低,無害. 掃完恢復成 pins_config.h 的腳位.
  static const uint8_t pins[] = {0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 20, 21};
  static const uint8_t addrs[] = {0x68, 0x69};
  esp_log_level_set("*", ESP_LOG_NONE);
  for (uint8_t a : pins) {
    for (uint8_t b : pins) {
      if (a == b) continue;
      Wire.end();
      if (!Wire.begin(a, b, 100000UL)) continue;
      Wire.setTimeOut(5);
      for (uint8_t addr : addrs) {
        Wire.beginTransmission(addr);
        if (Wire.endTransmission() == 0) Serial.printf("FOUND SDA=%u SCL=%u addr=0x%02X\n", a, b, addr);
      }
    }
    delay(1);
  }
  Wire.end();
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(400000UL);
  Wire.setTimeOut(10);
  esp_log_level_set("*", ESP_LOG_ERROR);
  Serial.println(F("scanall done"));
}

static void handleSerial() {
  if (!Serial.available()) return;
  const String raw = Serial.readStringUntil('\n');
  String line = raw;
  line.trim();
  line.toLowerCase();

  if (line == "t") {
    telemetryPrint = !telemetryPrint;
  } else if (line == "net") {
    printNet();
  } else if (line == "fs") {
    printFlight();
  } else if (line == "gesture") {
    flightRequestGesture();   // 測試用:當作做了一次啟動手勢(仍會檢查未儲存變更與感測器)
    Serial.println(F("OK gesture requested"));
  } else if (line == "disturb") {
    flightRequestDisturb();   // 測試用:倒數中當作偵測到一次外力
    Serial.println(F("OK disturb requested"));
  } else if (line == "tilt") {
    flightRequestTilt();      // 測試用:等待放穩/倒數中當作角度超過水平限制
    Serial.println(F("OK tilt requested"));
  } else if (line == "twist") {
    flightRequestTwist();     // 測試用:等待放穩/倒數中當作扭轉機尾超過角度
    Serial.println(F("OK twist requested"));
  } else if (line == "cancel") {
    flightRequestCancel();
    Serial.println(F("OK cancel requested"));
  } else if (line == "estop") {
    flightRequestEstop();
    Serial.println(F("OK estop requested"));
  } else if (line == "sim" || line.startsWith("sim ")) {
    // 測試用感測器模擬(說明見 test_hooks.h)
    char buf[200];
    testSimCommand(line.length() > 4 ? line.c_str() + 4 : "", buf, sizeof(buf));
    Serial.println(buf);
  } else if (line.startsWith("pwmcap")) {
    // GPIO5 跳線量 GPIO4 的脈寬:pwmcap on | off | reset;pwmcap gear 直接量 GPIO3 收輪舵機腳位自己的電位
    if (line.endsWith("off")) testPwmCapStop();
    else if (line.endsWith("reset")) testPwmCapResetMinMax();
    else if (line.endsWith("gear")) testPwmCapStartPin(PIN_GEAR_SERVO);
    else if (!TEST_GPIO5_AVAILABLE) {   // GPIO5 接感測器 I2C,不能拿來量脈寬
      Serial.println(F("ERR pwmcap: GPIO5 is I2C on this board"));
      return;
    } else if (escActiveProtocol() != ESC_PROTO_PWM50) {
      Serial.println(F("ERR pwmcap PWM only"));
      return;
    } else testPwmCapStart();
    Serial.println(F("OK pwmcap"));
  } else if (line == "pwm") {
    PwmCapStats c;
    testPwmCapGet(c);
    Serial.printf("pwm active=%d pulses=%lu high=%lu period=%lu min=%lu max=%lu age=%lu\n", c.active ? 1 : 0,
                  (unsigned long)c.pulses, (unsigned long)c.highUs, (unsigned long)c.periodUs, (unsigned long)c.minHighUs,
                  (unsigned long)c.maxHighUs, (unsigned long)c.edgeAgeMs);
  } else if (line.startsWith("ledcap")) {
    // 狀態燈腳位取樣:ledcap [毫秒],預設 3000;完成後用 led 讀結果
    const long ms = line.length() > 7 ? line.substring(7).toInt() : 3000;
    testLedCaptureStart((uint32_t)constrain(ms, 200, 20000));
    Serial.println(F("OK ledcap"));
  } else if (line == "led") {
    char buf[400];
    testLedCaptureReport(buf, sizeof(buf));
    Serial.println(buf);
  } else if (line == "dshot") {
    // DShot 回授自我檢查:在同一腳位收一個訊框解碼(不需要接電變或示波器)
    char buf[160];
    const bool ok = escDshotSelfTest(buf, sizeof(buf));
    Serial.printf("%s dshot %s\n", ok ? "OK" : "ERR", buf);
  } else if (line == "rpmtest" || line.startsWith("rpmtest ")) {
    // 雙向回傳解碼自我測試:rpmtest [週期µs],預設 1000µs(= 60000 eRPM)
    const long p = line.length() > 8 ? line.substring(8).toInt() : 1000;
    char buf[200];
    const bool ok = escRpmSelfTest((uint32_t)constrain(p, 1, 65408), buf, sizeof(buf));
    Serial.printf("%s rpmtest %s\n", ok ? "OK" : "ERR", buf);
  } else if (line.startsWith("escemu")) {
    // 模擬電變(GPIO5 跳線接 GPIO4):escemu <週期µs> 開始/換週期,escemu stop 回傳「馬達停止」,escemu off 停止模擬
    const String arg = line.length() > 7 ? line.substring(7) : String("");
    if (arg == "off") {
      escEmuStop();
      Serial.println(F("OK escemu off"));
    } else if (!TEST_GPIO5_AVAILABLE) {   // GPIO5 接感測器 I2C
      Serial.println(F("ERR escemu: GPIO5 is I2C on this board"));
    } else {
      const char *err = escEmuStart(arg == "stop" ? 0xFFFF : (uint32_t)constrain(arg.toInt(), 1, 65408));
      Serial.println(err ? String("ERR escemu ") + err : String("OK escemu on"));
    }
  } else if (line == "emu") {
    EscEmuStats e;
    escEmuGetStats(e);
    Serial.printf("emu frames=%lu crcok=%lu replies=%lu value=%lu period=%lu\n", (unsigned long)e.frames,
                  (unsigned long)e.frameCrcOk, (unsigned long)e.replies, (unsigned long)e.lastValue, (unsigned long)e.periodUs);
  } else if (line == "rpm") {
    EscRpmStats r;
    escRpmGetStats(r);
    Serial.printf("rpm active=%d frames=%lu replies=%lu ok=%lu bad=%lu noreply=%lu period=%lu\n", escRpmActive() ? 1 : 0,
                  (unsigned long)r.frames, (unsigned long)r.replies, (unsigned long)r.ok, (unsigned long)r.bad,
                  (unsigned long)r.noReply, (unsigned long)r.periodUs);
  } else if (line == "timing") {
    controlResetTimingStats();
    Serial.println(F("OK timing stats cleared"));
  } else if (line.startsWith("wifi ") || line == "wifi") {
    // wifi <名稱> <密碼>:SSID 與密碼區分大小寫,所以從原文切詞,不用小寫化後的字串.
    // 用 USB 救援:WiFi 設錯連不上時不必拿手機連熱點. 名稱或密碼含空白請用網頁設定.
    String args = raw;
    args.trim();
    args = args.substring(4);
    args.trim();
    const int sp = args.indexOf(' ');
    WifiConfig c = wifiConfig();
    const String ssid = sp < 0 ? args : args.substring(0, sp);
    const String pw = sp < 0 ? String("") : args.substring(sp + 1);
    if (ssid.length() == 0 || ssid.length() >= WIFI_SSID_BUFFER || pw.length() >= WIFI_PASS_BUFFER) {
      Serial.println(F("ERR usage: wifi <ssid> <password>"));
      return;
    }
    memset(c.ssid, 0, sizeof(c.ssid));
    memset(c.password, 0, sizeof(c.password));
    strncpy(c.ssid, ssid.c_str(), sizeof(c.ssid) - 1);
    strncpy(c.password, pw.c_str(), sizeof(c.password) - 1);
    c.forceAp = false;
    const char *err = wifiSaveConfig(c);
    Serial.println(err ? String("ERR ") + err : String("OK saved, type 'reboot' to connect"));
  } else if (line.startsWith("txp ")) {
    // txp <dBm>:WiFi 發射功率立即生效並存檔. USB 救援用:網頁拉桿調太大連不上時(GG 2026-09-14).
    const long dbm = line.substring(4).toInt();
    if (dbm < WIFI_TX_POWER_MIN_DBM || dbm > WIFI_TX_POWER_MAX_DBM || String(dbm) != line.substring(4)) {
      Serial.printf("ERR usage: txp <%u~%u>\n", WIFI_TX_POWER_MIN_DBM, WIFI_TX_POWER_MAX_DBM);
      return;
    }
    wifiApplyTxPower((uint8_t)dbm);
    WifiConfig c = wifiConfig();
    c.txPowerDbm = (uint8_t)dbm;
    const char *err = wifiSaveConfig(c);
    Serial.println(err ? String("ERR ") + err : String("OK txp ") + dbm + "dBm applied and saved");
  } else if (line == "stadrop" || line == "stadrop hold") {
    // 測試用:讓家用 WiFi 斷線一次(驗證斷線自動重連);hold = 不重連(驗證斷線太久改開熱點)
    wifiTestDropSta(line == "stadrop hold");
    Serial.println(F("OK sta dropped"));
  } else if (line.startsWith("fwwin ")) {
    // 測試用:這次開機的新韌體確認時限改成 N 秒(驗證沒確認自動退回,不用等 1 分鐘)
    const long sec = line.substring(6).toInt();
    if (sec < 10 || sec > 600 || String(sec) != line.substring(6)) {
      Serial.println(F("ERR usage: fwwin <10~600>"));
      return;
    }
    fwUpdateTestSetWindow((uint16_t)sec);
    Serial.printf("OK confirm window %lds\n", sec);
  } else if (line == "fwurl off" || line.startsWith("fwurl https://")) {
    // 測試用:暫時改讀別的更新來源(公開專案的測試分支),不存檔,重開即恢復正式來源
    String url = raw;   // 網址大小寫有差,不能用轉小寫後的 line
    url.trim();
    const bool ok = fwUpdateTestSetBaseUrl(line == "fwurl off" ? "" : url.c_str() + 6);
    Serial.println(ok ? F("OK fw source set") : F("ERR fwurl https://.../ (ends with /) or busy"));
  } else if (line == "fw") {
    FwStatus s;
    fwUpdateGetStatus(s);
    Serial.printf("version=%s busy=%d pending=%d remain=%.0f rolledBack=%d(%s) check=%u err=%s remote=%s size=%lu prog=%u\n", FW_VERSION,
                  s.busy, s.pending, s.confirmRemainS, s.rolledBack, s.rolledBackFrom, s.check, s.err, s.remoteVersion,
                  (unsigned long)s.remoteSize, s.progress);
  } else if (line.startsWith("calexp ")) {
    // 測試用:校正旗標時效改成 N 秒(預設 600)
    const long sec = line.substring(7).toInt();
    if (sec < 5 || sec > 3600 || String(sec) != line.substring(7)) {
      Serial.println(F("ERR usage: calexp <5~3600>"));
      return;
    }
    escCalibTestSetExpire((uint32_t)sec);
    Serial.printf("OK calib expire %lds\n", sec);
  } else if (line == "armsw 0" || line == "armsw 1" || line == "armsw off") {
    // 測試用:覆寫安全開關(開發板沒接 GPIO21 的微動開關). off = 讀真的腳位
    testArmOverrideSet(line == "armsw off" ? -1 : (line == "armsw 1" ? 1 : 0));
    Serial.println(line == "armsw off" ? F("OK armsw real pin") : (line == "armsw 1" ? F("OK armsw pressed") : F("OK armsw released")));
  } else if (line == "armwait off" || line.startsWith("armwait ")) {
    // 測試用:安全開關等待上限改成 N 秒(設定最少 1 分鐘,測試不想等). off = 用設定值. 軟體重開保留
    const long sec = line == "armwait off" ? 0 : line.substring(8).toInt();
    if (line != "armwait off" && (sec < 5 || sec > 600 || String(sec) != line.substring(8))) {
      Serial.println(F("ERR usage: armwait <5~600>|off"));
      return;
    }
    testArmWaitOverrideSet((uint16_t)sec);
    Serial.printf("OK armwait %lds\n", sec);
  } else if (line == "powerontest") {
    // 測試用:下一次軟體重開也允許「上電後直接倒數」(平常只有真的拔電再接電才會自動倒數). 電變校正不受影響.
    Serial.println(escPowerOnTestArm() ? F("OK next reboot allows auto countdown") : F("ERR savefail"));
  } else if (line == "rescuetest") {
    // 測試用:下一次軟體重開也算一次「上電」(桌上 USB 供電沒辦法真的斷電,用來測連續開關電救援)
    wifiRescueTestArm();
    Serial.println(F("OK next reboot counts as power-on"));
  } else if (line == "reboot") {
    ESP.restart();
  } else if (line.startsWith("orient ")) {
    // orient <機頭軸> <機背軸>,例如 orient +x +z. 與網頁走同一套設定驗證,要保留請在網頁按儲存.
    const int sp = line.indexOf(' ', 7);
    const int8_t nose = parseAxis(line.substring(7, sp));
    const int8_t up = sp > 0 ? parseAxis(line.substring(sp + 1)) : -1;
    if (nose < 0 || up < 0) {
      Serial.println(F("ERR usage: orient +x +z"));
      return;
    }
    // 兩軸要一起換:逐項設定時中間狀態可能兩軸相同而被拒絕,所以先把機背軸移開再設.
    char nb[4], ub[4];
    snprintf(nb, sizeof(nb), "%d", nose);
    snprintf(ub, sizeof(ub), "%d", up);
    const uint8_t spare = (uint8_t)((3 - nose / 2 - up / 2) * 2);   // 第三軸
    char sb[4];
    snprintf(sb, sizeof(sb), "%u", spare);
    const char *err = settingsSet(-1, "upAxis", sb);
    if (!err) err = settingsSet(-1, "noseAxis", nb);
    if (!err) err = settingsSet(-1, "upAxis", ub);
    Serial.println(err ? String("ERR ") + err : String("OK (unsaved)"));
  } else if (line == "save") {
    const char *err = settingsSave();
    Serial.println(err ? String("ERR ") + err : String("OK saved"));
  } else if (line == "scan" || line == "scanall" || line == "mpu") {
    // 只在感測器不在線時允許:控制工作在線時會用 Wire,兩邊不能同時碰匯流排.
    if (controlImuPresent()) {
      Serial.println(F("ERR MPU in use"));
      return;
    }
    if (line == "scan") scanI2c();
    else if (line == "scanall") scanAllPins();
    else {
      Wire.end();
      if (i2cBusRecover(PIN_I2C_SDA, PIN_I2C_SCL)) Serial.println(F("I2C bus was stuck (SDA low), recovered"));
      Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
      Wire.setClock(400000UL);
      Wire.setTimeOut(10);
      const bool ok = imuBegin();
      Serial.println(ok ? F("MPU OK") : F("ERR MPU (no reply on I2C, check wiring / pull-ups)"));
      controlSetImuPresent(ok);
    }
  } else if (line.length()) {
    Serial.println(F("commands: t | net | fs | gesture | disturb | twist | tilt | cancel | estop | sim ... | pwmcap on|off|reset | pwm | ledcap [ms] | led | dshot | rpm | rpmtest [us] | timing | wifi <ssid> <pw> | txp <dBm> | fw | fwwin <s> | calexp <s> | armsw 0|1|off | armwait <s>|off | powerontest | rescuetest | reboot | orient +x +z | save | mpu | scan | scanall"));
  }
}

void setup() {
  // 第一件事:電變腳位拉低,不留任何浮空或亂脈衝的空窗.
  escPinLow();
  // 事件紀錄第一筆:這次為什麼開機(飛行中板子重開時,馬達停的真正原因在這裡)
  eventLog(EV_BOOT, 0, (float)esp_reset_reason());
  // 讀完設定才掛輸出:協定(PWM/DShot)要一開始就對,電變多半只在上電時判斷一次訊號種類.
  // 電變校正精靈:只有上電重置才會進入(見 esc_service.h),而且只限 PWM;開機第一個脈衝就是最高油門.
  // 腳位低電位的這幾十毫秒電變看到的是「沒有訊號」,不會動作.
  const bool calibFlag = escCalibTakeAtBoot();
  settingsBegin();   // 在控制工作啟動前載入:協定,脈寬,安裝方位與角度修正要先就位
  backupSelfCheck();
  buzzerBegin(sharedSettings.buzzerActiveLow != 0);   // 電位看設定,所以在載入設定之後
  const bool escCalibrate = calibFlag && sharedSettings.escProtocol == ESC_PROTO_PWM50;
  const bool escOk = escBegin(sharedSettings.escProtocol, escCalibrate ? sharedSettings.escMaxUs : ESC_US_SAFE_IDLE,
                              sharedSettings.escPwmHz, sharedSettings.escRpmTelemetry != 0);
  if (!escOk) eventLog(EV_REJECT, REJECT_ESC_OUTPUT);   // 腳位沒訊號:記一筆,起飛時也會被拒
  const uint32_t escCalibStartMs = millis();
  gearBegin(sharedSettings);   // 機輪收腳舵機:開機一律輸出放下位置

  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, STATUS_LED_ACTIVE_LOW ? HIGH : LOW);   // 解鎖期間熄滅,之後由控制工作依狀態驅動

  // USB CDC:沒有人讀序列埠時 write 預設會卡住呼叫端最久約 2 秒(參考專案實測),
  // 逾時設 0 永不等待. 緩衝要在 begin() 之前設.
  Serial.setTxBufferSize(SERIAL_TX_BUFFER_BYTES);
  Serial.setTxTimeoutMs(0);
  Serial.begin(115200);

  const bool i2cWasStuck = i2cBusRecover(PIN_I2C_SDA, PIN_I2C_SCL);   // 上次在感測器傳資料到一半時重開,匯流排會卡住
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(400000UL);
  Wire.setTimeOut(10);   // 線斷掉時單次讀取最多卡 10ms,不拖垮控制節拍

  const bool imuOk = imuBegin();
  if (i2cWasStuck) Serial.println(F("I2C bus was stuck at boot (SDA low), recovered"));
  Serial.println(imuOk ? F("MPU OK") : F("ERR MPU"));
  {
    static const char *const protoNames[] = {"PWM", "DShot150", "DShot300"};
    Serial.printf("ESC protocol %s %uHz\n", protoNames[escActiveProtocol() <= 2 ? escActiveProtocol() : 0], escActivePwmHz());
  }
  if (calibFlag && !escCalibrate) Serial.println(F("ESC calibration flag ignored (DShot needs no calibration)"));
  if (escCalibrate) eventLog(EV_CALIB_START, 0, sharedSettings.escMaxUs, sharedSettings.calibHoldSec);
  if (!imuOk) eventLog(EV_IMU_FAULT, 2);   // 2 = 開機時就找不到感測器
  if (escCalibrate) Serial.printf("ESC calibration: output %uus for %.1fs\n", sharedSettings.escMaxUs, sharedSettings.calibHoldSec);
  else if (escCalibPending()) Serial.println(F("ESC calibration pending (waits for a power-on reset)"));
  testArmOverrideBoot();   // 測試用安全開關覆寫(軟體重開保留),要在控制工作開始讀之前
  fwUpdateBegin();   // 新韌體待確認或上次更新被退回;要在控制工作讀 fwUpdateBlockReason 之前設好(安全審查 2-F:原本在控制工作之後)
  controlBegin(imuOk, escCalibrate, escCalibStartMs);

  Serial.printf("FW version %s I2C SDA=%u SCL=%u\n", FW_VERSION, PIN_I2C_SDA, PIN_I2C_SCL);
  if (testArmOverride() >= 0) Serial.printf("TEST armsw override %d (kept across soft reboot)\n", testArmOverride());
  if (testArmWaitOverride()) Serial.printf("TEST armwait override %us (kept across soft reboot)\n", (unsigned)testArmWaitOverride());
  wifiBegin();
  Serial.println(F("READY (type 'help')"));
}

void loop() {
  handleSerial();
  wifiTick();
  webTick();
  fwUpdateTick(millis());
  escCalibTick(millis());   // 校正旗標時效
  static uint32_t lastPrintMs = 0;
  const uint32_t now = millis();
  if (telemetryPrint && now - lastPrintMs >= 200) {
    lastPrintMs = now;
    printTelemetry();
  }
  delay(2);
}
