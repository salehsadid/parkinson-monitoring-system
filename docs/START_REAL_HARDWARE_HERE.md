# START REAL HARDWARE HERE

## The Master Guide: Zero to Working Hardware

This guide takes you from a pile of components to a fully working Parkinson's monitoring system with real sensors, real Wi-Fi, and real data storage.

**You need:**
- 1 ESP32 dev board
- 2 MPU6050 breakout boards
- 1 buzzer (active, 3.3V compatible)
- Jumper wires (~15)
- USB cable
- Windows laptop

---

## PART 1 — Check Hardware

1. Lay out all components on your desk
2. Verify ESP32 board has USB port
3. Verify both MPU6050 boards have labeled pins (VCC, GND, SDA, SCL, AD0)
4. Verify buzzer has two pins (+ and -)

**Expected**: You have all components.

---

## PART 2 — Wire Only ESP32 (No Sensors Yet)

Connect only USB cable to ESP32. No other wiring.

**Action**: Plug USB into laptop.

**Expected**: ESP32 powers on, maybe an LED lights up.

---

## PART 3 — Test ESP32 Upload

1. Open Arduino IDE
2. Install ESP32 board support: File → Preferences → Board Manager URLs → add `https://dl.espressif.com/dl/package_esp32_index.json`
3. Tools → Board → ESP32 Arduino → ESP32 Dev Module
4. Tools → Port → Select COM port (check Device Manager)
5. Open `firmware/esp32_dual_mpu6050/tests/01_esp32_basic/01_esp32_basic.ino`
6. Click Upload
7. Open Serial Monitor (115200 baud)

**Expected output**:
```
========================================
  ESP32 Basic Test - Stage 1.1
========================================
[OK] Serial Monitor connected
[OK] Board: ESP32
[OK] CPU freq: 240 MHz
[OK] Free heap: 300000+ bytes
========================================
PASS: ESP32 is working
========================================
Heartbeat: 1
Heartbeat: 2
```

**If this works**: ESP32 is functional. Proceed to PART 4.

---

## PART 4 — Connect First MPU6050

**BEFORE connecting, disconnect USB from ESP32.**

Wire MPU6050 #1 (hand sensor):

| MPU6050 Pin | ESP32 Pin |
|-------------|-----------|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |
| AD0 | GND |

**AD0 to GND = address 0x68**

Double-check:
- VCC goes to 3.3V (NOT 5V unless your module supports it)
- GND goes to GND
- SDA goes to GPIO21
- SCL goes to GPIO22
- AD0 goes to GND

---

## PART 5 — Run Scanner

Upload `firmware/esp32_dual_mpu6050/tests/02_i2c_scanner/02_i2c_scanner.ino`.

Open Serial Monitor.

**Expected output**:
```
  Found device at 0x68 <- MPU6050 (AD0=LOW, hand)
  1 devices found.
```

**If nothing found**: Check wiring. SDA/SCL might be swapped. Check power.

---

## PART 6 — Read First Sensor

Upload `firmware/esp32_dual_mpu6050/tests/03_single_mpu/03_single_mpu.ino`.

Open Serial Monitor.

**Expected output**:
```
AX=+0.12  AY=-0.04  AZ=+9.71 m/s2
GX=+2     GY=+1     GZ=0 raw
```

**Verification**: When you tilt the sensor, AZ changes. When still, AZ ≈ 9.8.

---

## PART 7 — Connect Second MPU6050

**Disconnect USB first.**

Wire MPU6050 #2 (shoe sensor) to the SAME SDA and SCL pins:

| MPU6050 Pin | Connection |
|-------------|------------|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO21 (same bus) |
| SCL | GPIO22 (same bus) |
| AD0 | 3.3V |

**AD0 to 3.3V = address 0x69**

Both sensors share SDA and SCL. The AD0 pin makes them different devices.

---

## PART 8 — Configure AD0

Verify:
- Hand sensor AD0 → GND (0x68)
- Shoe sensor AD0 → 3.3V (0x69)

---

## PART 9 — Verify 0x68 and 0x69

Re-upload I2C scanner (`02_i2c_scanner.ino`).

**Expected output**:
```
  Found device at 0x68 <- MPU6050 (AD0=LOW, hand)
  Found device at 0x69 <- MPU6050 (AD0=HIGH, shoe)
  2 devices found.
```

**If both show 0x68**: Second AD0 not connected to 3.3V.
**If both show 0x69**: First AD0 not connected to GND.

---

## PART 10 — Read Both Sensors

Upload `firmware/esp32_dual_mpu6050/tests/04_dual_mpu_serial/04_dual_mpu_serial.ino`.

**Expected output**:
```
HAND:
  AX=+0.12  AY=-0.04  AZ=+9.71 m/s2
SHOE:
  AX=+0.24  AY=+0.33  AZ=+9.22 m/s2
```

**Verification**: Move each sensor independently. Only its values change.

---

## PART 11 — Start Laptop Backend

Open PowerShell in project root:

```powershell
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn pc_backend.app.main:app --host 0.0.0.0 --port 8000
```

**Expected**: Server starts on http://0.0.0.0:8000

---

## PART 12 — Find Laptop IP

Open new PowerShell window:

```powershell
ipconfig
```

Find Wi-Fi adapter IPv4 (e.g., 192.168.0.105).

---

## PART 13 — Configure ESP32 Wi-Fi

In `firmware/esp32_dual_mpu6050/esp32_dual_mpu6050.ino`, edit:

```cpp
const char* WIFI_SSID      = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD  = "YOUR_WIFI_PASSWORD";
const char* PC_HOST        = "192.168.0.105";  // Your laptop IP
```

---

## PART 14 — Test WebSocket

Upload `firmware/esp32_dual_mpu6050/tests/06_websocket_test/06_websocket_test.ino`.

**Expected Serial output**:
```
[WS] Connected to server
[TX] Packet #0 sent
```

**Expected backend output**: You should see connection log.

---

## PART 15 — Upload Final Firmware

Upload `firmware/esp32_dual_mpu6050/esp32_dual_mpu6050.ino`.

**Expected Serial output**:
```
[OK] Hand MPU6050 (0x68) ready
[OK] Shoe MPU6050 (0x69) ready
[OK] IP: 192.168.0.xxx
[WS] Connected
ALL SYSTEMS READY
```

---

## PART 16 — Verify Real Packets

Let firmware run for 30 seconds.

Open new PowerShell:
```powershell
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"
.\venv\Scripts\Activate.ps1
python tools/count_sensor_records.py
```

**Expected**: Record count increasing.

---

## PART 17 — Inspect SQLite

```powershell
python tools/inspect_sensor_data.py --limit 5
```

**Expected**: Real sensor values with hand and shoe readings.

---

## PART 18 — Watch Live Stored Readings

```powershell
python tools/watch_sensor_data.py
```

**Action**: Physically move the hand sensor. You should see values change in real-time as packets arrive.

---

## PART 19 — Connect Buzzer Safely

**Disconnect USB first.**

Wire buzzer:
- Signal pin → GPIO23
- GND → GND

**Check your buzzer type:**
- Active buzzer: Apply HIGH = sound, LOW = silent
- Passive buzzer: Needs PWM/tone signal
- High-current buzzer: Use transistor driver

---

## PART 20 — Test FOG_CUE_ON

With final firmware running, from backend you can trigger a cue.

Alternatively, test buzzer directly by modifying firmware to turn buzzer ON in setup():
```cpp
digitalWrite(BUZZER_PIN, HIGH);
delay(2000);
digitalWrite(BUZZER_PIN, LOW);
```

---

## PART 21 — Test Automatic Timeout

The final firmware includes local timeout. If FOG_CUE_ON specifies duration_ms=5000, the buzzer will automatically stop after 5 seconds even if FOG_CUE_OFF is never received.

---

## PART 22 — Troubleshooting

### ESP32 won't upload
- Hold BOOT button during upload
- Try different USB cable
- Check COM port in Device Manager

### No I2C devices found
- Check SDA/SCL not swapped
- Check power connections
- Check common ground
- Verify AD0 state

### Wi-Fi won't connect
- Check SSID and password
- Check signal strength
- Try closer to router

### WebSocket won't connect
- Verify laptop IP is correct (ipconfig)
- Verify backend is running with --host 0.0.0.0
- Check Windows Firewall
- Verify same network

### Buzzer doesn't sound
- Check buzzer type (active/passive)
- Check wiring
- Check GPIO pin number
- Verify buzzer voltage rating
