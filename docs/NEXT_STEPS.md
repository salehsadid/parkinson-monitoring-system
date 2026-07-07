# Next Steps

## Parkinson's Tremor and FOG Monitoring & Cueing System

### Stage 2: Real ESP32 Firmware

#### Objective
Implement actual ESP32 firmware that reads dual MPU6050 sensors and communicates with the PC backend.

#### Hardware Requirements
- ESP32 development board (e.g., ESP32-DevKitC)
- 2x MPU6050 breakout boards
- Buzzer (active or passive)
- Jumper wires
- Breadboard
- USB cable for programming

#### Tasks

**2.1 Basic MPU6050 Reading**
- [ ] Wire MPU6050 #1 (hand) to ESP32 I2C (SDA=21, SCL=22)
- [ ] Wire MPU6050 #2 (shoe) to ESP32 I2C (SDA=16, SCL=17)
- [ ] Use separate I2C buses for each sensor
- [ ] Configure MPU6050 at 50 Hz sampling rate
- [ ] Read all 6 axes from both sensors
- [ ] Verify data accuracy with serial monitor

**2.2 Wi-Fi Connectivity**
- [ ] Configure ESP32 Wi-Fi credentials
- [ ] Implement reconnection logic
- [ ] Add connection status LED indicator

**2.3 WebSocket Client**
- [ ] Implement WebSocket client on ESP32
- [ ] Connect to PC backend at `ws://{PC_IP}:8000/ws/device/{device_id}`
- [ ] Send sensor packets at 50 Hz
- [ ] Implement JSON serialization
- [ ] Handle connection drops gracefully

**2.4 Command Reception**
- [ ] Listen for commands from PC
- [ ] Parse FOG_CUE_ON command
- [ ] Parse FOG_CUE_OFF command
- [ ] Implement command acknowledgment

**2.5 Buzzer Control**
- [ ] Wire buzzer to ESP32 GPIO (e.g., GPIO 25)
- [ ] Implement non-blocking buzzer control
- [ ] Create rhythmic cueing pattern (tik-tik-tik)
- [ ] Test buzzer activation/deactivation

**2.6 Integration Testing**
- [ ] Test with PC backend running
- [ ] Verify sensor data reception in database
- [ ] Test FOG cue command flow
- [ ] Monitor for stability over 1 hour

#### Resources
- [Arduino MPU6050 Tutorial](https://randomnerdtutorials.com/esp32-mpu-6050-accelerometer-gyroscope-arduino/)
- [ESP32 WebSocket Client](https://github.com/Links204/arduinoWebSockets)
- [ESP32 I2C Multiple Devices](https://randomnerdtutorials.com/esp32-i2c-communication-arduino-ide/)

---

### Stage 3: Data Collection and Dataset Creation

#### Objective
Collect real sensor data from Parkinson's patients to create training datasets.

#### Requirements
- IRB approval (if applicable)
- Patient consent forms
- Multiple patients (target: 10+)
- Recording sessions (target: 30+ minutes each)

#### Tasks

**3.1 Data Collection Protocol**
- [ ] Define recording procedures
- [ ] Create patient consent forms
- [ ] Establish data storage policy
- [ ] Document sensor placement procedure

**3.2 Data Collection**
- [ ] Record baseline (no tremor, normal gait)
- [ ] Record tremor episodes (if available)
- [ ] Record FOG episodes (if available)
- [ ] Record medication ON/OFF states
- [ ] Label data with clinical assessments

**3.3 Dataset Organization**
- [ ] Organize data by patient
- [ ] Create metadata files (CSV/JSON)
- [ ] Document data collection conditions
- [ ] Store raw data in `data/raw/`

**3.4 Data Quality**
- [ ] Check for missing data
- [ ] Identify sensor artifacts
- [ ] Validate sampling rate consistency
- [ ] Document any issues

#### Deliverables
- Raw sensor data files
- Patient metadata CSV
- Data collection log
- Quality assessment report

---

### Stage 4: Signal Processing and Feature Engineering

#### Objective
Develop preprocessing pipelines and extract meaningful features for ML models.

#### Tasks

**4.1 Signal Preprocessing**
- [ ] Implement low-pass filter (Butterworth)
- [ ] Remove gravity component from acceleration
- [ ] Normalize signals
- [ ] Handle missing data

**4.2 Feature Extraction - Hand (Tremor)**
- [ ] Time-domain features (RMS, peak, std dev)
- [ ] Frequency-domain features (FFT, dominant frequency)
- [ ] Windowing (1-2 second windows)
- [ ] Feature normalization

**4.3 Feature Extraction - Shoe (FOG)**
- [ ] Gait cadence estimation
- [ ] Step detection
- [ ] Symmetry metrics
- [ ] Frequency analysis

**4.4 Feature Validation**
- [ ] Visualize feature distributions
- [ ] Check for class separability
- [ ] Remove redundant features
- [ ] Document feature meanings

#### Deliverables
- Preprocessing pipeline code
- Feature extraction code
- Feature documentation
- Feature visualization plots

---

### Stage 5: ML Model Development

#### Objective
Train and validate ML models for tremor classification and FOG detection.

#### Tasks

**5.1 Tremor Classification Model**
- [ ] Define classification labels (no_tremor, mild, moderate, severe)
- [ ] Split data into train/validation/test
- [ ] Train Random Forest classifier
- [ ] Train SVM classifier
- [ ] Compare model performance
- [ ] Select best model
- [ ] Save model to `ml/saved_models/`

**5.2 FOG Detection Model**
- [ ] Define binary classification (FOG/not_FOG)
- [ ] Handle class imbalance (if any)
- [ ] Train classifier
- [ ] Optimize for recall (minimize false negatives)
- [ ] Validate on held-out data
- [ ] Save model to `ml/saved_models/`

**5.3 Model Evaluation**
- [ ] Compute accuracy, precision, recall, F1
- [ ] Generate confusion matrices
- [ ] Analyze misclassifications
- [ ] Document model limitations

**5.4 Model Integration**
- [ ] Implement model loading in `inference/interfaces.py`
- [ ] Integrate with WebSocket endpoint
- [ ] Test end-to-end flow
- [ ] Measure inference latency

#### Deliverables
- Trained model files (.joblib)
- Model evaluation reports
- Model documentation
- Integration code

---

### Stage 6: Dashboard and Caregiver Interface

#### Objective
Create a caregiver-facing dashboard for monitoring patients.

#### Tasks

**6.1 Dashboard Technology Selection**
- [ ] Evaluate Blynk vs custom web app
- [ ] Consider Flutter for mobile
- [ ] Document decision

**6.2 Dashboard Implementation**
- [ ] Implement device status display
- [ ] Show real-time sensor data (optional)
- [ ] Display FOG event history
- [ ] Show tremor analysis results
- [ ] Add caregiver notifications

**6.3 Integration**
- [ ] Connect dashboard to PC backend
- [ ] Test real-time updates
- [ ] Verify notification delivery

#### Deliverables
- Dashboard application
- Integration documentation
- User guide

---

### Stage 7: Clinical Validation

#### Objective
Validate the system with clinical experts and patients.

#### Tasks

**7.1 Clinical Review**
- [ ] Present system to neurologists
- [ ] Gather feedback on usability
- [ ] Identify clinical requirements

**7.2 Validation Study**
- [ ] Design validation protocol
- [ ] Recruit participants
- [ ] Conduct testing sessions
- [ ] Collect ground truth data

**7.3 Performance Evaluation**
- [ ] Compare with clinical assessments
- [ ] Calculate sensitivity/specificity
- [ ] Document limitations
- [ ] Iterate based on feedback

#### Deliverables
- Clinical validation report
- Performance metrics
- Recommendations for improvement

---

### Manual Actions Required

#### From You (Human Developer)

**Hardware Setup**
1. Purchase ESP32 and MPU6050 sensors
2. Set up development environment (Arduino IDE or PlatformIO)
3. Wire and test basic sensor reading
4. Document sensor placement on patient

**Dataset Acquisition**
1. Obtain IRB approval (if required)
2. Create patient consent forms
3. Recruit patients for data collection
4. Record sensor data during clinical sessions
5. Label data with clinical assessments

**Clinical Collaboration**
1. Connect with neurologists for guidance
2. Define tremor severity labels
3. Validate FOG detection criteria
4. Review system with clinical experts

**ML Development**
1. Decide on classification labels
2. Choose evaluation metrics
3. Validate model performance
4. Document model limitations

**Dashboard Decisions**
1. Choose between Blynk and custom app
2. Define notification requirements
3. Design user interface
4. Test with caregivers

---

### Timeline Estimate

| Stage | Duration | Dependencies |
|-------|----------|--------------|
| Stage 2 | 2-3 weeks | ESP32 hardware |
| Stage 3 | 4-6 weeks | IRB approval, patients |
| Stage 4 | 2-3 weeks | Stage 3 complete |
| Stage 5 | 3-4 weeks | Stage 4 complete |
| Stage 6 | 2-3 weeks | Stage 5 complete |
| Stage 7 | 4-6 weeks | Clinical partners |
| **Total** | **17-25 weeks** | |

---

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Insufficient patient data | Start with public datasets if available |
| Poor model performance | Iterate on features and algorithms |
| Hardware compatibility issues | Test with multiple MPU6050 units |
| Clinical validation delays | Begin with synthetic testing |
| Dashboard complexity | Start with simple web interface |

---

### Success Criteria

**Stage 2 Success:**
- ESP32 reads both MPU6050 sensors
- Data received in PC database
- Buzzer responds to FOG commands

**Stage 5 Success:**
- Tremor classifier achieves >80% accuracy
- FOG detector achieves >90% recall
- Inference latency <100ms

**Overall Success:**
- System works end-to-end with real sensors
- Clinical experts validate approach
- Caregivers find dashboard useful
