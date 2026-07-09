# Parkinson's Tremor and FOG Monitoring & Cueing System

## Project Overview

This system monitors Parkinson's disease symptoms using wearable sensors:

- **2 MPU6050 IMU sensors**:
  - Hand sensor (tremor analysis) - mounted on glove or ring
  - Shoe sensor (Freezing of Gait detection) - mounted on shoe
- **1 ESP32 microcontroller**: Reads both sensors and communicates via Wi-Fi
- **1 buzzer**: Provides rhythmic cueing during FOG episodes
- **Local PC/laptop**: Processes data and runs ML models
- **SQLite database**: Stores sensor data and events locally
- **Caregiver dashboard**: Future interface for monitoring (Blynk or custom app)

**Important**: This is a research prototype, not a medical device. It is not clinically validated and should not be used for diagnosis or treatment decisions.

---

## Start Here

### Real Hardware (Stage 2 — Verified)

**Hardware is connected and working?**

→ **[docs/START_REAL_HARDWARE_HERE.md](docs/START_REAL_HARDWARE_HERE.md)**

### Signal Validation & Analysis (Stage 2.1 — Current)

**Validate real sensor data quality and ML readiness?**

→ **[docs/START_STAGE_2_1_HERE.md](docs/START_STAGE_2_1_HERE.md)**

---

## Real Hardware Data Flow

```
2x MPU6050 (hand + shoe)
        │
        ▼
      ESP32
        │
        │ Wi-Fi WebSocket
        ▼
   FastAPI Server (laptop)
        │
        ▼
   Pydantic Validation
        │
        ▼
   SQLAlchemy ORM
        │
        ▼
    SQLite Database
```

## How to Inspect and Analyze Stored Data

```powershell
# View latest records
python tools/inspect_sensor_data.py --limit 20

# Watch live data arriving
python tools/watch_sensor_data.py

# Record count statistics
python tools/count_sensor_records.py
```

### Stage 2.1 Analysis Tools

```powershell
# Real-time signal visualization (live plot)
python tools/live_signal_plot.py

# Record a session (start/stop with metadata)
python tools/record_session.py start
python tools/record_session.py stop

# Export session data to CSV
python tools/export_sensor_session.py --output data/export.csv

# Storage growth analysis (72-hour projection)
python tools/analyze_database_growth.py

# Stream stability analysis (long-running)
python tools/analyze_stream_stability.py

# Comprehensive data quality report
python tools/generate_data_quality_report.py
```

---

## Current Stage

**Stage 2.1: Real Signal Validation — COMPLETE**

Real hardware verified. Analysis modules, CLI tools, and documentation complete. 83 tests passing.

---

## What Was Implemented

### Stage 1: Project Foundation

- [x] FastAPI backend with REST and WebSocket endpoints
- [x] Pydantic schemas for sensor, command, and event validation
- [x] SQLite database with SQLAlchemy ORM
- [x] WebSocket connection manager for ESP32 devices
- [x] 72-hour data retention service
- [x] Processing and inference interfaces (placeholders)
- [x] Cue service for FOG buzzer activation
- [x] Dashboard no-op interface (ready for Blynk integration)
- [x] Mock ESP32 simulator with synthetic signal generation
- [x] Comprehensive test suite
- [x] Configuration system with environment variables
- [x] Logging setup with loguru
- [x] Documentation (architecture, data contracts, reports)

### Stage 1.1: Hardening

- [x] Device identity validation (patient_id + device_id consistency)
- [x] Single-transaction database commits
- [x] Pydantic v2 ConfigDict migration (no deprecation warnings)
- [x] CommandPacket duration_ms cue contract (1000–30000ms)

### Stage 2: Real ESP32 Hardware (Verified)

- [x] Final firmware: `esp32_dual_mpu6050.ino` — dual MPU6050 + Wi-Fi + buzzer
- [x] 6 incremental test sketches (basic → I2C → single → dual → Wi-Fi → WebSocket)
- [x] Real sensor data stored in SQLite (4521+ rows, 1.16 MB)
- [x] Physical verification by user — end-to-end confirmed

### Stage 2.1: Signal Validation (Current)

- [x] Analysis modules: stream quality, signal quality, storage, session metadata
- [x] CLI tools: live plot, session recording, CSV export, storage analysis, quality report
- [x] Documentation: validation protocol, storage evaluation, ML readiness
- [x] Tests: 83 passing (57 original + 26 new analysis tests)
- [x] Sidecar JSON session metadata (no DB migration)

---

## Repository Structure

```
parkinson-monitoring-system/
├── firmware/
│   └── esp32_dual_mpu6050/       # ESP32 firmware
│       ├── esp32_dual_mpu6050.ino # Final firmware (dual MPU6050 + Wi-Fi + buzzer)
│       └── tests/                  # Incremental test sketches (01–06)
├── pc_backend/
│   └── app/
│       ├── api/                   # REST endpoints
│       ├── analysis/              # Stage 2.1: signal/stream/storage/session analysis
│       ├── core/                  # Configuration, logging
│       ├── database/              # SQLAlchemy models, retention
│       ├── inference/             # ML model interfaces
│       ├── processing/            # Signal processing interfaces
│       ├── schemas/               # Pydantic validation
│       ├── services/              # Cue service, dashboard
│       └── websocket/             # WebSocket manager
├── ml/
│   ├── datasets/                  # Raw data storage
│   ├── preprocessing/             # Signal preprocessing
│   ├── features/                  # Feature extraction
│   ├── training/                  # Model training
│   ├── evaluation/                # Model evaluation
│   └── saved_models/              # Trained models
├── simulator/
│   ├── mock_esp32.py              # Mock ESP32 simulator
│   └── signal_generator.py        # Synthetic signals
├── tools/
│   ├── inspect_sensor_data.py     # View stored sensor readings
│   ├── watch_sensor_data.py       # Live monitor new records
│   ├── count_sensor_records.py    # Record statistics
│   ├── live_signal_plot.py        # Real-time matplotlib visualization
│   ├── plot_sensor_session.py     # Offline session plots
│   ├── record_session.py          # Start/stop recording sessions
│   ├── export_sensor_session.py   # Export data to CSV
│   ├── analyze_database_growth.py # Storage growth projections
│   ├── analyze_stream_stability.py # Long-running stability metrics
│   └── generate_data_quality_report.py # Comprehensive quality report
├── data/
│   ├── raw/                       # Raw sensor data
│   ├── interim/                   # Intermediate data
│   ├── processed/                 # Final data
│   └── sessions/                  # Session metadata (sidecar JSON)
├── tests/                         # Test suite (83 tests)
├── docs/                          # Documentation
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   MPU6050 #1    │     │      ESP32      │     │   MPU6050 #2    │
│   (Hand)        ├────►│  Microcontroller ◄─────┤   (Shoe)        │
│   Tremor        │     │                  │     │   FOG           │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                                 │ Wi-Fi
                                 ▼
                        ┌─────────────────┐
                        │    Local PC     │
                        │   FastAPI       │
                        │   WebSocket     │
                        └────────┬────────┘
                                 │
                        ┌────────┴────────┐
                        │                 │
                        ▼                 ▼
               ┌─────────────┐   ┌─────────────┐
               │   SQLite    │   │   Future    │
               │   Database  │   │   Dashboard │
               └─────────────┘   └─────────────┘
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (optional)

### Windows PowerShell

```powershell
# Clone or download the repository
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
Copy-Item .env.example .env
```

### Windows CMD

```cmd
# Clone or download the repository
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
```

### Linux/macOS

```bash
# Clone or download the repository
cd /path/to/parkinson-monitoring-system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

---

## How to Run the Backend

```bash
# Make sure virtual environment is activated

# Start the FastAPI server
uvicorn pc_backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## How to Run the ESP32 Simulator

Open a new terminal (keep the backend running):

```bash
# Navigate to simulator directory
cd simulator

# Run with default settings (baseline mode)
python mock_esp32.py

# Run with specific options
python mock_esp32.py --device-id ESP32_001 --patient-id P001 --signal-mode tremor_like
```

### Simulator Options

| Option | Default | Description |
|--------|---------|-------------|
| `--device-id` | ESP32_001 | Device identifier |
| `--patient-id` | P001 | Patient identifier |
| `--server-url` | ws://localhost:8000 | WebSocket server URL |
| `--sampling-rate` | 50 | Sampling rate in Hz |
| `--signal-mode` | baseline | Signal mode (baseline, tremor_like, gait_like, fog_like) |

---

## How to Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_schemas.py -v

# Run with coverage
python -m pytest tests/ --cov=pc_backend
```

---

## API Endpoints

### GET /

Returns project information.

```json
{
  "project": "Parkinson's Monitoring System",
  "version": "0.1.0",
  "status": "running",
  "stage": "Stage 1: Project Foundation"
}
```

### GET /health

Returns system health status.

```json
{
  "api_status": "healthy",
  "database_status": "connected",
  "connected_devices": 0,
  "timestamp": "2026-07-07T00:00:00"
}
```

### WebSocket /ws/device/{device_id}

Real-time communication with ESP32 devices.

**Send sensor data:**
```json
{
  "protocol_version": "1.0",
  "message_type": "sensor_data",
  "patient_id": "P001",
  "device_id": "ESP32_001",
  "sequence": 12345,
  "timestamp_ms": 1720012345678,
  "sampling_rate_hz": 50,
  "hand": {
    "ax": 0.12, "ay": -0.04, "az": 9.71,
    "gx": 2.30, "gy": 1.10, "gz": -0.40
  },
  "shoe": {
    "ax": 1.24, "ay": 0.33, "az": 9.22,
    "gx": 12.40, "gy": 4.20, "gz": 2.10
  }
}
```

---

## Database

- **Location**: `parkinson_monitoring.db` (in project root)
- **Type**: SQLite (local file-based)
- **Tables**: patients, devices, sensor_records, fog_events, tremor_results
- **Retention**: 72-hour rolling window for sensor records

---

## Data Contract

### Sensor Packet

```json
{
  "protocol_version": "1.0",
  "message_type": "sensor_data",
  "patient_id": "P001",
  "device_id": "ESP32_001",
  "sequence": 12345,
  "timestamp_ms": 1720012345678,
  "sampling_rate_hz": 50,
  "hand": {
    "ax": 0.12, "ay": -0.04, "az": 9.71,
    "gx": 2.30, "gy": 1.10, "gz": -0.40
  },
  "shoe": {
    "ax": 1.24, "ay": 0.33, "az": 9.22,
    "gx": 12.40, "gy": 4.20, "gz": 2.10
  }
}
```

**Units**:
- Acceleration (ax, ay, az): m/s²
- Gyroscope (gx, gy, gz): degrees/second
- Timestamp: Unix epoch milliseconds

---

## Manual Actions Required From Me

### A. AUTOMATICALLY IMPLEMENTED BY THE CODING AGENT

See "What Was Implemented in Stage 1" above.

### B. MANUAL ACTION REQUIRED FROM THE HUMAN DEVELOPER

#### 1. Install Python 3.11+

**WHAT I NEED TO DO**: Ensure Python 3.11 or higher is installed on my system.

**WHY I NEED TO DO IT**: The project requires Python 3.11+ for modern features and compatibility.

**EXACT STEPS**:
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. Check "Add Python to PATH" during installation
4. Verify: `python --version`

**EXPECTED RESULT**: Python 3.11.x or higher is installed.

**HOW TO VERIFY**: Run `python --version` in terminal.

---

#### 2. Create Virtual Environment

**WHAT I NEED TO DO**: Create an isolated Python environment for the project.

**WHY I NEED TO DO IT**: Prevents dependency conflicts with other projects.

**EXACT STEPS**:
```bash
cd "D:\Academic Projects\IoT\parkinson-monitoring-system"
python -m venv venv
.\venv\Scripts\Activate  # Windows PowerShell
```

**EXPECTED RESULT**: Virtual environment is created and activated.

**HOW TO VERIFY**: Terminal prompt shows `(venv)` prefix.

---

#### 3. Install Dependencies

**WHAT I NEED TO DO**: Install all required Python packages.

**WHY I NEED TO DO IT**: The project depends on FastAPI, SQLAlchemy, Pydantic, and other libraries.

**EXACT STEPS**:
```bash
pip install -r requirements.txt
```

**EXPECTED RESULT**: All packages installed successfully.

**HOW TO VERIFY**: Run `pip list` and check for required packages.

---

#### 4. Copy Environment File

**WHAT I NEED TO DO**: Create a `.env` file from the template.

**WHY I NEED TO DO IT**: Configuration is loaded from environment variables.

**EXACT STEPS**:
```bash
Copy-Item .env.example .env  # Windows PowerShell
# or
cp .env.example .env  # Linux/macOS
```

**EXPECTED RESULT**: `.env` file exists in project root.

**HOW TO VERIFY**: `ls .env` or `dir .env` shows the file.

---

#### 5. Start Backend Server

**WHAT I NEED TO DO**: Start the FastAPI server.

**WHY I NEED TO DO IT**: The backend handles WebSocket connections and stores data.

**EXACT STEPS**:
```bash
uvicorn pc_backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**EXPECTED RESULT**: Server starts and shows "Application started successfully".

**HOW TO VERIFY**: Open browser to http://localhost:8000/health

---

#### 6. Start Simulator

**WHAT I NEED TO DO**: Run the mock ESP32 simulator.

**WHY I NEED TO DO IT**: Generates test data without physical hardware.

**EXACT STEPS** (in new terminal):
```bash
cd simulator
python mock_esp32.py
```

**EXPECTED RESULT**: Simulator connects and sends sensor data.

**HOW TO VERIFY**: Check backend logs show "Device connected: ESP32_001".

---

#### 7. Verify Health Endpoint

**WHAT I NEED TO DO**: Check the health endpoint returns correct status.

**WHY I NEED TO DO IT**: Confirms the backend is running correctly.

**EXACT STEPS**:
```bash
curl http://localhost:8000/health
```

**EXPECTED RESULT**:
```json
{
  "api_status": "healthy",
  "database_status": "connected",
  "connected_devices": 0
}
```

**HOW TO VERIFY**: Response shows `"api_status": "healthy"`.

---

#### 8. Verify SQLite Database

**WHAT I NEED TO DO**: Check the database file was created.

**WHY I NEED TO DO IT**: Confirms database initialization worked.

**EXACT STEPS**:
```bash
ls *.db  # Linux/macOS
dir *.db  # Windows
```

**EXPECTED RESULT**: `parkinson_monitoring.db` file exists.

**HOW TO VERIFY**: File exists and is not empty.

---

#### 9. Run Tests

**WHAT I NEED TO DO**: Execute the test suite.

**WHY I NEED TO DO IT**: Verifies all components work correctly.

**EXACT STEPS**:
```bash
python -m pytest tests/ -v
```

**EXPECTED RESULT**: All 83 tests pass.

**HOW TO VERIFY**: Output shows "83 passed".

---

#### 10. Review Packet Contract

**WHAT I NEED TO DO**: Understand the sensor packet format.

**WHY I NEED TO DO IT**: ESP32 firmware must send packets in this format.

**EXACT STEPS**:
1. Read `docs/DATA_CONTRACT.md`
2. Review `pc_backend/app/schemas/sensor.py`
3. Note required fields and units

**EXPECTED RESULT**: Understanding of packet structure.

**HOW TO VERIFY**: Can explain the packet format to others.

---

#### 11. Prepare ESP32 Hardware

**WHAT I NEED TO DO**: Purchase and prepare ESP32 and sensors.

**WHY I NEED TO DO IT**: Stage 2 requires real hardware.

**EXACT STEPS**:
1. Purchase ESP32 development board
2. Purchase 2x MPU6050 breakout boards
3. Purchase active buzzer
4. Gather jumper wires and breadboard
5. Set up Arduino IDE or PlatformIO

**EXPECTED RESULT**: Hardware ready for firmware development.

**HOW TO VERIFY**: All components on desk and Arduino IDE installed.

---

#### 12. Verify Both MPU6050 Addresses

**WHAT I NEED TO DO**: Check I2C addresses of both sensors.

**WHY I NEED TO DO IT**: Sensors must have different addresses or use separate I2C buses.

**EXACT STEPS**:
1. Wire MPU6050 to ESP32
2. Run I2C scanner sketch
3. Note addresses (usually 0x68 or 0x69)

**EXPECTED RESULT**: Both sensors have different addresses or are on separate buses.

**HOW TO VERIFY**: I2C scanner shows two addresses.

---

#### 13. Decide Exact Hand Mounting Position

**WHAT I NEED TO DO**: Determine where to mount the hand sensor.

**WHY I NEED TO DO IT**: Affects sensor orientation and data interpretation.

**EXACT STEPS**:
1. Consider glove vs ring mount
2. Test comfort and stability
3. Document orientation (which axis is up)

**EXPECTED RESULT**: Clear mounting specification.

**HOW TO VERIFY**: Can describe mounting to others.

---

#### 14. Decide Exact Shoe Mounting Position

**WHAT I NEED TO DO**: Determine where to mount the shoe sensor.

**WHY I NEED TO DO IT**: Affects gait detection accuracy.

**EXACT STEPS**:
1. Consider top of foot vs side
2. Test during walking
3. Document orientation

**EXPECTED RESULT**: Clear mounting specification.

**HOW TO VERIFY**: Can describe mounting to others.

---

#### 15. Decide Target Sampling Rate

**WHAT I NEED TO DO**: Choose the actual sampling rate for sensors.

**WHY I NEED TO DO IT**: Affects data quality and battery life.

**EXACT STEPS**:
1. Review literature for similar studies
2. Consider ESP32 capabilities
3. Test with simulator (default: 50 Hz)

**EXPECTED RESULT**: Sampling rate selected (e.g., 50 Hz).

**HOW TO VERIFY**: Documented in project notes.

---

#### 16. Obtain Datasets

**WHAT I NEED TO DO**: Find or create training datasets.

**WHY I NEED TO DO IT**: ML models need labeled data.

**EXACT STEPS**:
1. Search for public Parkinson's datasets
2. Consider PhysioNet, UCI ML Repository
3. Document dataset licenses

**EXPECTED RESULT**: At least one dataset identified.

**HOW TO VERIFY**: Dataset files downloaded and documented.

---

#### 17. Document Dataset Licenses

**WHAT I NEED TO DO**: Record usage rights for all datasets.

**WHY I NEED TO DO IT**: Legal compliance and academic integrity.

**EXACT STEPS**:
1. Read dataset license files
2. Record allowed uses
3. Note attribution requirements

**EXPECTED RESULT**: License documentation complete.

**HOW TO VERIFY**: `datasets/LICENSES.md` file exists.

---

#### 18. Decide Blynk vs Custom App

**WHAT I NEED TO DO**: Choose dashboard technology.

**WHY I NEED TO DO IT**: Affects caregiver interface development.

**EXACT STEPS**:
1. Research Blynk capabilities
2. Consider custom web app
3. Evaluate Flutter for mobile
4. Document decision

**EXPECTED RESULT**: Technology choice made and documented.

**HOW TO VERIFY**: `docs/DASHBOARD_DECISION.md` file exists.

---

## What I Should Do Next

### Immediate: Physical Validation (User Action)

Run the validation protocol with real hardware:

1. **Stationary baseline test** (60 seconds) — verify hand_az ≈ 9.8 m/s²
2. **10-minute stream test** — verify no crashes or data loss
3. **Buzzer interference test** — verify sensor data unaffected
4. **72-hour storage test** — monitor database growth

→ See `docs/REAL_SIGNAL_VALIDATION_PROTOCOL.md`

### Next Development Stage

**Stage 3: Data Collection and Dataset Creation**

- Define recording procedures
- Create patient consent forms
- Record tremor/FOG episodes (if available)
- Label data with clinical assessments

See `docs/NEXT_STEPS.md` for detailed Stage 3 tasks.

---

## Known Limitations

### Current Limitations

1. **No Authentication**: WebSocket connections are open
2. **In-Memory State**: Connection manager loses state on restart
3. **Single Worker**: No multi-worker support
4. **SQLite Write Contention**: Under heavy load (not a concern for single-device)
5. **No Real ML**: Model interfaces raise NotImplementedError
6. **No Clinical Validation**: All thresholds are placeholders
7. **No Blynk/Dashboard**: Caregiver interface is a no-op placeholder

### Medical Disclaimer

**This system is a research prototype.**

- NOT a medical device
- NOT clinically validated
- NOT for diagnosis
- NOT for treatment decisions
- NOT a substitute for professional medical advice

Any resemblance to clinical patterns is for testing purposes only. Do NOT use this system for actual patient monitoring without proper clinical validation and regulatory approval.

---

## Contributing

This is a university research project. For questions or contributions, please contact the project owner.

---

## License

This project is for educational and research purposes. See repository for license details.
