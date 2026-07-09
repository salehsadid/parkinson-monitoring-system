# Architecture Documentation

## Parkinson's Tremor and FOG Monitoring & Cueing System

### System Overview

This system monitors Parkinson's disease symptoms (tremor and Freezing of Gait) using wearable sensors and provides real-time cueing to help patients during FOG episodes.

**Current status**: Stage 2.1 complete — real hardware verified, analysis modules tested, 83 tests passing.

### Hardware Architecture (Real — Verified)

```
+-------------------+     +-------------------+     +-------------------+
|   MPU6050 #1      |     |      ESP32        |     |   MPU6050 #2      |
|   (Hand/Glove)    +----->   Microcontroller  <-----+   (Shoe)          |
|   Tremor Analysis |     |                   |     |   FOG Detection   |
+-------------------+     +--------+----------+     +-------------------+
                                   |
                                   | Wi-Fi
                                   v
                          +-------------------+
                          |    Local PC       |
                          |   (Laptop/PC)    |
                          +-------------------+
                                   |
                                   v
                          +-------------------+
                          |  SQLite Database  |
                          |  (Local Storage)  |
                          +-------------------+
                                   |
                                   v
                          +-------------------+
                          |   Dashboard       |
                          |  (Future: Blynk)  |
                          +-------------------+
```

### Software Architecture

```
+----------------------------------------------------------------------------------+
|                              PC Backend (Python/FastAPI)                          |
+----------------------------------------------------------------------------------+
|                                                                                  |
|  +------------------+  +------------------+  +------------------+                |
|  |  REST API        |  |  WebSocket       |  |  ML Inference    |                |
|  |  /health         |  |  /ws/device/{id} |  |  (Future)        |                |
|  +------------------+  +------------------+  +------------------+                |
|           |                    |                    |                            |
|           v                    v                    v                            |
|  +------------------+  +------------------+  +------------------+                |
|  |  Pydantic        |  |  Connection      |  |  Model           |                |
|  |  Schemas (v2)    |  |  Manager         |  |  Interfaces      |                |
|  +------------------+  +------------------+  +------------------+                |
|           |                    |                    |                            |
|           v                    v                    v                            |
|  +------------------+  +------------------+  +------------------+                |
|  |  Database        |  |  Cue Service     |  |  Analysis        |                |
|  |  (SQLite/SQLAlch)|  |  (FOG Cueing)    |  |  (Stage 2.1)     |                |
|  +------------------+  +------------------+  +------------------+                |
|           |                    |                    |                            |
|           v                    v                    v                            |
|  +------------------+  +------------------+  +------------------+                |
|  |  Retention       |  |  Processing      |  |  Session         |                |
|  |  Service         |  |  Interfaces      |  |  Metadata        |                |
|  +------------------+  +------------------+  +------------------+                |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

### Analysis Modules (Stage 2.1)

```
pc_backend/app/analysis/
├── __init__.py
├── stream_quality.py      # Sampling rate, packet loss, jitter, session segmentation
├── signal_quality.py      # Baseline stats, magnitude, independence checks
├── storage_analysis.py    # Growth projections, 72-hour feasibility
└── session_analysis.py    # Session metadata CRUD, sidecar JSON files
```

### Bidirectional Communication Flow

#### ESP32 → PC (Sensor Data)

```
1. ESP32 reads both MPU6050 sensors
2. ESP32 packages data into JSON packet
3. ESP32 sends packet via WebSocket
4. PC backend receives packet
5. PC validates packet using Pydantic
6. PC stores valid packet in SQLite
7. PC logs malformed packets
```

#### PC → ESP32 (Commands)

```
1. ML model detects FOG event (future)
2. PC creates FOG_CUE_ON command
3. PC sends command via WebSocket
4. ESP32 receives command
5. ESP32 activates buzzer with rhythmic pattern
6. FOG event is logged in database
7. FOG event is shown in dashboard (future)
```

### FOG Cue Loop

```
+-------------------+     +-------------------+     +-------------------+
|  Shoe Sensor      |     |  FOG Detection    |     |  Buzzer Cueing    |
|  (IMU Data)       +----->  Model (Future)   +----->  (ESP32)          |
+-------------------+     +-------------------+     +-------------------+
        ^                                                   |
        |                                                   |
        +---------------------------------------------------+
                    Feedback Loop (Optional)
```

### Database Role

- **Patient Records**: Store patient metadata
- **Device Records**: Track ESP32 devices and their association with patients
- **Sensor Records**: Store raw IMU readings (72-hour rolling window)
- **FOG Events**: Store detected FOG events (preserved longer)
- **Tremor Results**: Store tremor analysis results (preserved longer)

### Dashboard Role

- **Real-time Monitoring**: Display current sensor data and status
- **Event History**: Show historical FOG events and tremor results
- **Caregiver Notifications**: Alert caregivers during FOG episodes (future)
- **Data Visualization**: Charts and graphs for clinical review (future)

### Data Flow Diagram

```
+-------------+    +-------------+    +-------------+    +-------------+
|   ESP32     |    |   FastAPI   |    |   SQLite    |    |  Dashboard  |
|  (Sensor)   +--->+  (Backend)  +--->+  (Database) +--->+  (Future)   |
+-------------+    +------+------+    +-------------+    +-------------+
                          |
                          | Commands
                          v
                     +-------------+
                     |   ESP32     |
                     |  (Buzzer)   |
                     +-------------+
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | FastAPI | REST API and WebSocket server |
| Database | SQLite | Local data storage |
| ORM | SQLAlchemy | Database abstraction |
| Validation | Pydantic v2 | Data validation and serialization (ConfigDict) |
| WebSocket | FastAPI WebSocket | Real-time communication |
| Analysis | Python stdlib (math, statistics) | Stream/signal quality analysis |
| Visualization | matplotlib | Live signal plotting |
| ML | scikit-learn | Future ML inference |
| Testing | pytest | Unit and integration tests (83 tests) |

### Security Considerations

**Stage 1 Limitations:**
- No authentication (WebSocket connections are open)
- No encryption (plain WebSocket)
- No rate limiting
- No input sanitization beyond Pydantic validation

**Future Enhancements:**
- JWT-based authentication
- WSS (WebSocket Secure)
- Rate limiting
- API key management
- Patient data encryption

### Scalability Considerations

**Stage 1 Assumptions:**
- Single PC backend instance
- In-memory connection management
- SQLite for local storage
- Single patient monitoring

**Future Enhancements:**
- Redis for multi-worker support
- PostgreSQL for production
- Multi-patient support
- Cloud deployment option
- Load balancing

### Performance Considerations

**Stage 1 Baseline:**
- WebSocket connections: ~100 concurrent (theoretical)
- Sensor packet processing: ~1000 packets/second
- Database writes: ~500 records/second
- Latency: <10ms for local processing

**Bottlenecks:**
- SQLite write contention under heavy load
- In-memory connection state limits
- Single-threaded ML inference (future)

### Monitoring and Observability

**Stage 1 Logging:**
- Application logs (INFO level)
- Database operations
- WebSocket connections/disconnections
- Malformed packet warnings

**Future Enhancements:**
- Prometheus metrics
- Grafana dashboards
- Distributed tracing
- Alerting system

### Deployment Architecture

**Development:**
- Local PC running FastAPI
- SQLite file in project directory
- Simulator for testing

**Production (Future):**
- Dedicated server or cloud instance
- Docker containerization
- Reverse proxy (nginx)
- SSL/TLS certificates
- Automated backups
