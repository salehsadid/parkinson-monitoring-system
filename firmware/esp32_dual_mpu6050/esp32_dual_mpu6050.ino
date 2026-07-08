// ============================================================
// ESP32 Dual MPU6050 - Final Firmware
// ============================================================
// Parkinson's Monitoring System - Real Hardware Firmware
//
// Features:
// - Dual MPU6050 (hand 0x68, shoe 0x69)
// - Wi-Fi connection
// - WebSocket communication with FastAPI backend
// - Receives commands from server
// - Buzzer cueing with local timeout
// - Non-blocking loop
// - Automatic reconnection
// ============================================================

#include <Wire.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURATION - EDIT THESE
// ============================================
const char* WIFI_SSID      = "LSH_515";
const char* WIFI_PASSWORD  = "87827446";
const char* PC_HOST        = "192.168.0.118";  // Your laptop IP
const int   PC_PORT        = 8000;

const char* DEVICE_ID      = "ESP32_001";
const char* PATIENT_ID     = "P001";
const int   SAMPLE_RATE_HZ = 50;

#define HAND_I2C_ADDR  0x68
#define SHOE_I2C_ADDR  0x69
#define SDA_PIN        21
#define SCL_PIN        22
#define BUZZER_PIN     23

// ============================================
// STATE
// ============================================
WebSocketsClient webSocket;
unsigned long sequence = 0;
unsigned long lastSampleTime = 0;
const unsigned long sampleIntervalMs = 1000 / SAMPLE_RATE_HZ;

// Buzzer state
bool buzzerActive = false;
unsigned long buzzerStartTime = 0;
unsigned long buzzerDurationMs = 0;

#define LED_BUILTIN 2

// ============================================
// MPU6050 FUNCTIONS
// ============================================

struct IMUData {
  float ax, ay, az;
  float gx, gy, gz;
};

bool initMPU(uint8_t addr) {
  Wire.beginTransmission(addr);
  Wire.write(0x6B);
  Wire.write(0x00);
  byte error = Wire.endTransmission(true);
  return error == 0;
}

IMUData readMPU(uint8_t addr) {
  IMUData data = {0, 0, 0, 0, 0, 0};

  Wire.beginTransmission(addr);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  if (Wire.requestFrom((uint8_t)addr, (uint8_t)14, (uint8_t)true) != 14) {
    return data;
  }

  int16_t raw_ax = Wire.read() << 8 | Wire.read();
  int16_t raw_ay = Wire.read() << 8 | Wire.read();
  int16_t raw_az = Wire.read() << 8 | Wire.read();
  Wire.read(); Wire.read(); // temperature
  int16_t raw_gx = Wire.read() << 8 | Wire.read();
  int16_t raw_gy = Wire.read() << 8 | Wire.read();
  int16_t raw_gz = Wire.read() << 8 | Wire.read();

  // Convert to m/s^2 and deg/s (±2g and ±250°/s ranges)
  data.ax = raw_ax / 16384.0 * 9.81;
  data.ay = raw_ay / 16384.0 * 9.81;
  data.az = raw_az / 16384.0 * 9.81;
  data.gx = raw_gx / 131.0;
  data.gy = raw_gy / 131.0;
  data.gz = raw_gz / 131.0;

  return data;
}

// ============================================
// BUZZER FUNCTIONS
// ============================================

void buzzerOn() {
  digitalWrite(BUZZER_PIN, HIGH);
  buzzerActive = true;
  buzzerStartTime = millis();
  Serial.println("[BUZZER] ON");
}

void buzzerOff() {
  digitalWrite(BUZZER_PIN, LOW);
  buzzerActive = false;
  buzzerDurationMs = 0;
  Serial.println("[BUZZER] OFF");
}

void updateBuzzer() {
  if (buzzerActive && buzzerDurationMs > 0) {
    if (millis() - buzzerStartTime >= buzzerDurationMs) {
      Serial.println("[BUZZER] Auto-stop (duration_ms timeout)");
      buzzerOff();
    }
  }
}

// ============================================
// WEBSOCKET FUNCTIONS
// ============================================

void sendSensorPacket() {
  IMUData hand = readMPU(HAND_I2C_ADDR);
  IMUData shoe = readMPU(SHOE_I2C_ADDR);

  StaticJsonDocument<512> doc;

  doc["protocol_version"] = "1.0";
  doc["message_type"] = "sensor_data";
  doc["patient_id"] = PATIENT_ID;
  doc["device_id"] = DEVICE_ID;
  doc["sequence"] = sequence;
  doc["timestamp_ms"] = millis();
  doc["sampling_rate_hz"] = SAMPLE_RATE_HZ;

  JsonObject h = doc.createNestedObject("hand");
  h["ax"] = round(hand.ax * 100) / 100.0;
  h["ay"] = round(hand.ay * 100) / 100.0;
  h["az"] = round(hand.az * 100) / 100.0;
  h["gx"] = round(hand.gx * 100) / 100.0;
  h["gy"] = round(hand.gy * 100) / 100.0;
  h["gz"] = round(hand.gz * 100) / 100.0;

  JsonObject s = doc.createNestedObject("shoe");
  s["ax"] = round(shoe.ax * 100) / 100.0;
  s["ay"] = round(shoe.ay * 100) / 100.0;
  s["az"] = round(shoe.az * 100) / 100.0;
  s["gx"] = round(shoe.gx * 100) / 100.0;
  s["gy"] = round(shoe.gy * 100) / 100.0;
  s["gz"] = round(shoe.gz * 100) / 100.0;

  String json;
  serializeJson(doc, json);
  webSocket.sendTXT(json);
  sequence++;
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Disconnected");
      digitalWrite(LED_BUILTIN, LOW);
      break;

    case WStype_CONNECTED:
      Serial.println("[WS] Connected");
      digitalWrite(LED_BUILTIN, HIGH);
      break;

    case WStype_TEXT: {
      String msg = String((char*)payload);
      Serial.printf("[WS] Command: %s\n", msg.c_str());

      StaticJsonDocument<256> doc;
      DeserializationError error = deserializeJson(doc, msg);

      if (!error) {
        const char* command = doc["command"];
        const char* cmd_type = doc["message_type"];

        if (strcmp(command, "FOG_CUE_ON") == 0) {
          int duration = doc["duration_ms"] | 10000;
          buzzerDurationMs = duration;
          buzzerOn();
          Serial.printf("[CUE] FOG_CUE_ON, duration=%dms\n", duration);

        } else if (strcmp(command, "FOG_CUE_OFF") == 0) {
          buzzerOff();

        } else if (strcmp(command, "PING") == 0) {
          Serial.println("[CMD] Ping received");
        }
      }
      break;
    }
  }
}

// ============================================
// WI-FI
// ============================================

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
    Serial.println("\n[FAIL] Wi-Fi failed!");
    while (1) { delay(1000); }
  }
}

void connectWebSocket() {
  Serial.printf("[WS] Connecting to %s:%d\n", PC_HOST, PC_PORT);
  webSocket.begin(PC_HOST, PC_PORT, "/ws/device/" + String(DEVICE_ID));
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

// ============================================
// SETUP & LOOP
// ============================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("  Parkinson's Monitor - Real Firmware");
  Serial.println("  Dual MPU6050 + Buzzer + WebSocket");
  Serial.println("========================================");

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // Init I2C
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("[OK] I2C initialized");

  // Init MPU6050
  if (initMPU(HAND_I2C_ADDR)) {
    Serial.printf("[OK] Hand MPU6050 (0x%02X) ready\n", HAND_I2C_ADDR);
  } else {
    Serial.printf("[FAIL] Hand MPU6050 (0x%02X) not found!\n", HAND_I2C_ADDR);
    while (1) { delay(1000); }
  }

  if (initMPU(SHOE_I2C_ADDR)) {
    Serial.printf("[OK] Shoe MPU6050 (0x%02X) ready\n", SHOE_I2C_ADDR);
  } else {
    Serial.printf("[FAIL] Shoe MPU6050 (0x%02X) not found!\n", SHOE_I2C_ADDR);
    while (1) { delay(1000); }
  }

  // Connect
  connectWiFi();
  connectWebSocket();

  Serial.println("========================================");
  Serial.println("ALL SYSTEMS READY");
  Serial.printf("Sampling at %d Hz\n", SAMPLE_RATE_HZ);
  Serial.println("========================================");
}

void loop() {
  webSocket.loop();

  // Non-blocking sample timer
  unsigned long now = millis();
  if (now - lastSampleTime >= sampleIntervalMs) {
    lastSampleTime = now;

    if (webSocket.isConnected()) {
      sendSensorPacket();
    }
  }

  // Update buzzer timeout
  updateBuzzer();
}
