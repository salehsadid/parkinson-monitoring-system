# ESP32 Dual MPU6050 Firmware

This directory contains the ESP32 firmware for the Parkinson's Monitoring System.

## Current Status

**Stage 1: Not implemented yet.**

Firmware development will begin in Stage 2.

## Planned Features

### Stage 2 Implementation

- [ ] Dual MPU6050 sensor reading (hand + shoe)
- [ ] Wi-Fi connectivity
- [ ] WebSocket client for PC communication
- [ ] Buzzer control for FOG cueing
- [ ] Non-blocking command handling

### Hardware Requirements

- ESP32 development board (e.g., ESP32-DevKitC)
- 2x MPU6050 breakout boards
- Active buzzer
- Jumper wires
- Breadboard

### Wiring Diagram (Planned)

```
ESP32          MPU6050 #1 (Hand)
──────────────────────────────
GPIO 21 (SDA) → SDA
GPIO 22 (SCL) → SCL
3.3V          → VCC
GND           → GND

ESP32          MPU6050 #2 (Shoe)
──────────────────────────────
GPIO 16 (SDA) → SDA
GPIO 17 (SCL) → SCL
3.3V          → VCC
GND           → GND

ESP32          Buzzer
──────────────────────────────
GPIO 25       → Buzzer (+)
GND           → Buzzer (-)
```

### Communication Protocol

**ESP32 → PC**: Sensor data packets (50 Hz)
**PC → ESP32**: Commands (FOG_CUE_ON, FOG_CUE_OFF, PING)

See `docs/DATA_CONTRACT.md` for packet specifications.

## Development Environment

### Option 1: Arduino IDE

1. Install Arduino IDE
2. Add ESP32 board package
3. Install libraries:
   - WiFi
   - WebSockets
   - Wire (I2C)

### Option 2: PlatformIO

1. Install VS Code
2. Install PlatformIO extension
3. Create new ESP32 project
4. Add dependencies in `platformio.ini`

## Testing

Before deploying to ESP32:

1. Test with mock simulator
2. Verify packet format
3. Check Wi-Fi stability
4. Validate buzzer control

## Resources

- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [MPU6050 Library](https://github.com/jrowberg/i2cdevlib)
- [ArduinoWebSockets](https://github.com/Links204/arduinoWebSockets)
- [ESP32 I2C Guide](https://randomnerdtutorials.com/esp32-i2c-communication-arduino-ide/)
