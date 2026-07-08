// ============================================================
// Test 04: Dual MPU6050 Serial
// ============================================================
// Purpose: Read both MPU6050 sensors simultaneously.
// Expected: 0x68 = hand, 0x69 = shoe
// ============================================================

#include <Wire.h>

#define SDA_PIN 21
#define SCL_PIN 22
#define HAND_ADDR 0x68
#define SHOE_ADDR 0x69

int16_t hand_ax, hand_ay, hand_az, hand_gx, hand_gy, hand_gz;
int16_t shoe_ax, shoe_ay, shoe_az, shoe_gx, shoe_gy, shoe_gz;

bool initMPU(uint8_t addr) {
  Wire.beginTransmission(addr);
  Wire.write(0x6B);
  Wire.write(0x00);
  byte error = Wire.endTransmission(true);
  return error == 0;
}

void readMPU(uint8_t addr, int16_t &ax, int16_t &ay, int16_t &az,
             int16_t &gx, int16_t &gy, int16_t &gz) {
  Wire.beginTransmission(addr);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)addr, (uint8_t)14, (uint8_t)true);

  ax = Wire.read() << 8 | Wire.read();
  ay = Wire.read() << 8 | Wire.read();
  az = Wire.read() << 8 | Wire.read();
  Wire.read(); Wire.read();  // temperature
  gx = Wire.read() << 8 | Wire.read();
  gy = Wire.read() << 8 | Wire.read();
  gz = Wire.read() << 8 | Wire.read();
}

void printIMU(const char* label, int16_t ax, int16_t ay, int16_t az,
              int16_t gx, int16_t gy, int16_t gz) {
  float ax_m = ax / 16384.0 * 9.81;
  float ay_m = ay / 16384.0 * 9.81;
  float az_m = az / 16384.0 * 9.81;

  Serial.printf("%s:\n", label);
  Serial.printf("  AX=%+.2f  AY=%+.2f  AZ=%+.2f m/s2\n", ax_m, ay_m, az_m);
  Serial.printf("  GX=%+6d  GY=%+6d  GZ=%+6d raw\n", gx, gy, gz);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  Dual MPU6050 Serial Test");
  Serial.println("========================================");

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!initMPU(HAND_ADDR)) {
    Serial.println("[FAIL] Hand MPU6050 (0x68) not found!");
    while (1) { delay(1000); }
  }
  Serial.println("[OK] Hand MPU6050 (0x68) ready");

  if (!initMPU(SHOE_ADDR)) {
    Serial.println("[FAIL] Shoe MPU6050 (0x69) not found!");
    while (1) { delay(1000); }
  }
  Serial.println("[OK] Shoe MPU6050 (0x69) ready");

  Serial.println("========================================");
  Serial.println("BOTH SENSORS ACTIVE - Move them to see changes");
  Serial.println("========================================");
}

void loop() {
  readMPU(HAND_ADDR, hand_ax, hand_ay, hand_az, hand_gx, hand_gy, hand_gz);
  readMPU(SHOE_ADDR, shoe_ax, shoe_ay, shoe_az, shoe_gx, shoe_gy, shoe_gz);

  Serial.println("---");
  printIMU("HAND", hand_ax, hand_ay, hand_az, hand_gx, hand_gy, hand_gz);
  printIMU("SHOE", shoe_ax, shoe_ay, shoe_az, shoe_gx, shoe_gy, shoe_gz);
  Serial.println();

  delay(200);
}
