# Real Hardware Success Checklist

## How to Verify Each Checkbox

### Basic ESP32
- [ ] **ESP32 uploads code** → Arduino IDE shows "Done uploading"
- [ ] **Serial Monitor works** → You see text at 115200 baud

### I2C Detection
- [ ] **0x68 detected** → I2C scanner shows "Found device at 0x68"
- [ ] **0x69 detected** → I2C scanner shows "Found device at 0x69"

### Sensor Readings
- [ ] **Hand sensor values change** → Move hand sensor, hand values change in Serial Monitor
- [ ] **Shoe sensor values change** → Move shoe sensor, shoe values change in Serial Monitor

### Wi-Fi
- [ ] **ESP32 joins Wi-Fi** → Serial shows "IP: 192.168.x.x"
- [ ] **ESP32 prints local IP** → You see the IP address in Serial Monitor

### Server Connection
- [ ] **Laptop backend /health works** → Browser shows JSON with "healthy"
- [ ] **WebSocket connects** → Serial shows "[WS] Connected"

### Data Storage
- [ ] **Backend accepts packets** → Backend terminal shows "WebSocket connection opened"
- [ ] **No device ID mismatch** → No error messages about device identity
- [ ] **No patient mismatch** → No error messages about patient consistency
- [ ] **SensorRecord rows increase** → `count_sensor_records.py` shows increasing count
- [ ] **Real hand values appear in SQLite** → `inspect_sensor_data.py` shows non-zero hand values
- [ ] **Real shoe values appear in SQLite** → `inspect_sensor_data.py` shows non-zero shoe values
- [ ] **server_received_at_ms is populated** → Values appear in the column

### Buzzer Cueing
- [ ] **Laptop can send FOG_CUE_ON** → Backend sends command
- [ ] **Buzzer starts** → You hear the buzzer
- [ ] **Buzzer stops automatically at duration_ms timeout** → Buzzer stops after set time
- [ ] **FOG_CUE_OFF stops buzzer immediately** → Buzzer stops on command

---

## Verification Commands

### Check record count
```powershell
python tools/count_sensor_records.py
```

### Inspect latest records
```powershell
python tools/inspect_sensor_data.py --limit 10
```

### Watch records live
```powershell
python tools/watch_sensor_data.py
```

### Direct SQLite query
```powershell
sqlite3 parkinson_monitoring.db "SELECT id, sequence, hand_ax, hand_ay, hand_az, server_received_at_ms FROM sensor_records ORDER BY id DESC LIMIT 5;"
```
