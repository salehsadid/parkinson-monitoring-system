// ============================================================
// Test 02: I2C Scanner
// ============================================================
// Purpose: Detect all I2C devices on the bus.
// Expected with both MPU6050: 0x68 and 0x69
// ============================================================

#include <Wire.h>

#define SDA_PIN 21
#define SCL_PIN 22

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  I2C Scanner - Stage 1.1");
  Serial.println("========================================");

  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.printf("[OK] I2C initialized: SDA=%d, SCL=%d\n", SDA_PIN, SCL_PIN);
  Serial.println("Scanning...");
  Serial.println("----------------------------------------");
}

void loop() {
  int deviceCount = 0;

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    byte error = Wire.endTransmission();

    if (error == 0) {
      Serial.printf("  Found device at 0x%02X", addr);
      if (addr == 0x68) {
        Serial.print(" <- MPU6050 (AD0=LOW, hand)");
      } else if (addr == 0x69) {
        Serial.print(" <- MPU6050 (AD0=HIGH, shoe)");
      }
      Serial.println();
      deviceCount++;
    }
  }

  Serial.println("----------------------------------------");
  if (deviceCount == 0) {
    Serial.println("  NO devices found!");
    Serial.println("  Check: SDA/SCL wiring, power, common GND");
  } else if (deviceCount == 1) {
    Serial.println("  WARNING: Only 1 device found.");
    Serial.println("  If expecting 2x MPU6050, check AD0 wiring.");
  } else {
    Serial.printf("  %d devices found.\n", deviceCount);
  }
  Serial.println("========================================");
  delay(3000);
}
