// ============================================================
// Test 06: WebSocket Communication Test
// ============================================================
// Purpose: Test ESP32 -> laptop backend WebSocket communication.
// Sends a valid SensorPacket matching actual Pydantic schema.
// ============================================================

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURE THESE FOR YOUR NETWORK
// ============================================
const char* WIFI_SSID      = "LSH_515";
const char* WIFI_PASSWORD  = "87827446";
const char* PC_HOST        = "192.168.0.118"; // Your laptop IP
const int   PC_PORT        = 8000;
const char* DEVICE_ID      = "ESP32_001";
const char* PATIENT_ID     = "P001";
// ============================================

WebSocketsClient webSocket;
unsigned long sequence = 0;

#define LED_BUILTIN 2

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Disconnected");
      digitalWrite(LED_BUILTIN, LOW);
      break;
    case WStype_CONNECTED:
      Serial.println("[WS] Connected to server");
      digitalWrite(LED_BUILTIN, HIGH);
      break;
    case WStype_TEXT: {
      String msg = String((char*)payload);
      Serial.printf("[WS] Received: %s\n", msg.c_str());
      break;
    }
  }
}

void connectWiFi() {
  Serial.printf("Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[OK] IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[FAIL] Wi-Fi connection failed!");
    while (1) { delay(1000); }
  }
}

void connectWebSocket() {
  Serial.printf("Connecting to ws://%s:%d/ws/device/%s\n", PC_HOST, PC_PORT, DEVICE_ID);
  webSocket.begin(PC_HOST, PC_PORT, "/ws/device/" + String(DEVICE_ID));
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void sendTestPacket() {
  // Build JSON matching exact SensorPacket schema
  StaticJsonDocument<512> doc;

  doc["protocol_version"] = "1.0";
  doc["message_type"] = "sensor_data";
  doc["patient_id"] = PATIENT_ID;
  doc["device_id"] = DEVICE_ID;
  doc["sequence"] = sequence;
  doc["timestamp_ms"] = millis();
  doc["sampling_rate_hz"] = 50;

  // Hand (fake test values)
  JsonObject hand = doc.createNestedObject("hand");
  hand["ax"] = 0.12;
  hand["ay"] = -0.04;
  hand["az"] = 9.71;
  hand["gx"] = 2.30;
  hand["gy"] = 1.10;
  hand["gz"] = -0.40;

  // Shoe (fake test values)
  JsonObject shoe = doc.createNestedObject("shoe");
  shoe["ax"] = 1.24;
  shoe["ay"] = 0.33;
  shoe["az"] = 9.22;
  shoe["gx"] = 12.40;
  shoe["gy"] = 4.20;
  shoe["gz"] = 2.10;

  String json;
  serializeJson(doc, json);

  webSocket.sendTXT(json);
  Serial.printf("[TX] Packet #%lu sent\n", sequence);
  sequence++;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  WebSocket Communication Test");
  Serial.println("========================================");

  pinMode(LED_BUILTIN, OUTPUT);

  connectWiFi();
  connectWebSocket();

  Serial.println("========================================");
  Serial.println("Sending test packets every 2 seconds...");
  Serial.println("========================================");
}

void loop() {
  webSocket.loop();

  static unsigned long lastSend = 0;
  if (millis() - lastSend >= 2000) {
    lastSend = millis();
    if (webSocket.isConnected()) {
      sendTestPacket();
    } else {
      Serial.println("[WS] Not connected, waiting...");
    }
  }
}
