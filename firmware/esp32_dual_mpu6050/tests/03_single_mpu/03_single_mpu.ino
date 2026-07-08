// ============================================================
// Test 03: Single MPU6050
// ============================================================
// Purpose: Read one MPU6050 at address 0x68.
// Expected: acceleration ~9.8 m/s², gyro near 0 when stationary.
// ============================================================

#include <Wire.h>

#define SDA_PIN 21
#define SCL_PIN 22
#define MPU_ADDR 0x68

int16_t ax, ay, az, gx, gy, gz;

bool initMPU() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0x00);  // Clear sleep bit
  byte error = Wire.endTransmission(true);
  return error == 0;
}

void readMPU() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // ACCEL_XOUT_H register
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU_ADDR, (uint8_t)14, (uint8_t)true);

  ax = Wire.read() << 8 | Wire.read();
  ay = Wire.read() << 8 | Wire.read();
  az = Wire.read() << 8 | Wire.read();
  Wire.read(); Wire.read();  // temperature - skip
  gx = Wire.read() << 8 | Wire.read();
  gy = Wire.read() << 8 | Wire.read();
  gz = Wire.read() << 8 | Wire.read();
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  Single MPU6050 Test - 0x68");
  Serial.println("========================================");

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!initMPU()) {
    Serial.println("[FAIL] MPU6050 not found at 0x68!");
    Serial.println("Check: power, SDA/SCL, AD0=LOW");
    while (1) { delay(1000); }
  }
  Serial.println("[OK] MPU6050 initialized at 0x68");
  Serial.println("Stationary: accel ~9.8 m/s2, gyro ~0 deg/s");
  Serial.println("----------------------------------------");
}

void loop() {
  readMPU();

  float ax_m = ax / 16384.0 * 9.81;
  float ay_m = ay / 16384.0 * 9.81;
  float az_m = az / 16384.0 * 9.81;

  Serial.printf("AX=%+.2f  AY=%+.2f  AZ=%+.2f m/s2\n", ax_m, ay_m, az_m);
  Serial.printf("GX=%+6d  GY=%+6d  GZ=%+6d raw\n", gx, gy, gz);
  Serial.println();

  delay(200);
}
