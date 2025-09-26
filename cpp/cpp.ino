#include <SPI.h>

// ==== Register Addresses ====
#define REG_DEVID       0x00
#define REG_POWER_CTL   0x2D
#define REG_DATA_FORMAT 0x31
#define REG_DATAX0      0x32

// ==== Constants ====
#define DEVID_EXPECTED  0xE5
#define SCALE           (9.80665 / 256.0) // m/s^2 per LSB

// ==== Pin Setup ====
const int CS_PIN = 9;
const int SCK_PIN = 10;
const int MOSI_PIN = 11;
const int MISO_PIN = 12;

unsigned long lastRead = 0;
const unsigned int interval = 10; // ms (100Hz)

// ==== SPI Helper Functions ====
void regWrite(uint8_t reg, uint8_t val) {
  digitalWrite(CS_PIN, LOW);
  SPI1.transfer(reg & 0x3F);
  SPI1.transfer(val);
  digitalWrite(CS_PIN, HIGH);
}

uint8_t regRead(uint8_t reg) {
  digitalWrite(CS_PIN, LOW);
  SPI1.transfer(0x80 | (reg & 0x3F));
  uint8_t val = SPI1.transfer(0x00);
  digitalWrite(CS_PIN, HIGH);
  return val;
}

void regReadMulti(uint8_t reg, uint8_t* buf, uint8_t len) {
  digitalWrite(CS_PIN, LOW);
  SPI1.transfer(0xC0 | (reg & 0x3F)); // multi-byte read
  for (uint8_t i = 0; i < len; i++) {
    buf[i] = SPI1.transfer(0x00);
  }
  digitalWrite(CS_PIN, HIGH);
}

// ==== Setup ====
void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);

  // Initialize SPI1 with explicit pins
  SPI1.setSCK(SCK_PIN);
  SPI1.setTX(MOSI_PIN);
  SPI1.setRX(MISO_PIN);
  SPI1.begin();
  SPI1.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE3));

  // Check device ID
  if (regRead(REG_DEVID) != DEVID_EXPECTED) {
    Serial.println("ADXL343 not detected.");
    while (1);
  }

  regWrite(REG_DATA_FORMAT, 0x0A); // ±8g, full resolution
  regWrite(REG_POWER_CTL, regRead(REG_POWER_CTL) | 0x08); // Set measure bit
  delay(100);
}

// ==== Loop: Read every 10ms ====
void loop() {
  unsigned long now = millis();
  if (now - lastRead >= interval) {
    lastRead = now;

    uint8_t raw[6];
    regReadMulti(REG_DATAX0, raw, 6);
    int16_t x = (int16_t)(raw[1] << 8 | raw[0]);
    int16_t y = (int16_t)(raw[3] << 8 | raw[2]);
    int16_t z = (int16_t)(raw[5] << 8 | raw[4]);

    float ax = x * SCALE;
    float ay = y * SCALE;
    float az = z * SCALE;

    Serial.printf("|%lu, %.6f, %.6f, %.6f\n", now, ax, ay, az);
  }
}
