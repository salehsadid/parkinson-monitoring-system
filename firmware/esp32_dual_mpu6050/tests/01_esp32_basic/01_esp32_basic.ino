// ============================================================
// Test 01: ESP32 Basic Test
// ============================================================
// Purpose: Verify ESP32 uploads and Serial Monitor works.
// No sensors, no Wi-Fi, no peripherals.
// ============================================================

#define LED_BUILTIN 2  // Most ESP32 boards use GPIO2 for LED

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  ESP32 Basic Test - Stage 1.1");
  Serial.println("========================================");
  Serial.println("[OK] Serial Monitor connected");
  Serial.printf("[OK] Board: %s\n", ESP.getChipModel());
  Serial.printf("[OK] CPU freq: %d MHz\n", ESP.getCpuFreqMHz());
  Serial.printf("[OK] Free heap: %d bytes\n", ESP.getFreeHeap());

  pinMode(LED_BUILTIN, OUTPUT);
  Serial.println("[OK] LED pin configured");
  Serial.println("========================================");
  Serial.println("PASS: ESP32 is working");
  Serial.println("========================================");
}

void loop() {
  static unsigned long lastPrint = 0;
  static int heartbeat = 0;

  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();
    heartbeat++;
    Serial.printf("Heartbeat: %d\n", heartbeat);

    // Blink LED if available
    digitalWrite(LED_BUILTIN, heartbeat % 2 == 0 ? HIGH : LOW);
  }
}
