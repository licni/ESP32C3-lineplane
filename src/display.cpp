// 版本流水號: r2 (2026-09-25) WiFi 頁只留模式與 IP,IP 用 7x14 粗體分兩行;輪播狀態頁 4 秒,WiFi 頁 6 秒(GG)
// 舊: r1 (2026-09-25) 初版(GG):帶螢幕板 0.42 吋 OLED(72x40)顯示油門,動力階段,起飛程序,取消/拒絕原因,WiFi 與 IP
#include "display.h"
#include "pins_config.h"

#if BOARD_C3_OLED
#include <U8g2lib.h>
#include <Wire.h>
#include "control.h"
#include "flight.h"
#include "wifi_manager.h"

// 72x40 裝得下:小字 5x8 一行 14 字,5 行;大字 logisoso18 放油門與倒數. 太長的行自動換 4x6 小字(18 字).
// 螢幕太小放不下中文字型,畫面文字用英文縮寫(對照表見開發紀錄).
static const uint8_t OLED_ADDR = 0x3C;
static const uint32_t FRAME_MS = 200;
static const uint32_t STATUS_PAGE_MS = 4000;   // 地面資訊輪播:狀態頁 4 秒,WiFi 頁 6 秒(GG:WiFi 停留太短)
static const uint32_t WIFI_PAGE_MS = 6000;
static const uint32_t REJECT_SHOW_MS = 6000;   // 拒絕啟動原因顯示多久
static const uint8_t FAIL_LIMIT = 5;           // 連續幾張畫面傳輸失敗就停用

static uint8_t i2cErrors = 0;

// I2C 傳輸自己做:不讓 U8g2 呼叫 Wire.begin / setClock(會動到感測器用的腳位與速度).
static uint8_t byteCb(u8x8_t *u8x8, uint8_t msg, uint8_t argInt, void *argPtr) {
  switch (msg) {
    case U8X8_MSG_BYTE_SEND: Wire.write((const uint8_t *)argPtr, argInt); break;
    case U8X8_MSG_BYTE_START_TRANSFER: Wire.beginTransmission(u8x8_GetI2CAddress(u8x8) >> 1); break;
    case U8X8_MSG_BYTE_END_TRANSFER:
      if (Wire.endTransmission() != 0 && i2cErrors < 255) ++i2cErrors;
      break;
    case U8X8_MSG_BYTE_INIT:
    case U8X8_MSG_BYTE_SET_DC: break;
    default: return 0;
  }
  return 1;
}

static uint8_t gpioCb(u8x8_t *, uint8_t msg, uint8_t argInt, void *) {
  if (msg == U8X8_MSG_DELAY_MILLI) delay(argInt);
  return 1;
}

class Oled : public U8G2 {
 public:
  Oled() { u8g2_Setup_ssd1306_i2c_72x40_er_f(&u8g2, U8G2_R0, byteCb, gpioCb); }
};

static Oled oled;
static bool ready = false;
static uint8_t failFrames = 0;
static uint32_t lastFrameMs = 0;
static uint8_t lastBuf[9 * 8 * 5];   // 72x40 = 9x5 格,每格 8 位元組

static const char *endText(uint8_t r) {
  switch (r) {
    case END_TOUCH_SPIKE: return "Touchdown";
    case END_TOUCH_STILL: return "Landed(still)";
    case END_TOUCH_ROLL: return "Landed(roll)";
    case END_LANDING_TIMEOUT: return "Land timeout";
    case END_CRASH: return "CRASH STOP";
    case END_ESTOP: return "E-STOP(web)";
    case END_CANCELED: return "Canceled";
    case END_TWIST_CANCEL: return "Twist cancel";
    case END_TILT_CANCEL: return "Tilt cancel";
    case END_ARM_TIMEOUT: return "Switch timeout";
    case END_FORCE_SWITCH: return "Force:switch";
    case END_FORCE_WAG: return "Force:wag";
    default: return "";
  }
}

static const char *rejectText(uint8_t r) {
  switch (r) {
    case REJECT_UNSAVED: return "Unsaved set";
    case REJECT_IMU: return "IMU error";
    case REJECT_TILT: return "Not level";
    case REJECT_TILT_WAIT: return "Wait level";
    case REJECT_FW_UPDATING: return "FW updating";
    case REJECT_FW_UNCONFIRMED: return "FW not confirm";
    case REJECT_ARM_SWITCH:
    case REJECT_ARM_WAIT: return "Safety switch";
    case REJECT_CRASH_LOCK: return "Crash lock";
    case REJECT_ESC_OUTPUT: return "ESC no signal";
    default: return "?";
  }
}

// 第 row 行(0~4)小字;超過寬度換 4x6
static void line(uint8_t row, const char *s) {
  if (strlen(s) * 5 > 72) {
    oled.setFont(u8g2_font_4x6_tf);
    oled.drawStr(0, row * 8 + 6, s);
  } else {
    oled.setFont(u8g2_font_5x8_tf);
    oled.drawStr(0, row * 8 + 7, s);
  }
}

// 標題列反白
static void title(const char *s) {
  oled.drawBox(0, 0, 72, 8);
  oled.setDrawColor(0);
  line(0, s);
  oled.setDrawColor(1);
}

// 大字置中(第 1~3 行的位置)
static void big(const char *s) {
  oled.setFont(u8g2_font_logisoso18_tr);
  const int w = oled.getStrWidth(s);
  oled.drawStr(max(0, (72 - w) / 2), 30, s);
}

static void bigPage(const char *t, const char *b, const char *bottom) {
  title(t);
  big(b);
  line(4, bottom);
}

// WiFi 頁(GG 2026-09-25:只留模式與 IP,IP 用大字):IP 在第二個點後斷成兩行,例如 "192.168." / "0.15"
static void wifiPage() {
  char buf[40];
  const WifiState ws = wifiState();
  title(ws == WIFI_STATE_STA ? "WiFi: HOME" : ws == WIFI_STATE_AP ? "WiFi: HOTSPOT" : "WiFi: connect");
  if (ws == WIFI_STATE_CONNECTING) {
    snprintf(buf, sizeof(buf), "hotspot in %us", (unsigned)wifiStaCountdownSeconds());
    line(2, buf);
    return;
  }
  const String ip = wifiIpText();
  int cut = ip.indexOf('.');
  cut = cut < 0 ? -1 : ip.indexOf('.', cut + 1);
  oled.setFont(u8g2_font_7x14B_tf);   // 一行 10 字,兩行各最多 8 字("255.255." / "255.255")
  if (cut < 0) {
    oled.drawStr(0, 24, ip.c_str());
  } else {
    oled.drawStr(0, 22, ip.substring(0, cut + 1).c_str());
    oled.drawStr(0, 38, ip.substring(cut + 1).c_str());
  }
}

// 地面狀態頁:第 0 行狀態,第 1 行說明,第 2 行風格與感測器,第 3 行角度,第 4 行上次結束原因
static void groundPage(const FlightStatus &f, const Telemetry &t, const char *state, const char *detail) {
  char buf[32];
  title(state);
  line(1, detail);
  snprintf(buf, sizeof(buf), "Prof %u %s", (unsigned)f.flightProfile + 1,
           !t.imuPresent ? "NO IMU" : t.imuFault ? "IMU ERR" : "IMU OK");
  line(2, buf);
  if (t.imuPresent && !t.imuFault) {
    snprintf(buf, sizeof(buf), "P%+.1f R%+.1f", t.pitchDeg, t.rollDeg);
    line(3, buf);
  }
  if (f.endReason != END_NONE) {
    snprintf(buf, sizeof(buf), "last:%s", endText(f.endReason));
    line(4, buf);
  }
}

static const char *powerTitle(const FlightStatus &f) {
  if (f.state == FS_TAKEOFF) return "SOFT START";
  if (f.state == FS_LANDING) return f.landPulse ? "LAND PULSE" : f.landingWarn ? "LAND REDUCE" : "WAIT TOUCH";
  if (f.takeoffBoost) return "TAKEOFF PWR";
  if (f.phaseRamp) return "PH1 > PH2";
  return f.phase == 1 ? "PHASE 1" : "PHASE 2";
}

static void render(uint32_t now) {
  FlightStatus f;
  flightGetStatus(f);
  Telemetry t;
  controlGetTelemetry(t);
  char b[24], s[32];
  const bool page2 = now % (STATUS_PAGE_MS + WIFI_PAGE_MS) >= STATUS_PAGE_MS;   // 地面頁輪播:狀態 / WiFi

  oled.clearBuffer();
  if (t.calibState == CALIB_HOLD_MAX) {
    snprintf(b, sizeof(b), "%.0fs", t.calibRemainS);
    bigPage("ESC CALIB", b, "max throttle");
    return;
  }
  if (t.manualActive) {
    snprintf(b, sizeof(b), "%u", t.escUs);
    bigPage("MANUAL OUT", b, "us (web)");
    return;
  }
  const bool ground = f.state == FS_ARMING || f.state == FS_STANDBY || f.state == FS_DONE;
  if (ground && f.rejectReason != REJECT_NONE && f.rejectAgeMs < REJECT_SHOW_MS) {
    title("REJECTED");
    line(2, rejectText(f.rejectReason));
    return;
  }

  switch (f.state) {
    case FS_ARMING:
      if (page2) wifiPage();
      else groundPage(f, t, "ESC ARMING", "wait...");
      break;
    case FS_STANDBY:
      if (f.autoWaitLevel && f.armWaitLeftS >= 0) {
        snprintf(b, sizeof(b), "%.0f", ceilf(f.armWaitLeftS));
        bigPage("PRESS SWITCH", b, "s to cancel");
      } else if (f.autoWaitLevel) {
        title("AUTO START");
        line(2, "level the plane");
      } else if (page2) {
        wifiPage();
      } else {
        groundPage(f, t, f.gestureEnabled ? "READY" : "REPOWER TO FLY",
                   f.gestureBlockS > 0 ? "blocked..." : f.gestureEnabled ? "push to start" : "auto used");
      }
      break;
    case FS_WAIT_STILL:
      if (f.armWaitLeftS >= 0) {
        snprintf(b, sizeof(b), "%.0f", ceilf(f.armWaitLeftS));
        bigPage("PRESS SWITCH", b, "s to cancel");
      } else {
        snprintf(b, sizeof(b), "%.1f", f.settleSeconds);
        bigPage("HOLD STILL", b, "settling (s)");
      }
      break;
    case FS_COUNTDOWN:
      snprintf(b, sizeof(b), "%.1f", f.countdownRemainS);
      snprintf(s, sizeof(s), "Prof %u", (unsigned)f.flightProfile + 1);
      bigPage("COUNTDOWN", b, s);
      break;
    case FS_TAKEOFF:
    case FS_FLYING:
    case FS_LANDING:
      snprintf(b, sizeof(b), "%.0f%%", f.outPct);
      snprintf(s, sizeof(s), "%.0fs P%+.0f", f.flightSeconds, t.pitchDeg);
      bigPage(powerTitle(f), b, s);
      break;
    case FS_DONE:
      if (page2) {
        wifiPage();
      } else {
        title("END");
        line(1, endText(f.endReason));
        snprintf(s, sizeof(s), "flew %.0fs", f.flightSeconds);
        line(2, s);
        line(4, f.gestureEnabled ? "push to restart" : "repower to fly");
      }
      break;
  }
}

void displayBegin() {
  Wire.beginTransmission(OLED_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println(F("OLED not found (0x3C)"));
    return;
  }
  oled.setI2CAddress(OLED_ADDR << 1);
  oled.begin();
  oled.setFontMode(1);
  ready = i2cErrors == 0;
  Serial.println(ready ? F("OLED OK") : F("ERR OLED init"));
}

void displayTick(uint32_t now) {
  if (!ready || now - lastFrameMs < FRAME_MS) return;
  lastFrameMs = now;
  render(now);
  uint8_t *buf = oled.getBufferPtr();
  if (!memcmp(buf, lastBuf, sizeof(lastBuf))) return;   // 畫面沒變不傳,少佔感測器的線
  i2cErrors = 0;
  oled.sendBuffer();
  if (i2cErrors) {
    if (++failFrames >= FAIL_LIMIT) {
      ready = false;
      Serial.println(F("ERR OLED: I2C errors, display disabled until power cycle"));
    }
    return;   // 沒傳成功:下次照樣重傳
  }
  failFrames = 0;
  memcpy(lastBuf, buf, sizeof(lastBuf));
}

#else
void displayBegin() {}
void displayTick(uint32_t) {}
#endif
