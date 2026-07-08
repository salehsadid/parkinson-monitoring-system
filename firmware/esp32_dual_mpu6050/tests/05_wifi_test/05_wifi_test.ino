// ============================================================
// Test 05: Wi-Fi Connection Test
// ============================================================
// Purpose: Connect ESP32 to Wi-Fi, print local IP.
// No sensors, no WebSocket complexity.
// ============================================================

#include <WiFi.h>

// ============================================
// CONFIGURE THESE FOR YOUR NETWORK
// ============================================
const char* WIFI_SSID     = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
// ============================================

#define LED_BUILTIN 2

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  Wi-Fi Test - Stage 1.1");
  Serial.println("========================================");
  Serial.printf("Connecting to: %s\n", WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  pinMode(LED_BUILTIN, OUTPUT);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
    digitalWrite(LED_BUILTIN, attempts % 2 == 0 ? HIGH : LOW);
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("[OK] Wi-Fi connected!");
    Serial.printf("[OK] ESP32 IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("[OK] Signal: %d dBm\n", WiFi.RSSI());
    Serial.println("========================================");
    Serial.println("PASS: Wi-Fi working");
    Serial.println("========================================");
  } else {
    Serial.println("[FAIL] Could not connect to Wi-Fi!");
    Serial.println("Check: SSID, password, signal strength");
    Serial.printf("Status code: %d\n", WiFi.status());
  }
}

void loop() {
  static unsigned long lastPrint = 0;

  if (millis() - lastPrint >= 5000) {
    lastPrint = millis();

    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("Connected | IP: %s | RSSI: %d dBm\n",
                    WiFi.localIP().toString().c_str(), WiFi.RSSI());
    } else {
      Serial.println("Disconnected, attempting reconnect...");
      WiFi.reconnect();
    }
  }
}
