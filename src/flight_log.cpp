// 版本流水號: r6 (2026-10-30) 只記起飛程序:狀態 3~6(倒數~降落)才收,離開後再記 5 秒;每趟第一筆旗標 0x10;待機不碰快閃
// 舊: r5 (2026-10-30) 改存快閃 spiffs 分割區(環形,序號標頭,mmap 讀取,倒數預擦,loop 寫頁);RAM 佇列取代 66KB 環形緩衝
// 舊: r4 (2026-10-29) 每筆加翼軸仰角與方位角(區間最後的值)
// 舊: r3 (2026-10-29) 每筆加線軸 G(區間最後的低通值)
// 舊: r2 (2026-09-13) 修正每筆實際 105ms(區間起點改走固定 100ms 格點)
// 舊: r1 (2026-09-13) 初版:0.1 秒一筆的環形紀錄(角度,油門,G 力,Z 抖動,短尖峰,手勢推力,狀態)
#include "flight_log.h"
#include <esp_partition.h>

// --- 快閃版面 ---
static const uint32_t SECTOR = 4096;
static const uint16_t MAGIC = 0x474C;   // "LG"
struct __attribute__((packed)) SectorHeader {
  uint16_t magic;
  uint32_t seq;        // 從 1 起遞增,0 不用
  uint8_t sampleSize;  // sizeof(FlightLogSample),格式變了舊區塊就當無效
  uint8_t reserved;
};
static const uint16_t SAMPLES_PER_SECTOR = (SECTOR - sizeof(SectorHeader)) / sizeof(FlightLogSample);   // 371
static const uint32_t PREPARE_MARGIN_SAMPLES = 600;   // 預擦多留 1 分鐘

static const esp_partition_t *part = nullptr;
static const uint8_t *mapped = nullptr;   // mmap 後的唯讀視窗
static uint16_t sectorCount = 0;
static uint16_t headSector = 0;           // 正在寫的區塊
static uint32_t headSeq = 0;              // 它的序號(0 = 還沒開始寫)
static uint16_t headSlot = 0;             // 區塊內下一筆位置
static uint32_t oldestSeq = 0;            // 保留範圍內最舊的序號
static volatile uint32_t flashedTotal = 0;   // 已寫進快閃的全域筆數 = headSeq*371 + headSlot(headSeq 從 1 起,減 1 個區塊)
static uint32_t inflightErases = 0;

// --- 控制工作 → loop 的佇列(單一生產者,單一消費者) ---
static const uint16_t QUEUE_CAP = 256;    // 25 秒;loop 被 WiFi 卡住超過這麼久才會丟
static FlightLogSample queueBuf[QUEUE_CAP];
static volatile uint16_t qHead = 0, qTail = 0;
static volatile uint32_t dropped = 0;
static volatile uint32_t prepareRequest = 0;   // 要先擦好的筆數(0 = 沒有請求)

// 記錄的開關(控制工作):起飛程序中(狀態 3~6)記,離開後再記 REC_TAIL_MS 收尾(觸地滾行,降落後的衝擊),其他時候不收也不寫快閃
static const uint32_t REC_TAIL_MS = 5000;
static bool recording = false;
static bool recStartPending = false;   // 下一筆是這趟的第一筆
static uint32_t lastActiveMs = 0;      // 最後一次處於狀態 3~6 的時間

// 目前區間的累積(控制工作)
static bool slotOpen = false;
static uint32_t slotStartMs = 0;
static FlightLogSample slot;
static float slotAcc = 0, slotVib = 0, slotSpike = 0, slotPush = -100;

static uint8_t clampU8(float v) { return v <= 0 ? 0 : (v >= 255 ? 255 : (uint8_t)lroundf(v)); }
static int8_t clampI8(float v) { return v <= -127 ? -127 : (v >= 127 ? 127 : (int8_t)lroundf(v)); }

static inline uint32_t globalIndex(uint32_t seq, uint16_t s) { return (seq - 1) * SAMPLES_PER_SECTOR + s; }

static const SectorHeader *headerOf(uint16_t sec) { return (const SectorHeader *)(mapped + (uint32_t)sec * SECTOR); }
static bool sectorValid(uint16_t sec) {
  const SectorHeader *h = headerOf(sec);
  return h->magic == MAGIC && h->seq != 0 && h->seq != 0xFFFFFFFFu && h->sampleSize == sizeof(FlightLogSample);
}
static bool sectorErased(uint16_t sec) {
  const uint32_t *p = (const uint32_t *)(mapped + (uint32_t)sec * SECTOR);
  for (uint32_t i = 0; i < SECTOR / 4; ++i)
    if (p[i] != 0xFFFFFFFFu) return false;
  return true;
}
static bool sampleErased(const FlightLogSample *s) {
  const uint8_t *b = (const uint8_t *)s;
  for (size_t i = 0; i < sizeof(FlightLogSample); ++i)
    if (b[i] != 0xFF) return false;
  return true;
}

static void recomputeOldest() {
  oldestSeq = 0;
  for (uint16_t i = 0; i < sectorCount; ++i)
    if (sectorValid(i) && (oldestSeq == 0 || headerOf(i)->seq < oldestSeq)) oldestSeq = headerOf(i)->seq;
}

void flightLogBegin() {
  part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_SPIFFS, nullptr);
  if (!part) {
    Serial.println(F("flight log: no spiffs partition, log disabled"));
    return;
  }
  esp_partition_mmap_handle_t h;
  const void *ptr = nullptr;
  if (esp_partition_mmap(part, 0, part->size, ESP_PARTITION_MMAP_DATA, &ptr, &h) != ESP_OK) {
    Serial.println(F("flight log: mmap failed, log disabled"));
    part = nullptr;
    return;
  }
  mapped = (const uint8_t *)ptr;
  sectorCount = part->size / SECTOR;
  // 找序號最大的區塊接著寫;沒有任何有效區塊就從 0 號開始(第一次寫會擦)
  uint32_t best = 0;
  for (uint16_t i = 0; i < sectorCount; ++i)
    if (sectorValid(i) && headerOf(i)->seq > best) { best = headerOf(i)->seq; headSector = i; }
  if (best) {
    headSeq = best;
    const FlightLogSample *s = (const FlightLogSample *)(mapped + (uint32_t)headSector * SECTOR + sizeof(SectorHeader));
    headSlot = 0;
    while (headSlot < SAMPLES_PER_SECTOR && !sampleErased(&s[headSlot])) ++headSlot;
  } else {
    headSector = 0;
    headSeq = 0;
    headSlot = SAMPLES_PER_SECTOR;   // 第一筆就會開新區塊
  }
  recomputeOldest();
  flashedTotal = headSeq ? globalIndex(headSeq, headSlot) : 0;
  Serial.printf("flight log: flash %u sectors (%u samples, %.1f min), resume seq %lu slot %u, oldest seq %lu\n",
                (unsigned)sectorCount, (unsigned)(sectorCount * SAMPLES_PER_SECTOR), sectorCount * SAMPLES_PER_SECTOR * 0.1f / 60,
                (unsigned long)headSeq, (unsigned)headSlot, (unsigned long)oldestSeq);
}

// 開下一個區塊:沒擦的就地擦(飛行中會停 30~50ms,計數讓人看得到),寫標頭.
static bool openNextSector(bool inFlight) {
  const uint16_t next = headSeq ? (uint16_t)((headSector + 1) % sectorCount) : 0;
  if (!sectorErased(next)) {
    if (esp_partition_erase_range(part, (uint32_t)next * SECTOR, SECTOR) != ESP_OK) return false;
    if (inFlight) {
      ++inflightErases;
      Serial.println(F("flight log: erased a sector in flight (flight longer than prepared)"));
    }
  }
  const SectorHeader hdr = {MAGIC, headSeq + 1, (uint8_t)sizeof(FlightLogSample), 0xFF};
  if (esp_partition_write(part, (uint32_t)next * SECTOR, &hdr, sizeof(hdr)) != ESP_OK) return false;
  headSector = next;
  headSeq = hdr.seq;
  headSlot = 0;
  recomputeOldest();   // 剛擦掉的可能是最舊的
  return true;
}

void flightLogRequestPrepare(uint32_t samples) { prepareRequest = samples + PREPARE_MARGIN_SAMPLES; }

// 預擦:從目前區塊之後開始,擦到能放下 samples 筆為止(已經是空的區塊跳過). 在地上做,停機沒關係.
static void prepare(uint32_t samples) {
  if (!part) return;
  uint32_t room = headSeq ? (uint32_t)(SAMPLES_PER_SECTOR - headSlot) : 0;
  uint16_t sec = headSeq ? headSector : (uint16_t)(sectorCount - 1);   // 還沒開始寫時,下一個區塊是 0 號
  uint16_t erased = 0, visited = 0;
  while (room < samples && visited < sectorCount - 1) {   // 最多擦到剩目前區塊,不把自己擦掉
    sec = (uint16_t)((sec + 1) % sectorCount);
    ++visited;
    if (!sectorErased(sec)) {
      if (esp_partition_erase_range(part, (uint32_t)sec * SECTOR, SECTOR) != ESP_OK) break;
      ++erased;
    }
    room += SAMPLES_PER_SECTOR;
  }
  recomputeOldest();
  Serial.printf("flight log: prepared %lu samples, erased %u sectors\n", (unsigned long)samples, (unsigned)erased);
}

void flightLogService(uint32_t nowMs) {
  if (!part) {   // 沒有快閃:佇列只是丟掉
    qTail = qHead;
    return;
  }
  if (prepareRequest) {
    const uint32_t n = prepareRequest;
    prepareRequest = 0;
    prepare(n);
  }
  static uint32_t lastFlushMs = 0;
  const uint16_t pending = (uint16_t)((qHead - qTail + QUEUE_CAP) % QUEUE_CAP);
  if (!pending || (nowMs - lastFlushMs < 1000 && pending < 23)) return;   // 每秒或湊滿約一頁(23 筆 = 253 位元組)才寫
  lastFlushMs = nowMs;
  // 佇列裡最新一筆的狀態決定「飛行中」(就地擦除計數用)
  const bool inFlight = queueBuf[(qHead + QUEUE_CAP - 1) % QUEUE_CAP].state >= 4 && queueBuf[(qHead + QUEUE_CAP - 1) % QUEUE_CAP].state <= 6;
  while (qTail != qHead) {
    if (headSlot >= SAMPLES_PER_SECTOR || headSeq == 0) {
      if (!openNextSector(inFlight)) return;   // 快閃失敗:這批留在佇列下次再試
    }
    // 連續的幾筆一次寫(同一區塊內),減少寫入次數
    uint16_t n = 0;
    FlightLogSample buf[32];
    while (qTail != qHead && n < 32 && headSlot + n < SAMPLES_PER_SECTOR) {
      buf[n++] = queueBuf[qTail];
      qTail = (uint16_t)((qTail + 1) % QUEUE_CAP);
    }
    const uint32_t off = (uint32_t)headSector * SECTOR + sizeof(SectorHeader) + (uint32_t)headSlot * sizeof(FlightLogSample);
    if (esp_partition_write(part, off, buf, n * sizeof(FlightLogSample)) != ESP_OK) return;
    headSlot += n;
    flashedTotal = globalIndex(headSeq, headSlot);
  }
}

void flightLogFeed(float pitchDeg, float throttlePct, float accMagG, float vibG, float spikeG, float pushG,
                   float lineG, float sideDeg, float azimuthDeg, uint8_t state, uint8_t flags, uint32_t nowMs) {
  // 只記起飛程序:狀態 3(倒數)~6(降落). 回到待機/結束後再記 5 秒收尾就停,下次進倒數再開新的一趟
  const bool active = state >= 3 && state <= 6;
  if (active) lastActiveMs = nowMs | 1;
  if (!recording) {
    if (!active) return;
    recording = true;
    recStartPending = true;
    slotOpen = false;   // 重新對齊區間起點
  } else if (!active && (!lastActiveMs || nowMs - lastActiveMs > REC_TAIL_MS)) {
    recording = false;
    slotOpen = false;   // 沒收成的半筆丟掉
    return;
  }
  if (!slotOpen) {
    slotOpen = true;
    // 區間起點走固定 100ms 格點. r1 用「這一拍」當起點:收尾那一拍算進上一區,下一區從再下一拍才開,
    // 每筆實際 105ms,時間軸慢 5%(全功能測試段 4:33 秒飛行只有 314 筆). 落後超過一格(例如剛開機)才重新對齊.
    slotStartMs = (slotStartMs && nowMs - slotStartMs < 2 * FLIGHT_LOG_SAMPLE_MS) ? slotStartMs + FLIGHT_LOG_SAMPLE_MS : nowMs;
    slotAcc = slotVib = slotSpike = 0;
    slotPush = -100;
    slot.flags = 0;
  }
  if (accMagG > slotAcc) slotAcc = accMagG;
  if (vibG > slotVib) slotVib = vibG;
  if (spikeG > slotSpike) slotSpike = spikeG;
  if (pushG > slotPush) slotPush = pushG;
  slot.flags |= flags;   // 區間內出現過就記
  if (recStartPending) slot.flags |= LOG_FLAG_REC_START;
  // 角度,油門,狀態取區間最後一個值
  slot.pitchDeg = clampI8(pitchDeg);
  slot.throttlePct = clampU8(throttlePct);
  slot.lineDg = clampU8(lineG * 10);
  slot.sideDeg = clampU8(sideDeg);
  slot.azim = (uint8_t)lroundf(fmodf(azimuthDeg + 360.0f, 360.0f) * 256.0f / 360.0f) & 0xFF;
  slot.state = state;

  if (nowMs - slotStartMs < FLIGHT_LOG_SAMPLE_MS) return;
  slot.accMaxDg = clampU8(slotAcc * 10);
  slot.vibCg2 = clampU8(slotVib * 50);
  slot.spikeDg = clampU8(slotSpike * 10);
  slot.pushDg = clampI8(slotPush * 10);
  if (slot.throttlePct == 0xFF) slot.throttlePct = 0xFE;   // 全 0xFF 代表「還沒寫」,油門本來就不會到 255
  const uint16_t next = (uint16_t)((qHead + 1) % QUEUE_CAP);
  if (next == qTail) {   // 佇列滿:丟最舊的,計數
    qTail = (uint16_t)((qTail + 1) % QUEUE_CAP);
    ++dropped;
  }
  queueBuf[qHead] = slot;   // 先寫資料
  qHead = next;             // 再推進
  slotOpen = false;
  recStartPending = false;
}

uint32_t flightLogTotal() { return flashedTotal; }

uint32_t flightLogOldest() { return oldestSeq ? globalIndex(oldestSeq, 0) : flashedTotal; }

bool flightLogGet(uint32_t index, FlightLogSample &out) {
  if (!part || !headSeq || index >= flashedTotal || index < flightLogOldest()) return false;
  const uint32_t seq = index / SAMPLES_PER_SECTOR + 1, s = index % SAMPLES_PER_SECTOR;
  // 序號 → 區塊:從目前區塊往回數(序號連續,中間不會跳號)
  const uint32_t back = headSeq - seq;
  if (back >= sectorCount) return false;
  const uint16_t sec = (uint16_t)((headSector + sectorCount - back) % sectorCount);
  if (!sectorValid(sec) || headerOf(sec)->seq != seq) return false;
  memcpy(&out, mapped + (uint32_t)sec * SECTOR + sizeof(SectorHeader) + s * sizeof(FlightLogSample), sizeof(out));
  return !sampleErased(&out);
}

void flightLogStats(bool &flashOk, uint16_t &sectors, uint32_t &seq, uint32_t &droppedOut, uint32_t &erases) {
  flashOk = part != nullptr;
  sectors = sectorCount;
  seq = headSeq;
  droppedOut = dropped;
  erases = inflightErases;
}
