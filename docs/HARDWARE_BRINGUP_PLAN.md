# Hardware Bring-Up Plan

## Overview

This plan guides you from a bare ESP32 to a fully working system with dual MPU6050 sensors, Wi-Fi, WebSocket communication, and buzzer cueing.

## Hardware Requirements

| Component | Quantity | Purpose |
|-----------|----------|---------|
| ESP32 dev board | 1 | Main controller |
| MPU6050 breakout | 2 | IMU sensors |
| Buzzer | 1 | Audio cue output |
| Jumper wires | ~15 | Connections |
| USB cable | 1 | Power + programming |
| Windows laptop | 1 | Server + development |

---

## Milestone A: Test ESP32 Alone

**Objective**: Verify ESP32 uploads code and Serial Monitor works.

**Wiring**: None (USB only).

**Code**: `firmware/esp32_dual_mpu6050/tests/01_esp32_basic/01_esp32_basic.ino`

**Steps**:
1. Open Arduino IDE
2. Install ESP32 board support if needed
3. Select board: "ESP32 Dev Module"
4. Select correct COM port
5. Upload `01_esp32_basic.ino`
6. Open Serial Monitor at 115200 baud

**Expected output**:
```
========================================
  ESP32 Basic Test - Stage 1.1
========================================
[OK] Serial Monitor connected
[OK] Board: ESP32
[OK] CPU freq: 240 MHz
[OK] Free heap: 300000+ bytes
[OK] LED pin configured
========================================
PASS: ESP32 is working
========================================
Heartbeat: 1
Heartbeat: 2
```

**Pass condition**: You see heartbeat messages incrementing.

**Failure symptoms**: No output, garbled text, upload error.

**Troubleshooting**:
- No output: Check correct COM port selected
- Garbled text: Set baud rate to 115200
- Upload error: Hold BOOT button during upload, try different USB cable
- Board not detected: Install CP2102 or CH340 drivers

---

## Milestone B: Connect and Detect MPU6050 #1

**Objective**: Wire first MPU6050 (hand) and detect it via I2C.

**Wiring** (hand sensor only):
- ESP32 3.3V → MPU6050 #1 VCC
- ESP32 GND → MPU6050 #1 GND
- ESP32 GPIO21 → MPU6050 #1 SDA
- ESP32 GPIO22 → MPU6050 #1 SCL
- MPU6050 #1 AD0 → GND (address 0x68)

**Code**: `firmware/esp32_dual_mpu6050/tests/02_i2c_scanner/02_i2c_scanner.ino`

**Steps**:
1. Wire MPU6050 #1 as above (before powering)
2. Upload I2C scanner
3. Open Serial Monitor

**Expected output**:
```
  Found device at 0x68 <- MPU6050 (AD0=LOW, hand)
  1 devices found.
```

**Pass condition**: 0x68 appears in scan.

**Failure symptoms**: No devices found.

**Troubleshooting**:
- No devices: Check SDA/SCL not swapped, verify power, check common GND
- Wrong address: Verify AD0 pin state

---

## Milestone C: Connect and Detect MPU6050 #2

**Objective**: Add second MPU6050 (shoe) with different address.

**Wiring** (add shoe sensor):
- ESP32 3.3V → MPU6050 #2 VCC
- ESP32 GND → MPU6050 #2 GND
- MPU6050 #2 SDA → same bus as #1
- MPU6050 #2 SCL → same bus as #1
- MPU6050 #2 AD0 → 3.3V (address 0x69)

**Code**: Same I2C scanner (already uploaded).

**Expected output**:
```
  Found device at 0x68 <- MPU6050 (AD0=LOW, hand)
  Found device at 0x69 <- MPU6050 (AD0=HIGH, shoe)
  2 devices found.
```

**Pass condition**: Both 0x68 and 0x69 appear.

**Failure symptoms**: Only one device, both at same address, or none.

**Troubleshooting**:
- Only 0x68: Check AD0 on second sensor is HIGH (3.3V)
- Both 0x68: AD0 not connected HIGH on second sensor
- Both 0x69: AD0 not connected LOW on first sensor

---

## Milestone D: Verify Both MPU6050 Sensors Simultaneously

**Objective**: Confirm both sensors are readable on same I2C bus.

**Code**: `firmware/esp32_dual_mpu6050/tests/04_dual_mpu_serial/04_dual_mpu_serial.ino`

**Expected output**: Both HAND and SHOE sections with changing values.

---

## Milestone E: Read Real Values from Both Sensors

**Objective**: See real accelerometer and gyroscope data.

**Code**: Same as Milestone D (04_dual_mpu_serial).

**Expected output**:
```
HAND:
  AX=+0.12  AY=-0.04  AZ=+9.71 m/s2
  GX=+2     GY=+1     GZ=0 raw

SHOE:
  AX=+0.24  AY=+0.33  AZ=+9.22 m/s2
  GX=+12    GY=+4     GZ=+2 raw
```

**Verification**:
- When stationary: AZ near 9.8 m/s² (gravity), others near 0
- When you move hand sensor: hand values change
- When you move shoe sensor: shoe values change
- Gyro shows small noise when still

---

## Milestone F: Connect ESP32 to Wi-Fi

**Objective**: ESP32 joins your local network.

**Code**: `firmware/esp32_dual_mpu6050/tests/05_wifi_test/05_wifi_test.ino`

**Prerequisite**: Set `WIFI_SSID` and `WIFI_PASSWORD` in the sketch.

**Expected output**:
```
Connecting to YOUR_WIFI_NAME....
[OK] IP: 192.168.0.xxx
[OK] Signal: -45 dBm
```

**Pass condition**: ESP32 prints its local IP.

---

## Milestone G: Connect ESP32 WebSocket to Laptop Backend

**Objective**: ESP32 connects to your FastAPI server.

**Steps**:
1. Start backend (see ESP32-to-Laptop guide)
2. Find your laptop IP
3. Set `PC_HOST` in sketch
4. Upload WebSocket test sketch
5. Check Serial Monitor for connection

**Code**: `firmware/esp32_dual_mpu6050/tests/06_websocket_test/06_websocket_test.ino`

**Expected output**:
```
[WS] Connected to server
[TX] Packet #0 sent
[TX] Packet #1 sent
```

---

## Milestone H: Send Real Dual-MPU6050 Packets

**Objective**: Send real sensor data from both sensors to server.

**Code**: `firmware/esp32_dual_mpu6050/esp32_dual_mpu6050.ino` (final firmware)

**Expected**: Serial shows packets being sent, server logs show received packets.

---

## Milestone I: Verify Real Packets Stored in SQLite

**Objective**: Confirm sensor data appears in database.

**Steps**:
1. Let firmware run for 30+ seconds
2. Run inspection tool:
```
python tools/inspect_sensor_data.py --limit 10
```

**Expected**: Real sensor values in database with server_received_at_ms.

---

## Milestone J: Send FOG_CUE_ON from Laptop to ESP32

**Objective**: Server sends command to activate buzzer.

**Method**: Use cue service or manual WebSocket test.

---

## Milestone K: Verify Real Buzzer Cueing and Local Timeout

**Objective**: Buzzer turns on when FOG_CUE_ON received, stops after duration_ms.

**Expected**:
- Buzzer activates on FOG_CUE_ON
- Buzzer deactivates on FOG_CUE_OFF
- Buzzer auto-stops after duration_ms timeout
