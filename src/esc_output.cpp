// 版本流水號: r7 (2026-09-14) DShot 送框失敗不記成已送出(下一拍重送)
// 舊: r6 (2026-09-13) DShot300 雙向轉速回傳(單腳:計時器 2kHz 推挽送反相訊框,送完中斷放開線並接收,接收中斷解 GCR);合成回傳自我測試
// 舊: r5 (2026-09-13) DShot 改 150/300(GG:不需要 600)
// 舊: r4 (2026-09-13) PWM 頻率可調(50~400Hz,開機套用)
// 舊: r3 (2026-09-13) 加 DShot300/600(RMT 硬體連續重送 4kHz),開機依設定協定初始化,回授自我檢查
// 舊: r2 (2026-09-13) escBegin 可指定初始脈寬(電變校正開機直接輸出最高油門)
// 舊: r1 (2026-09-13) 初版:LEDC 50Hz 14bit 脈寬輸出
#include "esc_output.h"
#include "pins_config.h"
#include "settings.h"
#include "driver/gpio.h"
#include "driver/rmt_rx.h"
#include "driver/rmt_tx.h"
#include "esp_timer.h"
#include "hal/gpio_ll.h"

static uint8_t protocol = ESC_PROTO_PWM50;
static uint16_t pwmHz = ESC_PWM_FREQ_HZ;
static volatile uint16_t escUs = 0;
static volatile uint16_t dshotValue = 0xFFFF;

// --- DShot(RMT) ---
// 解析度 20MHz(一格 50ns). DShot300 一位元 3.333µs = 67 格,1 的高電位 75%,0 的高電位 37.5%;
// DShot150 加倍(一位元 6.667µs = 133 格,訊框 107µs). 訊框 16 位元後補低電位到 250µs,整段在 RMT 記憶體裡硬體迴圈重送.
static const uint32_t DSHOT_RMT_RESOLUTION_HZ = 20000000;
static const size_t DSHOT_SYMBOLS = 17;
static rmt_channel_handle_t txChannel = nullptr;
static rmt_encoder_handle_t copyEncoder = nullptr;
static rmt_symbol_word_t frame[DSHOT_SYMBOLS];
static uint16_t bitTicks = 67, oneHighTicks = 50, zeroHighTicks = 25;
static bool looping = false;

void escPinLow() {
  pinMode(PIN_ESC_SIGNAL, OUTPUT);
  digitalWrite(PIN_ESC_SIGNAL, LOW);
}

static void writePwmUs(uint16_t us) {
  if (us < ESC_US_ABSOLUTE_MIN) us = ESC_US_ABSOLUTE_MIN;
  if (us > ESC_US_ABSOLUTE_MAX) us = ESC_US_ABSOLUTE_MAX;
  if (us == escUs) return;
  const uint32_t periodUs = 1000000UL / pwmHz;
  const uint32_t fullScale = 1UL << ESC_PWM_RESOLUTION_BITS;
  const uint32_t duty = ((uint32_t)us * fullScale + periodUs / 2) / periodUs;
  ledcWrite(PIN_ESC_SIGNAL, duty);
  escUs = us;
}

// --- 雙向 DShot(只有 DShot300)---
// 查證紀錄:docs/雙向DShot與EDT查證_2026-09-13.md. 線上反相(閒置高),CRC 取反;電變在訊框結束後約 30µs 用推挽回傳
// 21 位元(5/4 位元率,DShot300 = 2.667µs/位元),GCR 編碼. 單腳做法(參考 esp-fc 與 DShotRMT_NEO):
//   計時器(2kHz,Betaflight 對 DShot300 雙向上限 5kHz)→ 切推挽 → 送訊框(非迴圈)
//   → 送完中斷:切開汲極放開線(內部上拉維持高電位),啟動接收
//   → 接收完中斷:解碼. 下一拍還沒收到就取消接收,算一次沒回傳.
static const uint32_t BIDIR_FRAME_PERIOD_US = 500;
static const uint32_t REPLY_BIT_NS = 2667;               // 375kbps
static bool bidir = false;
static rmt_channel_handle_t rxChannel = nullptr;
static esp_timer_handle_t bidirTimer = nullptr;
static rmt_symbol_word_t bidirFrame[16];                  // 控制工作更新的訊框
static rmt_symbol_word_t txBuf[16];                       // 計時器送出用的複本(傳送期間不可改)
static portMUX_TYPE frameLock = portMUX_INITIALIZER_UNLOCKED;
static rmt_symbol_word_t rxBuf[48];
static rmt_receive_config_t replyRxCfg = {};
static volatile bool gotReply = false;      // 這一框之後收到過像回傳的東西(成功或失敗)
static volatile bool bidirPaused = false;
// 接收通道一直開著,每收完一段就在中斷裡重新啟動接收. 同腳位會收到自己送的訊框(16 個符號),
// 電變回傳最多 21 段電位(≤ 11 個符號),用符號數分辨. 不在送框前停用/啟用接收通道:
// r6 初版那樣做,通道沒回到啟用狀態,中斷每秒 2000 次接收失敗並印錯誤訊息,序列埠塞爆拖垮 WiFi.
static const size_t REPLY_MAX_SYMBOLS = 12;
static EscRpmStats rpm = {};

// GCR 5 位元 → 4 位元(-1 = 無效碼). Betaflight dshot_bitbang_decode.c L83-85,Bluejay/AM32 相同.
static const int8_t GCR_DECODE[32] = {-1, -1, -1, -1, -1, -1, -1, -1, -1, 9,  10, 11, -1, 13, 14, 15,
                                      -1, -1, 2,  3,  -1, 5,  6,  7,  -1, 0,  8,  1,  -1, 4,  12, -1};

static uint16_t dshotPacket(uint16_t value) {
  const uint16_t data = (uint16_t)(value << 1);   // 最低位是遙測請求,不用
  uint16_t crc = (data ^ (data >> 4) ^ (data >> 8)) & 0x0F;
  if (bidir) crc = ~crc & 0x0F;                    // 雙向:CRC 取反(電變靠這個分辨)
  return (uint16_t)((data << 4) | crc);
}

// 解碼一次回傳. RMT 接收到的是電位長度(level,duration),換成位元數後拼成 21 位元,
// 再 NRZI(v ^ v>>1)→ 20 位元 GCR → 16 位元 → 檢查取反 CRC. 成功回週期 µs(0xFFFF = 馬達停止),失敗回 0.
static uint32_t IRAM_ATTR decodeReply(const rmt_symbol_word_t *sym, size_t n) {
  uint32_t v = 0;
  uint32_t bits = 0;
  for (size_t i = 0; i < n && bits < 21; ++i) {
    for (uint8_t h = 0; h < 2 && bits < 21; ++h) {
      const uint32_t dur = h ? sym[i].duration1 : sym[i].duration0;
      const uint32_t level = h ? sym[i].level1 : sym[i].level0;
      if (dur == 0) break;
      if (bits == 0 && level != 0) return 0;   // 回傳一定以低電位(起始位元)開頭
      uint32_t cnt = (dur * 50 + REPLY_BIT_NS / 2) / REPLY_BIT_NS;
      if (cnt == 0) cnt = 1;
      if (bits + cnt > 21) cnt = 21 - bits;    // 最後一段高電位和閒置連在一起,只取到 21 位元
      v = (v << cnt) | (level ? ((1UL << cnt) - 1) : 0);
      bits += cnt;
    }
  }
  if (bits < 5) return 0;
  if (bits < 21) {                              // 結尾的高電位量不到長度(接收因閒置結束),補 1
    const uint32_t pad = 21 - bits;
    v = (v << pad) | ((1UL << pad) - 1);
  }
  const uint32_t gcr = (v ^ (v >> 1)) & 0xFFFFF;
  uint16_t v16 = 0;
  for (int k = 0; k < 4; ++k) {
    const int8_t nib = GCR_DECODE[(gcr >> (15 - 5 * k)) & 0x1F];
    if (nib < 0) return 0;
    v16 = (uint16_t)((v16 << 4) | nib);
  }
  if (((v16 ^ (v16 >> 4) ^ (v16 >> 8) ^ (v16 >> 12)) & 0x0F) != 0x0F) return 0;   // 取反 CRC
  const uint16_t v12 = v16 >> 4;
  if (v12 == 0x0FFF) return 0xFFFF;             // 馬達停止
  const uint32_t period = (uint32_t)(v12 & 0x1FF) << (v12 >> 9);
  return period;                                 // 0 視為無效
}

static bool IRAM_ATTR onBidirTxDone(rmt_channel_handle_t, const rmt_tx_done_event_data_t *, void *) {
  gpio_ll_od_enable(GPIO_LL_GET_HW(GPIO_PORT_0), PIN_ESC_SIGNAL);   // 放開線,電變 30µs 後回傳
  return false;
}

static bool IRAM_ATTR onBidirRxDone(rmt_channel_handle_t, const rmt_rx_done_event_data_t *ev, void *) {
  if (ev->num_symbols > 0 && ev->num_symbols <= REPLY_MAX_SYMBOLS) {   // 像電變回傳(自己的訊框是 16 個符號,略過)
    gotReply = true;
    ++rpm.replies;
    const uint32_t p = decodeReply(ev->received_symbols, ev->num_symbols);
    if (p == 0) {
      ++rpm.bad;
    } else {
      ++rpm.ok;
      rpm.periodUs = p;
      rpm.lastOkMs = (uint32_t)(esp_timer_get_time() / 1000);
    }
  }
  // 馬上重新接收:自己的訊框收完約 15µs 後,電變在訊框結束後 30µs 才開始回傳
  rmt_receive(rxChannel, rxBuf, sizeof(rxBuf), &replyRxCfg);
  return false;
}

static void bidirTick(void *) {
  if (bidirPaused) return;
  if (rpm.frames && !gotReply) ++rpm.noReply;   // 上一框之後沒收到回傳
  gotReply = false;
  portENTER_CRITICAL(&frameLock);
  memcpy(txBuf, bidirFrame, sizeof(txBuf));
  portEXIT_CRITICAL(&frameLock);
  gpio_ll_od_disable(GPIO_LL_GET_HW(GPIO_PORT_0), PIN_ESC_SIGNAL);  // 送訊框時推挽,邊緣才夠陡
  rmt_transmit_config_t tc = {};
  if (rmt_transmit(txChannel, copyEncoder, txBuf, sizeof(txBuf), &tc) == ESP_OK) ++rpm.frames;
}

static void writeDshot(uint16_t value) {
  if (value == dshotValue || !txChannel) return;
  const uint16_t packet = dshotPacket(value);
  for (uint8_t i = 0; i < 16; ++i) {
    const bool one = packet & (0x8000 >> i);
    const uint16_t high = one ? oneHighTicks : zeroHighTicks;
    frame[i].level0 = 1;
    frame[i].duration0 = high;
    frame[i].level1 = 0;
    frame[i].duration1 = bitTicks - high;
  }
  if (bidir) {
    // 雙向:只換訊框內容,由計時器送出(輸出反相由 RMT invert_out 做)
    portENTER_CRITICAL(&frameLock);
    memcpy(bidirFrame, frame, sizeof(bidirFrame));
    portEXIT_CRITICAL(&frameLock);
    dshotValue = value;
    return;
  }
  // 訊框之間的低電位分成兩半放進最後一個符號(每半最多 32767 格)
  const uint32_t gapTicks = DSHOT_FRAME_PERIOD_US * (DSHOT_RMT_RESOLUTION_HZ / 1000000UL) - 16UL * bitTicks;
  frame[16].level0 = 0;
  frame[16].duration0 = gapTicks / 2;
  frame[16].level1 = 0;
  frame[16].duration1 = gapTicks - gapTicks / 2;
  // 換值:停掉目前的迴圈再送新的. 正在送的那一框可能被截斷,電變會因 CRC 不符丟掉它,下一框就是新值.
  if (looping) {
    rmt_disable(txChannel);
    rmt_enable(txChannel);
  }
  rmt_transmit_config_t tc = {};
  tc.loop_count = -1;
  looping = rmt_transmit(txChannel, copyEncoder, frame, sizeof(frame), &tc) == ESP_OK;
  // 送框失敗就不記成已送出:下一拍會再送. r6 以前失敗也更新 dshotValue,油門不變時就永遠不再送,
  // 電變失訊停機(2026-09-14 安全審查 B3).
  if (looping) dshotValue = value;
}

static bool beginDshot(uint8_t proto, bool wantBidir) {
  const bool d150 = proto == ESC_PROTO_DSHOT150;
  bitTicks = d150 ? 133 : 67;
  oneHighTicks = d150 ? 100 : 50;
  zeroHighTicks = d150 ? 50 : 25;
  bidir = wantBidir && proto == ESC_PROTO_DSHOT300;   // 現行電變只有 DShot300 支援雙向(查證紀錄)
  rmt_tx_channel_config_t cfg = {};
  cfg.gpio_num = (gpio_num_t)PIN_ESC_SIGNAL;
  cfg.clk_src = RMT_CLK_SRC_DEFAULT;
  cfg.resolution_hz = DSHOT_RMT_RESOLUTION_HZ;
  cfg.mem_block_symbols = 48;   // C3 每通道 48 個符號,訊框 17 個放得下,迴圈才能完全在硬體裡跑
  cfg.trans_queue_depth = 4;
  cfg.flags.io_loop_back = 1;   // 自我檢查與雙向接收:輸出同時送回輸入端
  cfg.flags.invert_out = bidir ? 1 : 0;   // 雙向:線上反相,閒置高電位
  if (rmt_new_tx_channel(&cfg, &txChannel) != ESP_OK) return false;
  rmt_copy_encoder_config_t ec = {};
  if (rmt_new_copy_encoder(&ec, &copyEncoder) != ESP_OK) return false;
  if (bidir) {
    gpio_pullup_en((gpio_num_t)PIN_ESC_SIGNAL);   // 放開線時靠內部上拉維持高電位(Betaflight 也只用內部上拉)
    rmt_rx_channel_config_t rc = {};
    rc.gpio_num = (gpio_num_t)PIN_ESC_SIGNAL;
    rc.clk_src = RMT_CLK_SRC_DEFAULT;
    rc.resolution_hz = DSHOT_RMT_RESOLUTION_HZ;
    rc.mem_block_symbols = 48;
    if (rmt_new_rx_channel(&rc, &rxChannel) != ESP_OK) return false;
    rmt_rx_event_callbacks_t rcb = {};
    rcb.on_recv_done = onBidirRxDone;
    rmt_rx_register_event_callbacks(rxChannel, &rcb, nullptr);
    rmt_tx_event_callbacks_t tcb = {};
    tcb.on_trans_done = onBidirTxDone;
    rmt_tx_register_event_callbacks(txChannel, &tcb, nullptr);
    replyRxCfg.signal_range_min_ns = 800;      // 回傳最短一段 2.667µs,短於 0.8µs 當雜訊
    replyRxCfg.signal_range_max_ns = 15000;    // 最長一段 3 位元(8µs);高電位超過 15µs = 回傳結束
    if (rmt_enable(rxChannel) != ESP_OK) return false;
    // 中斷裡萬一重新接收失敗,IDF 會印錯誤訊息;每秒幾千次會塞爆序列埠,關掉 rmt 的訊息
    esp_log_level_set("rmt", ESP_LOG_NONE);
    if (rmt_receive(rxChannel, rxBuf, sizeof(rxBuf), &replyRxCfg) != ESP_OK) return false;
  }
  if (rmt_enable(txChannel) != ESP_OK) return false;
  writeDshot(DSHOT_STOP);
  escUs = ESC_US_SAFE_IDLE;
  if (bidir) {
    esp_timer_create_args_t ta = {};
    ta.callback = bidirTick;
    ta.name = "dshot";
    if (esp_timer_create(&ta, &bidirTimer) != ESP_OK) return false;
    esp_timer_start_periodic(bidirTimer, BIDIR_FRAME_PERIOD_US);
  }
  return true;
}

static bool outputOk = false;
bool escOutputOk() { return outputOk; }

bool escBegin(uint8_t proto, uint16_t initialUs, uint16_t hz, bool rpmTelemetry) {
  escPinLow();
  protocol = proto;
  pwmHz = (hz >= 50 && hz <= 400) ? hz : ESC_PWM_FREQ_HZ;
  if (proto == ESC_PROTO_DSHOT150 || proto == ESC_PROTO_DSHOT300) {
    outputOk = beginDshot(proto, rpmTelemetry);
    if (outputOk) return true;
    Serial.println(F("ERR ESC DShot RMT"));
    return false;   // 腳位維持低電位,不退回 PWM(電變會把 PWM 認成訊號種類)
  }
  protocol = ESC_PROTO_PWM50;
  // 核心 3.x:ledcAttach 自動配通道. 掛上當下 duty=0(持續低電位),下一行立刻給初始脈寬.
  if (!ledcAttach(PIN_ESC_SIGNAL, pwmHz, ESC_PWM_RESOLUTION_BITS)) {
    Serial.println(F("ERR ESC LEDC"));
    return false;
  }
  writePwmUs(initialUs);
  outputOk = true;
  return true;
}

void escWrite(uint16_t us, float pct, bool stop) {
  if (protocol == ESC_PROTO_PWM50) {
    writePwmUs(us);
    return;
  }
  if (stop || pct <= 0) {
    writeDshot(DSHOT_STOP);
  } else {
    if (pct > 100) pct = 100;
    writeDshot((uint16_t)lroundf(DSHOT_THROTTLE_MIN + (DSHOT_THROTTLE_MAX - DSHOT_THROTTLE_MIN) * pct / 100.0f));
  }
  escUs = us;
}

uint16_t escCurrentUs() { return escUs; }
uint16_t escCurrentDshot() { return protocol == ESC_PROTO_PWM50 ? 0xFFFF : dshotValue; }
uint8_t escActiveProtocol() { return protocol; }
uint16_t escActivePwmHz() { return pwmHz; }
bool escRpmActive() { return bidir; }
void escRpmGetStats(EscRpmStats &out) { out = rpm; }   // 各欄位是 32 位元整數,單一欄位讀寫不會讀到一半

// 把「週期 µs」編成電變回傳的 RMT 符號(TX 開 invert_out,符號電位 = 線上電位取反). 回傳符號數.
static size_t buildReplySymbols(uint32_t periodUs, rmt_symbol_word_t *syms, size_t maxSyms, uint16_t &v16Out, uint32_t &gcrOut) {
  static const uint8_t GCR_ENC[16] = {0x19, 0x1B, 0x12, 0x13, 0x1D, 0x15, 0x16, 0x17,
                                      0x1A, 0x09, 0x0A, 0x0B, 0x1E, 0x0D, 0x0E, 0x0F};
  uint16_t v12;
  if (periodUs == 0xFFFF) {
    v12 = 0x0FFF;   // 馬達停止
  } else {
    uint8_t e = 0;
    while ((periodUs >> e) > 0x1FF && e < 7) ++e;
    v12 = (uint16_t)((e << 9) | (periodUs >> e));
  }
  const uint16_t crc = ~(v12 ^ (v12 >> 4) ^ (v12 >> 8)) & 0x0F;
  const uint16_t v16 = (uint16_t)((v12 << 4) | crc);
  uint32_t gcr = 0;
  for (int k = 0; k < 4; ++k) gcr = (gcr << 5) | GCR_ENC[(v16 >> (12 - 4 * k)) & 0x0F];
  uint8_t level[21];
  level[0] = 0;
  for (int i = 0; i < 20; ++i) level[i + 1] = level[i] ^ ((gcr >> (19 - i)) & 1);
  memset(syms, 0, maxSyms * sizeof(rmt_symbol_word_t));
  size_t half = 0;
  auto put = [&](uint8_t lineLevel, uint32_t ticks) {
    if (half / 2 >= maxSyms) return;
    rmt_symbol_word_t &s = syms[half / 2];
    if (half % 2 == 0) { s.level0 = !lineLevel; s.duration0 = ticks; }
    else { s.level1 = !lineLevel; s.duration1 = ticks; }
    ++half;
  };
  int a = 0;
  while (a < 21) {
    int b = a;
    while (b < 21 && level[b] == level[a]) ++b;
    put(level[a], (uint32_t)((uint64_t)b * REPLY_BIT_NS / 50) - (uint32_t)((uint64_t)a * REPLY_BIT_NS / 50));
    a = b;
  }
  put(1, 600);                 // 結尾閒置高 30µs
  if (half % 2) put(1, 600);   // 湊滿整數個符號
  v16Out = v16;
  gcrOut = gcr;
  return half / 2;
}

// --- 模擬電變(測試用,需要 GPIO5 跳線接 GPIO4)---
// GG 2026-09-13 插了一條 GPIO5 ↔ GPIO4 的跳線給 Claude 測試(電變輸出仍是 GPIO4). 只有序列指令 escemu 會啟動,
// 平常開機不碰 GPIO5. GPIO5 的 RX 收控制器送的訊框(檢查反相 CRC),收完叫醒最高優先權工作,
// 由 GPIO5 的 TX(開汲極 + 反相,閒置放開線)送回指定週期的回傳. 回傳時間不是真電變的 30µs(工作切換延遲),
// 但控制器的接收只要求回傳在自己訊框收完之後,下一框之前,足夠驗證送框,放開線,接收,解碼整條路徑.
static const uint8_t EMU_PIN = 5;
static rmt_channel_handle_t emuRx = nullptr, emuTx = nullptr;
static rmt_encoder_handle_t emuEnc = nullptr;
static TaskHandle_t emuTask = nullptr;
static rmt_symbol_word_t emuRxBuf[48];
static rmt_symbol_word_t emuReply[12];
static size_t emuReplyCount = 0;
static rmt_receive_config_t emuRxCfg = {};
static volatile bool emuOn = false;
static EscEmuStats emu = {};

static bool IRAM_ATTR onEmuRxDone(rmt_channel_handle_t, const rmt_rx_done_event_data_t *ev, void *) {
  BaseType_t woke = pdFALSE;
  if (emuOn && ev->num_symbols >= 14 && ev->num_symbols <= 17) {   // 控制器的訊框(自己送的回傳 ≤ 12 符號,略過)
    ++emu.frames;
    uint16_t packet = 0;
    for (uint8_t i = 0; i < 16 && i < ev->num_symbols; ++i) {
      // 反相訊框:每位元先低後高,低電位長度決定 0/1(1 = 2.5µs,0 = 1.25µs,門檻 1.875µs = 37 格)
      const rmt_symbol_word_t &s = ev->received_symbols[i];
      const uint32_t low = s.level0 == 0 ? s.duration0 : s.duration1;
      packet = (uint16_t)((packet << 1) | (low > 37 ? 1 : 0));
    }
    const uint16_t data = packet >> 4;
    if ((~(data ^ (data >> 4) ^ (data >> 8)) & 0x0F) == (packet & 0x0F)) {
      ++emu.frameCrcOk;
      emu.lastValue = packet >> 5;
    }
    xTaskNotifyFromISR(emuTask, 1, eSetValueWithOverwrite, &woke);
  }
  rmt_receive(emuRx, emuRxBuf, sizeof(emuRxBuf), &emuRxCfg);
  return woke == pdTRUE;
}

static void emuTaskFn(void *) {
  for (;;) {
    xTaskNotifyWait(0, 0, nullptr, portMAX_DELAY);
    if (!emuOn) continue;
    rmt_transmit_config_t tc = {};
    if (rmt_transmit(emuTx, emuEnc, emuReply, emuReplyCount * sizeof(rmt_symbol_word_t), &tc) == ESP_OK) ++emu.replies;
  }
}

const char *escEmuStart(uint32_t periodUs) {
  if (!bidir) return "rpm telemetry not active";
  uint16_t v16;
  uint32_t gcr;
  emuReplyCount = buildReplySymbols(periodUs, emuReply, 12, v16, gcr);
  emu.periodUs = periodUs;
  if (emuOn) return nullptr;   // 已在執行:只換回傳的週期
  if (!emuTx) {
    gpio_pullup_en((gpio_num_t)EMU_PIN);
    rmt_tx_channel_config_t tcfg = {};
    tcfg.gpio_num = (gpio_num_t)EMU_PIN;
    tcfg.clk_src = RMT_CLK_SRC_DEFAULT;
    tcfg.resolution_hz = DSHOT_RMT_RESOLUTION_HZ;
    tcfg.mem_block_symbols = 48;
    tcfg.trans_queue_depth = 4;
    tcfg.flags.invert_out = 1;   // 閒置 = 高 = 開汲極放開
    tcfg.flags.io_od_mode = 1;
    if (rmt_new_tx_channel(&tcfg, &emuTx) != ESP_OK) return "emu tx fail";
    rmt_copy_encoder_config_t ec = {};
    if (rmt_new_copy_encoder(&ec, &emuEnc) != ESP_OK) return "emu enc fail";
    rmt_rx_channel_config_t rcfg = {};
    rcfg.gpio_num = (gpio_num_t)EMU_PIN;
    rcfg.clk_src = RMT_CLK_SRC_DEFAULT;
    rcfg.resolution_hz = DSHOT_RMT_RESOLUTION_HZ;
    rcfg.mem_block_symbols = 48;
    if (rmt_new_rx_channel(&rcfg, &emuRx) != ESP_OK) return "emu rx fail";
    rmt_rx_event_callbacks_t cb = {};
    cb.on_recv_done = onEmuRxDone;
    rmt_rx_register_event_callbacks(emuRx, &cb, nullptr);
    emuRxCfg.signal_range_min_ns = 300;
    emuRxCfg.signal_range_max_ns = 10000;   // 訊框內最長一段約 2.5µs;高電位超過 10µs = 訊框結束
    xTaskCreate(emuTaskFn, "escemu", 3072, nullptr, configMAX_PRIORITIES - 1, &emuTask);
    rmt_enable(emuTx);
    rmt_enable(emuRx);
  }
  emuOn = true;
  if (rmt_receive(emuRx, emuRxBuf, sizeof(emuRxBuf), &emuRxCfg) != ESP_OK) return "emu receive fail";
  return nullptr;
}

void escEmuStop() { emuOn = false; }
void escEmuGetStats(EscEmuStats &out) { out = emu; }

// --- 雙向回傳解碼自我測試 ---
// 沒有電變也能驗證解碼器與接收設定:暫停送訊框,用同一個 TX 送出一段「電變回傳」波形(指定週期編碼成 GCR),
// 同腳位的 RX 收下來走正式的解碼流程,比對解出的週期. 不驗證電變端的時序(要接真電變).
bool escRpmSelfTest(uint32_t periodUs, char *out, size_t outSize) {
  if (!bidir) {
    snprintf(out, outSize, "rpm telemetry not active (needs DShot300 + escRpm=1, reboot)");
    return false;
  }
  uint8_t e = 0;
  while ((periodUs >> e) > 0x1FF && e < 7) ++e;
  const uint16_t m = (uint16_t)(periodUs >> e);
  rmt_symbol_word_t syms[12];
  uint16_t v16;
  uint32_t gcr;
  const size_t count = buildReplySymbols(periodUs, syms, 12, v16, gcr);
  const size_t half = count * 2;

  bidirPaused = true;
  delay(3);   // 等最後一框與它的接收結束(接收通道一直開著)
  const uint32_t okBefore = rpm.ok, badBefore = rpm.bad;
  gpio_ll_od_disable(GPIO_LL_GET_HW(GPIO_PORT_0), PIN_ESC_SIGNAL);
  rmt_transmit_config_t tc = {};
  const bool sent = rmt_transmit(txChannel, copyEncoder, syms, (half / 2) * sizeof(rmt_symbol_word_t), &tc) == ESP_OK;
  delay(20);
  const bool ok = sent && rpm.ok == okBefore + 1 && rpm.periodUs == ((uint32_t)m << e);
  snprintf(out, outSize, "period=%luus encoded=0x%04X gcr=0x%05lX symbols=%u decoded=%luus ok+%lu bad+%lu",
           (unsigned long)periodUs, v16, (unsigned long)gcr, (unsigned)(half / 2), (unsigned long)rpm.periodUs,
           (unsigned long)(rpm.ok - okBefore), (unsigned long)(rpm.bad - badBefore));
  bidirPaused = false;
  return ok;
}

// --- DShot 回授自我檢查 ---
static volatile size_t rxCount = 0;
static volatile bool rxDone = false;

static bool IRAM_ATTR onRxDone(rmt_channel_handle_t, const rmt_rx_done_event_data_t *ev, void *) {
  rxCount = ev->num_symbols;
  rxDone = true;
  return false;
}

bool escDshotSelfTest(char *out, size_t outSize) {
  if (protocol == ESC_PROTO_PWM50 || !txChannel) {
    snprintf(out, outSize, "not DShot");
    return false;
  }
  if (bidir) {   // 雙向模式的接收通道正在用,改用 rpmtest
    snprintf(out, outSize, "rpm telemetry active, use 'rpmtest'");
    return false;
  }
  rmt_channel_handle_t rx = nullptr;
  rmt_rx_channel_config_t rc = {};
  rc.gpio_num = (gpio_num_t)PIN_ESC_SIGNAL;
  rc.clk_src = RMT_CLK_SRC_DEFAULT;
  rc.resolution_hz = DSHOT_RMT_RESOLUTION_HZ;
  rc.mem_block_symbols = 48;
  if (rmt_new_rx_channel(&rc, &rx) != ESP_OK) {
    snprintf(out, outSize, "rx channel fail");
    return false;
  }
  rmt_rx_event_callbacks_t cbs = {};
  cbs.on_recv_done = onRxDone;
  rmt_rx_register_event_callbacks(rx, &cbs, nullptr);
  rmt_enable(rx);
  rmt_symbol_word_t sym[48];
  rmt_receive_config_t rcv = {};
  rcv.signal_range_min_ns = 200;                         // 比最短的高電位(DShot300 的 0:1250ns)短很多的當雜訊
  rcv.signal_range_max_ns = 12UL * bitTicks * 50UL;      // 低電位超過 12 個位元長 = 訊框之間的空檔(DShot150 空檔 143µs),收完一框
  bool ok = false;
  int attempts = 0;
  out[0] = 0;
  for (; attempts < 20 && !ok; ++attempts) {
    rxDone = false;
    if (rmt_receive(rx, sym, sizeof(sym), &rcv) != ESP_OK) break;
    const uint32_t t0 = millis();
    while (!rxDone && millis() - t0 < 50) delay(1);
    if (!rxDone) continue;
    // 從空檔中間開始收的話前面會有半框,只接受剛好 16 個符號的完整訊框
    if (rxCount != 16) continue;
    uint16_t packet = 0;
    uint32_t hiOne = 0, hiZero = 0, nOne = 0, nZero = 0;
    for (uint8_t i = 0; i < 16; ++i) {
      const bool one = sym[i].duration0 > bitTicks / 2;
      packet = (uint16_t)((packet << 1) | (one ? 1 : 0));
      if (one) { hiOne += sym[i].duration0; ++nOne; }
      else { hiZero += sym[i].duration0; ++nZero; }
    }
    const uint16_t value = packet >> 5;
    const uint16_t data = packet >> 4;
    const bool crcOk = ((data ^ (data >> 4) ^ (data >> 8)) & 0x0F) == (packet & 0x0F);
    ok = crcOk && value == dshotValue;
    snprintf(out, outSize, "frame=0x%04X value=%u expect=%u crc=%s high1=%.2fus high0=%.2fus bit=%.2fus tries=%d",
             packet, value, dshotValue, crcOk ? "ok" : "BAD", nOne ? hiOne * 0.05f / nOne : 0,
             nZero ? hiZero * 0.05f / nZero : 0, bitTicks * 0.05f, attempts + 1);
  }
  rmt_disable(rx);
  rmt_del_channel(rx);
  if (!out[0]) snprintf(out, outSize, "no complete frame received (%d tries)", attempts);
  return ok;
}
