# Tóm Tắt Kế Hoạch Dự Án: Hệ Thống Phát Hiện Hành Vi Bất Thường

## 📊 Tiến Độ Hiện Tại: **Core AI Pipeline 100% Complete**

### ✅ Đã Hoàn Thành Cả 5 Phase:
1. **PHASE 1**: Setup môi trường Python 3.11 + PyTorch CUDA 12.1 + YOLOv8 + GPU RTX 2050
2. **PHASE 2**: YOLOv8-Pose + Camera (`scripts/camera_pose.py`)
3. **PHASE 3**: Tự động tạo dataset keypoints (`scripts/extract_keypoints.py`) - 330 normal + 107 abnormal (437 files .npy)
4. **PHASE 4**: Huấn luyện Custom LSTM (`scripts/train_lstm.py`) - **Best Val Acc: 86.93%** (đạt mục tiêu >85%), đã lưu `models/lstm_best.pt`
5. **PHASE 5**: YOLO + LSTM chạy Realtime (`scripts/realtime.py`) - hỗ trợ cả Webcam và file video test, hiển thị HUD cảnh báo trực quan

### 🚀 Bước Tiếp Theo (Nếu mở rộng):
- Backend API (Flask / FastAPI) & Mobile App / Dashboard nếu cần.

---

## 📅 Timeline 5 Tuần

### 🗓️ Week 1: Model Training & Optimization
**Mục tiêu:** Accuracy > 85%

- **Day 1-2**: Train LSTM model (50 epochs, batch 64)
- **Day 3-4**: Hyperparameter tuning (hidden size, learning rate, sequence length)
- **Day 5**: Model selection, webcam test, record demo video

**Lệnh:**
```bash
cd "D:\word_D\Hệ thống thông minh"
python scripts/train_lstm.py
```

---

### 🗓️ Week 2: Backend Development
**Tech Stack:** Flask + PyTorch + SQLite + WebSocket

- **Day 6-7**: Flask backend setup, API endpoints
- **Day 8-9**: WebSocket for real-time communication
- **Day 10**: Backend testing

**API Endpoints:**
- `POST /api/detect/image` - Detect từ single image
- `POST /api/detect/sequence` - Detect từ sequence frames
- `GET /api/status` - Server status
- `GET /api/history` - Lịch sử detections
- `POST /api/feedback` - User feedback
- `GET /api/stats` - Statistics

**Project Structure:**
```
backend/
├── app.py                    # Flask app chính
├── models/lstm_best.pt       # Trained model
├── utils.py                  # Helper functions
├── model_loader.py          # Model loading
├── database.py              # SQLite operations
└── requirements.txt
```

---

### 🗓️ Week 3: React Native Mobile App
**Tech Stack:** React Native + Camera + WebSocket + Axios

- **Day 11-12**: Project setup, camera integration
- **Day 13-14**: Detection UI & results screens
- **Day 15**: Settings & configuration

**Screens:**
1. **CameraScreen** - Camera + capture/stream
2. **ResultScreen** - Display results (Normal/Abnormal + confidence)
3. **HistoryScreen** - Detection history
4. **StatsScreen** - Statistics dashboard
5. **SettingsScreen** - Configuration

**Lệnh:**
```bash
npx react-native init ClassroomMonitor
cd ClassroomMonitor
npm install react-native-camera react-native-websocket axios
```

---

### 🗓️ Week 4: Advanced Features & Polish
- **Day 16-17**: On-device TFLite model (optional)
- **Day 18-19**: UI/UX improvements, animations
- **Day 20**: Notification system (visual, audio, vibration)

---

### 🗓️ Week 5: Testing, Demo & Presentation
- **Day 21-22**: Integration testing, bug fixes
- **Day 23-24**: Demo preparation, record videos
- **Day 25**: Documentation, presentation slides

---

## 🎯 Weekly Milestones

### ✅ Week 1: Model Complete
- LSTM model trained (accuracy > 85%)
- Real-time detection with webcam
- Demo video recorded

### ✅ Week 2: Backend Complete
- Flask server running locally
- All API endpoints working
- WebSocket real-time communication

### ✅ Week 3: Mobile App MVP
- React Native app captures frames
- App sends frames to server
- App displays detection results

### ✅ Week 4: App Polished
- On-device model integration (optional)
- Nice UI/UX with animations
- Notification system working

### ✅ Week 5: Demo Ready
- End-to-end system working
- Demo videos recorded
- Documentation complete
- Presentation slides ready

---

## 🔧 Tech Stack

### Backend
- Flask (Python web framework)
- PyTorch (Model inference)
- OpenCV (Image processing)
- Flask-SocketIO (WebSocket)
- SQLite (Database)

### Mobile App
- React Native (Cross-platform)
- React Native Camera
- React Native WebSocket
- Axios (HTTP requests)
- React Navigation
- React Native Reanimated

### Optional On-device
- TensorFlow Lite
- react-native-fast-tflite

---

## 📊 Expected Metrics

### Model Performance
- **Accuracy**: > 85%
- **Precision**: > 80% (abnormal class)
- **Recall**: > 80% (abnormal class)
- **F1-Score**: > 80%

### System Performance
- **Detection Latency**: < 2s (cloud), < 500ms (on-device)
- **WebSocket Latency**: < 100ms
- **App Startup Time**: < 3s
- **Battery Impact**: < 10%/hour

---

## 📦 Deliverables

1. **Source Code**
   - Training scripts
   - Backend Flask app
   - React Native mobile app
   - Documentation

2. **Trained Model**
   - `lstm_best.pt` (PyTorch)
   - `lstm_best.tflite` (optional)
   - Evaluation report

3. **Demo**
   - Live demo (if possible)
   - Demo video (5-10 phút)
   - Screenshots

4. **Documentation**
   - README with setup instructions
   - API documentation
   - Architecture diagram
   - User guide

5. **Presentation**
   - 15-20 slides
   - Live demo or video demo
   - Q&A preparation

---

## 🎯 Success Criteria

### Minimum (Grade: B)
- ✅ Model accuracy > 75%
- ✅ Backend API working
- ✅ Mobile app detects & displays results
- ✅ Demo video recorded
- ✅ Basic documentation

### Good (Grade: A-)
- ✅ Model accuracy > 85%
- ✅ Real-time WebSocket working
- ✅ Nice UI/UX
- ✅ Multiple screens complete
- ✅ Good documentation
- ✅ Live demo working

### Excellent (Grade: A)
- ✅ Model accuracy > 90%
- ✅ On-device model integration
- ✅ Notification system
- ✅ Statistics dashboard
- ✅ Excellent documentation
- ✅ Impressive live demo
- ✅ Additional features

---

## 💡 Tips for Success

1. **Start with model training immediately** - Foundation
2. **Test mobile deployment early** - Don't wait until Week 5
3. **Keep backend simple** - Flask > complex frameworks
4. **Focus on demo quality** - Impressive demo = good grade
5. **Document as you go** - Don't leave for last
6. **Have backup plans** - Video demo if live demo fails
7. **Test on real devices** - Emulator ≠ real phone
8. **Prepare for questions** - Know your system inside out

---

## ⚠️ Key Risks

| Risk | Mitigation |
|------|------------|
| Model accuracy < 80% | Collect more data, transfer learning |
| Mobile deployment issues | Use Expo, test early on devices |
| WebSocket unstable | Reconnection logic, HTTP fallback |
| On-device model slow | Quantization, cloud fallback |
| Time overrun | Focus on MVP first, cut non-essential features |

---

## 🚀 Next Immediate Actions

### 1. Train Model (Week 1, Day 1-2)
```bash
cd "D:\word_D\Hệ thống thông minh"
python scripts/train_lstm.py
```

### 2. Test with Webcam
```bash
python scripts/realtime.py
```

### 3. Setup Backend (Week 2, Day 6-7)
```bash
mkdir backend
cd backend
# Copy models/lstm_best.pt vào backend/
pip install flask torch opencv-python numpy flask-socketio
```

### 4. Initialize React Native (Week 3, Day 11-12)
```bash
npx react-native init ClassroomMonitor
cd ClassroomMonitor
npm install react-native-camera react-native-websocket axios
```

---

**Total Timeline: 5 Weeks (25 Days)**
**Current Status: 50% Complete (Data ready, need to train model)**
**Critical Path: Model Training → Backend → Mobile App → Demo**
