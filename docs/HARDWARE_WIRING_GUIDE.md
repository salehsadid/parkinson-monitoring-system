# Hardware Wiring Guide

## Target Configuration

| Component | Connection | Pin |
|-----------|------------|-----|
| Hand MPU6050 | SDA | GPIO21 |
| Hand MPU6050 | SCL | GPIO22 |
| Hand MPU6050 | AD0 | GND (0x68) |
| Shoe MPU6050 | SDA | GPIO21 |
| Shoe MPU6050 | SCL | GPIO22 |
| Shoe MPU6050 | AD0 | 3.3V (0x69) |
| Buzzer | Signal | GPIO23 |

---

## I2C Address Explanation

Both MPU6050 share the same I2C bus (SDA/SCL). The AD0 pin selects the address:

| AD0 State | Address | Device |
|-----------|---------|--------|
| LOW (GND) | 0x68 | Hand sensor |
| HIGH (3.3V) | 0x69 | Shoe sensor |

This allows both sensors to coexist on the same two wires.

---

## Connection Table

### Power (Common to all devices)

```
ESP32 3.3V  ──────┬──────────────────┐
                   │                  │
                   v                  v
            Hand MPU6050 VCC    Shoe MPU6050 VCC

ESP32 GND   ──────┬──────────┬──────────────────┐
                   │          │                  │
                   v          v                  v
            Hand MPU6050 GND  Shoe MPU6050 GND   Buzzer GND
```

### I2C Bus (Shared)

```
ESP32 GPIO21 (SDA) ─────┬──────────────────┐
                         │                  │
                         v                  v
                  Hand MPU6050 SDA    Shoe MPU6050 SDA

ESP32 GPIO22 (SCL) ─────┬──────────────────┐
                         │                  │
                         v                  v
                  Hand MPU6050 SCL    Shoe MPU6050 SCL
```

### Address Select

```
Hand MPU6050 AD0 ────── GND          (address 0x68)
Shoe MPU6050 AD0 ────── 3.3V         (address 0x69)
```

### Buzzer

```
ESP32 GPIO23 ────── Buzzer signal/control pin
ESP32 GND    ────── Buzzer GND (or driver GND)
```

---

## ASCII Circuit Diagram

```
                    ESP32 Dev Board
              ┌──────────────────────┐
              │                      │
         3.3V─┤ 3V3                  │
          GND─┤ GND                  │
         GPIO21─┤ SDA             │
         GPIO22─┤ SCL             │
         GPIO23─┤ BUZZER CTRL    │
              │                      │
              └───────┬──────────────┘
                      │
         I2C BUS (shared SDA/SCL)
                      │
        ┌─────────────┴──────────────┐
        │                            │
        v                            v
  ┌───────────────┐          ┌───────────────┐
  │ HAND MPU6050  │          │ SHOE MPU6050  │
  │               │          │               │
  │ VCC ← 3.3V   │          │ VCC ← 3.3V   │
  │ GND ← GND    │          │ GND ← GND    │
  │ SDA ← GPIO21 │          │ SDA ← GPIO21 │
  │ SCL ← GPIO22 │          │ SCL ← GPIO22 │
  │ AD0 ← GND    │          │ AD0 ← 3.3V   │
  │ (addr: 0x68) │          │ (addr: 0x69) │
  └───────────────┘          └───────────────┘
        │
        v
  ┌───────────┐
  │  BUZZER   │
  │           │
  │ + ← GPIO23│
  │ - ← GND   │
  └───────────┘
```

---

## Buzzer Safety Warning

**The exact buzzer circuit depends on your buzzer type.**

### Active Buzzer
- Can be switched ON/OFF directly from GPIO (if rated for 3.3V and <40mA)
- Set HIGH = on, LOW = off

### Passive Buzzer
- Requires frequency/PWM signal to produce tone
- Use `tone()` or LEDC for sound generation

### High-Current Buzzer
- Must NOT be driven directly from ESP32 GPIO
- Use a transistor (NPN like 2N2222 or MOSFET) as a switch
- GPIO controls transistor base/gate, transistor switches buzzer power

**Before connecting any buzzer**:
1. Check voltage rating (3.3V or 5V)
2. Check current rating (most small buzzers are fine, large ones need drivers)
3. If uncertain, use a transistor driver circuit

---

## Why Both MPU6050 Can Share SDA/SCL

I2C is a multi-device bus. Multiple devices share the same two wires (SDA, SCL) as long as:
- Each device has a unique address
- No address conflicts exist

With AD0=LOW (0x68) and AD0=HIGH (0x69), both MPU6050 are distinguishable.

---

## How to Verify Your ESP32 Board

1. **Check the silk screen**: Most ESP32 dev boards label GPIO pins
2. **Check 3.3V**: Most MPU6050 breakouts accept 3.3V. Some accept 5V but check datasheet.
3. **Verify COM port**: Plug in USB, check Device Manager for COM port

---

## How to Verify MPU6050 Breakout

1. **Check labels**: Most breakouts label VCC, GND, SDA, SCL, AD0
2. **Check voltage**: Most MPU6050 modules have onboard 3.3V regulator. Some accept 5V input, some only 3.3V.
3. **Default state**: AD0 floating may read as LOW or HIGH depending on module

---

## Before Connecting USB Power Checklist

- [ ] ESP32 disconnected from USB
- [ ] Verified 3.3V and GND pins (no VCC-GND short)
- [ ] Verified SDA connected to GPIO21
- [ ] Verified SCL connected to GPIO22
- [ ] Verified common ground between all devices
- [ ] Hand MPU6050 AD0 connected to GND
- [ ] Shoe MPU6050 AD0 connected to 3.3V
- [ ] Buzzer rating checked (voltage, current)
- [ ] No high-current buzzer directly on GPIO without driver
- [ ] All jumper wires firmly seated
