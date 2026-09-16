# Tóm Tắt Tiến Độ Dự Án: Hệ Thống Phát Hiện Hành Vi Bất Thường

**Cập nhật lần cuối:** 16/09/2026

## Trạng thái hiện tại

### Hoàn thành: Core AI pipeline

- Môi trường Python và dependencies đã được khai báo trong `requirements.txt`.
- YOLOv8-Pose đã được tích hợp để trích xuất 17 keypoint người trong `scripts/camera_pose.py` và `scripts/extract_keypoints.py`.
- Dataset đã được chuẩn bị: `330` file keypoint normal, `107` file keypoint abnormal, cùng `437` video đầu vào tương ứng.
- LSTM đã được huấn luyện bằng `scripts/train_lstm.py` với chuỗi 30 frame, 51 đặc trưng/frame, hidden size 128 và 2 layer.
- Kết quả tốt nhất đã lưu tại `models/lstm_best.pt`: validation accuracy **86.93%**. Checkpoint cuối nằm tại `models/lstm_last.pt`.
- Nhận diện realtime đã có trong `scripts/realtime.py`, hỗ trợ webcam, video file, threshold, loop, pause, snapshot và lưu video.
- `README.md` đã có hướng dẫn cài đặt, chuẩn bị dataset, train và chạy demo.

### Chưa thực hiện

- Chưa có backend Flask/FastAPI, REST API, database hoặc WebSocket.
- Chưa có React Native/mobile app hoặc dashboard web.
- Chưa có chuyển đổi TensorFlow Lite/on-device inference.
- Chưa có báo cáo precision, recall, F1 theo từng class hoặc benchmark latency chính thức.
- Chưa có bộ test tự động và chưa xác nhận demo video/presentation chính thức.

**Đánh giá tổng thể:** Core AI pipeline đã hoàn thành; sản phẩm tích hợp backend/mobile và các deliverable trình bày vẫn chưa bắt đầu.

## Kế hoạch tiếp theo

### Phase 1: Hoàn tất và kiểm thử model - Đã hoàn thành

- Dataset keypoint đã được tạo từ video.
- LSTM đã train 50 epoch; accuracy validation tốt nhất đạt 86.93%.
- Pipeline YOLO + LSTM đã chạy được với webcam và video file.

### Phase 2: Backend API - Chưa bắt đầu

**Mục tiêu:** Tách inference thành service có API để client khác sử dụng.

- [ ] Tạo backend Flask hoặc FastAPI và nạp `models/lstm_best.pt`.
- [ ] Thêm endpoint phát hiện từ sequence và endpoint health/status.
- [ ] Thêm lưu lịch sử và thống kê nếu cần.
- [ ] Bổ sung WebSocket chỉ khi yêu cầu realtime từ client.

**API dự kiến:**

- `POST /api/detect/sequence` - Phân loại chuỗi keypoint.
- `GET /api/status` - Kiểm tra server và model.
- `GET /api/history` - Lịch sử detections nếu dùng database.
- `GET /api/stats` - Thống kê nếu cần.

### Phase 3: Client mobile/dashboard - Chưa bắt đầu

- [ ] Chọn React Native mobile hoặc dashboard web sau khi backend ổn định.
- [ ] Tích hợp camera và hiển thị kết quả normal/abnormal cùng confidence.
- [ ] Thêm lịch sử, thống kê và cấu hình threshold.

### Phase 4: Tối ưu và tính năng nâng cao - Chưa bắt đầu

- [ ] Đo latency và độ ổn định trên webcam/video dài.
- [ ] Tính precision, recall, F1 và confusion matrix trên tập đánh giá cố định.
- [ ] Cân nhắc TFLite/on-device inference nếu có yêu cầu triển khai mobile.
- [ ] Bổ sung cảnh báo âm thanh/hình ảnh sau khi client đã có.

### Phase 5: Kiểm thử và bàn giao - Chưa bắt đầu

- [ ] Viết smoke test cho việc load model, đọc dataset và inference.
- [ ] Kiểm thử end-to-end sau khi backend/client hoàn thành.
- [ ] Quay demo, chụp màn hình và hoàn thiện slide.

## Các mốc đã đạt và còn lại

### Đã đạt

- [x] Model validation accuracy vượt mục tiêu 85%.
- [x] Realtime inference hoạt động với webcam và video file.
- [x] Có model checkpoint và README hướng dẫn chạy pipeline.

### Còn lại

- [ ] Backend API, client mobile/dashboard và WebSocket.
- [ ] On-device model, notification và UI nâng cao.
- [ ] Demo video, test tự động, báo cáo metric đầy đủ và presentation.

## Công nghệ đang sử dụng

- Python, PyTorch, OpenCV và Ultralytics YOLOv8-Pose.
- NumPy, tqdm và các package trong `requirements.txt`.
- Backend/mobile/TFLite chỉ là công nghệ dự kiến, chưa có trong repository.

## Chỉ số hiện có và cần bổ sung

- **Validation accuracy:** 86.93%.
- **Precision/Recall/F1:** chưa được tính trong pipeline hiện tại.
- **Latency/WebSocket/Battery:** chưa benchmark.

## Deliverables

- **Đã có:** source code xử lý dataset, trích xuất keypoint, train LSTM, realtime inference, README, `models/lstm_best.pt` và `models/lstm_last.pt`.
- **Cần bổ sung:** backend API, mobile/dashboard, file `.tflite` nếu cần, evaluation report, demo video, screenshots, architecture diagram và presentation.

## Tiêu chí hoàn thành tiếp theo

- [x] Model validation accuracy > 85%.
- [x] Realtime inference từ webcam/video file.
- [x] README và script chạy được.
- [ ] Backend API và kiểm thử API.
- [ ] Client hiển thị kết quả.
- [ ] Báo cáo metric đầy đủ và demo end-to-end.

## Rủi ro hiện tại

| Rủi ro | Hướng xử lý |
|---|---|
| Validation accuracy chưa phản ánh tốt từng class | Tính thêm precision, recall, F1 và confusion matrix |
| Chưa có API/client | Làm backend tối thiểu trước, sau đó mới tích hợp UI |
| Inference realtime phụ thuộc thiết bị | Benchmark CPU/GPU và đặt threshold phù hợp |
| Dataset mất cân bằng | Giữ class weights và theo dõi metric abnormal riêng |

## Việc cần làm tiếp theo

### 1. Kiểm tra pipeline hiện tại

```powershell
python scripts/realtime.py
```

### 2. Đo metric và tạo báo cáo đánh giá

Bổ sung precision, recall, F1 và confusion matrix trên tập validation/test cố định.

### 3. Tạo backend tối thiểu

Tạo service inference, nạp `models/lstm_best.pt`, sau đó kiểm thử endpoint sequence trước khi xây dựng client.
