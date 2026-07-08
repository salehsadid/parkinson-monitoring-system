# ESP32 to Laptop Server Guide

## Complete Step-by-Step Connection Guide

### Prerequisites
- ESP32 with firmware uploaded
- Both MPU6050 sensors wired
- Windows laptop on same network as ESP32
- Python installed with project dependencies

---

### STEP 1: Open PowerShell in Project Root

```powershell
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"
```

### STEP 2: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If venv doesn't exist, create it:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### STEP 3: Install Dependencies (if needed)

```powershell
pip install -r requirements.txt
```

### STEP 4: Prepare .env File

Copy example if not exists:
```powershell
Copy-Item .env.example .env
```

Verify `.env` contains:
```
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./parkinson_monitoring.db
```

### STEP 5: Start FastAPI Backend

```powershell
uvicorn pc_backend.app.main:app --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### STEP 6: Verify Health Endpoint

Open browser and go to:
```
http://localhost:8000/health
```

Or in PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

Expected: JSON response with status "healthy"

### STEP 7: Find Your Laptop IP

```powershell
ipconfig
```

Look for **Wi-Fi adapter** section:
```
Wireless LAN adapter Wi-Fi:

   IPv4 Address. . . . . . . . . . . : 192.168.0.105
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
```

The IPv4 address (e.g., `192.168.0.105`) is what ESP32 needs.

**Important**: Use the Wi-Fi adapter IP, NOT:
- 127.0.0.1 (localhost)
- 10.x.x.x (VPN)
- Any Ethernet adapter IP (unless using Ethernet)

### STEP 8: Put Laptop IP in ESP32 Firmware

In the firmware sketch, set:
```cpp
const char* PC_HOST = "192.168.0.105";  // Your laptop IP
```

### STEP 9: Ensure Same Network

ESP32 and laptop must be on the same reachable network:
- Both connected to same Wi-Fi router
- No AP/client isolation enabled on router
- No VLAN separation

### STEP 10: Upload Final Firmware

Upload `firmware/esp32_dual_mpu6050/esp32_dual_mpu6050.ino` to ESP32.

### STEP 11: Open Serial Monitor

Set baud rate to **115200**.

### STEP 12: Expected Connection Sequence

```
========================================
  Parkinson's Monitor - Real Firmware
  Dual MPU6050 + Buzzer + WebSocket
========================================
[OK] I2C initialized
[OK] Hand MPU6050 (0x68) ready
[OK] Shoe MPU6050 (0x69) ready
Connecting to YOUR_WIFI...
[OK] IP: 192.168.0.xxx
[WS] Connecting to 192.168.0.105:8000
[WS] Connected
========================================
ALL SYSTEMS READY
Sampling at 50 Hz
========================================
```

---

## Windows Firewall Troubleshooting

If ESP32 cannot connect:

### Check 1: Backend uses 0.0.0.0
The server must bind to `0.0.0.0`, not `127.0.0.1`.

### Check 2: Correct laptop IP
Use `ipconfig` to verify. Must be the Wi-Fi adapter IPv4.

### Check 3: Correct port
Default is 8000. Verify with backend startup output.

### Check 4: Same network
Both devices must be on the same subnet (e.g., 192.168.0.x).

### Check 5: Router isolation
Some routers have "AP Isolation" or "Client Isolation" that prevents devices from talking to each other. Disable this feature.

### Check 6: Windows Firewall
If prompted by Windows Firewall, allow Python/private network.

If still blocked:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules"
4. New Rule → Port → TCP → 8000 → Allow → Private → Name "FastAPI"

**Do NOT permanently disable firewall globally.**

---

## Verifying WebSocket Connection

When firmware connects, you should see in backend terminal:
```
INFO:     WebSocket connection opened
```

And in Serial Monitor:
```
[WS] Connected
```

If you see "WebSocket connection opened" in backend but ESP32 shows disconnected, check:
- IP address is correct
- Port 8000 is accessible
- No firewall blocking
- Both on same network
