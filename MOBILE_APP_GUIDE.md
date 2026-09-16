# Đặc Tả Mobile App

## 1. Mục tiêu ứng dụng

Ứng dụng mobile cho phép người dùng theo dõi hành vi qua camera, gửi dữ liệu đến hệ thống nhận diện và nhận cảnh báo khi phát hiện hành vi bất thường.

Ứng dụng là client của backend inference. Model YOLOv8-Pose + LSTM hiện đang chạy trong Python, vì vậy mobile app không gọi trực tiếp file `.pt`; app sẽ giao tiếp với backend qua REST API hoặc WebSocket.

## 2. Đối tượng sử dụng

- Giáo viên hoặc người giám sát lớp học.
- Nhân viên an ninh hoặc người vận hành camera.
- Người quản trị cần xem lại lịch sử và thống kê cảnh báo.

## 3. Chức năng bắt buộc

### 3.1. Đăng nhập và quản lý phiên

- Đăng nhập bằng tài khoản và mật khẩu.
- Ghi nhớ phiên đăng nhập bằng token an toàn.
- Đăng xuất.
- Hiển thị lỗi rõ ràng khi sai tài khoản, mất mạng hoặc phiên hết hạn.

Nếu giai đoạn MVP chưa có hệ thống tài khoản, có thể dùng màn hình kết nối server thay thế, nhưng phải giữ sẵn cấu trúc để bổ sung xác thực sau này.

### 3.2. Màn hình giám sát realtime

- Xin quyền sử dụng camera trước lần sử dụng đầu tiên.
- Hiển thị hình ảnh camera theo thời gian thực.
- Hiển thị trạng thái kết nối server.
- Gửi frame hoặc chuỗi keypoint đến backend.
- Hiển thị kết quả `Normal` hoặc `Abnormal`.
- Hiển thị confidence và thời điểm nhận kết quả.
- Hiển thị cảnh báo nổi bật khi phát hiện bất thường.
- Có nút bắt đầu/tạm dừng/kết thúc giám sát.
- Có thể chuyển camera trước/sau nếu thiết bị hỗ trợ.
- Có thể bật/tắt âm thanh và rung cảnh báo.
- Có thể chọn threshold cảnh báo trong giới hạn do backend cho phép.

### 3.3. Cảnh báo bất thường

Khi kết quả là `Abnormal`, ứng dụng phải:

- Đổi màu trạng thái sang đỏ hoặc màu cảnh báo đã quy định.
- Hiển thị thông báo ngắn, dễ đọc.
- Phát âm thanh hoặc rung nếu người dùng đã bật tùy chọn.
- Ghi lại thời điểm, confidence và nguồn camera.
- Không tạo hàng trăm thông báo lặp lại cho cùng một sự kiện; cần có khoảng thời gian chống lặp.

### 3.4. Lịch sử phát hiện

- Hiển thị danh sách các lần phát hiện gần đây.
- Mỗi bản ghi gồm thời gian, kết quả, confidence và nguồn camera.
- Lọc theo `Normal`, `Abnormal` và khoảng thời gian.
- Mở chi tiết một bản ghi.
- Cho phép xóa bản ghi nếu backend hỗ trợ quyền này.
- Hiển thị trạng thái danh sách rỗng, đang tải và lỗi tải dữ liệu.

### 3.5. Thống kê

- Tổng số lần phát hiện.
- Số lần bình thường và bất thường.
- Tỷ lệ bất thường.
- Biểu đồ theo ngày hoặc theo khoảng thời gian.
- Thời gian cập nhật dữ liệu gần nhất.
- Hiển thị thông báo khi chưa có đủ dữ liệu thống kê.

### 3.6. Cài đặt

- Cấu hình địa chỉ backend.
- Cấu hình threshold trong khoảng an toàn.
- Bật/tắt âm thanh cảnh báo.
- Bật/tắt rung.
- Chọn khoảng thời gian chống lặp cảnh báo.
- Chọn chất lượng hoặc tốc độ gửi dữ liệu nếu backend hỗ trợ.
- Xem trạng thái server và phiên bản ứng dụng.
- Đăng xuất.

## 4. Cấu trúc màn hình đề xuất

### 4.1. LoginScreen hoặc ConnectScreen

Thành phần:

- Logo/tên ứng dụng.
- Ô tài khoản nếu có đăng nhập.
- Ô mật khẩu nếu có đăng nhập.
- Ô địa chỉ server ở chế độ MVP nếu chưa có auth.
- Nút đăng nhập/kết nối.
- Trạng thái kết nối và thông báo lỗi.

### 4.2. HomeScreen

Home là màn hình chính sau khi kết nối thành công.

- Tóm tắt trạng thái server.
- Nút vào giám sát realtime.
- Số cảnh báo gần đây.
- Tóm tắt nhanh normal/abnormal.
- Truy cập nhanh đến lịch sử và thống kê.

### 4.3. MonitorScreen

Đây là màn hình quan trọng nhất.

- Vùng camera chiếm phần lớn màn hình.
- Nhãn trạng thái luôn nhìn thấy: `NORMAL`, `ABNORMAL`, `CONNECTING` hoặc `ERROR`.
- Confidence hiển thị cạnh trạng thái.
- Nút bắt đầu/tạm dừng/kết thúc đặt ở vùng dễ chạm bằng một tay.
- Thanh hoặc badge hiển thị server connection.
- Không che khuất khuôn mặt hoặc vùng người đang được theo dõi.

### 4.4. HistoryScreen

- Danh sách theo thời gian giảm dần.
- Badge màu cho normal/abnormal.
- Bộ lọc trạng thái và ngày.
- Pull-to-refresh.
- Empty state khi chưa có dữ liệu.

### 4.5. DetectionDetailScreen

- Kết quả phát hiện.
- Confidence.
- Thời gian và nguồn camera.
- Ảnh snapshot hoặc video ngắn nếu backend lưu dữ liệu.
- Ghi chú hoặc trạng thái đã xem nếu nghiệp vụ cần.

### 4.6. StatisticsScreen

- Bộ lọc thời gian.
- Thẻ tổng quan ngắn gọn.
- Biểu đồ dễ đọc.
- Không chỉ dùng màu để phân biệt dữ liệu; cần có nhãn hoặc ký hiệu đi kèm.

### 4.7. SettingsScreen

- Các nhóm cài đặt rõ ràng.
- Toggle cho thiết lập bật/tắt.
- Slider hoặc stepper cho threshold và thời gian chống lặp.
- Nút kiểm tra kết nối server.
- Thông tin phiên bản và nút đăng xuất.

## 5. Yêu cầu giao diện

### 5.1. Nguyên tắc chung

- Giao diện ưu tiên thao tác nhanh, dễ đọc khi đang giám sát.
- Màn hình giám sát phải là trọng tâm, không dùng bố cục mang tính quảng cáo.
- Điều hướng chính nên có tối đa 4 mục: Giám sát, Lịch sử, Thống kê, Cài đặt.
- Các nút thao tác chính phải có icon và nhãn rõ ràng.
- Icon lạ phải có tooltip hoặc nhãn hỗ trợ.
- Không dùng nút chữ quá dài trong vùng thao tác nhỏ.
- Không đặt các card lồng bên trong card khác.

### 5.2. Màu sắc trạng thái

- `Normal`: xanh lá hoặc màu tích cực.
- `Abnormal`: đỏ/cam cảnh báo, tương phản cao.
- `Connecting`: vàng hoặc xanh dương trung tính.
- `Error`: đỏ đậm, kèm thông báo cách xử lý.
- Không chỉ dựa vào màu; luôn kèm chữ, icon hoặc pattern để hỗ trợ người dùng khó phân biệt màu.

### 5.3. Typography và bố cục

- Dùng font dễ đọc, hỗ trợ đầy đủ tiếng Việt.
- Tiêu đề màn hình phải có thứ bậc rõ ràng.
- Text không được tràn khỏi nút, card hoặc vùng hiển thị.
- Khoảng cách chạm tối thiểu nên đạt khoảng 44x44 dp.
- Hỗ trợ màn hình nhỏ và xoay dọc; nội dung chính không bị che bởi camera cutout hoặc thanh điều hướng.
- Kiểm tra cả thiết bị Android nhỏ, Android lớn và iPhone có tai thỏ/Dynamic Island nếu triển khai iOS.

### 5.4. Camera và cảnh báo

- Khung camera giữ tỷ lệ ổn định, không làm layout nhảy khi trạng thái thay đổi.
- Overlay cảnh báo không che toàn bộ hình ảnh.
- Khi mất camera hoặc mất server, phải hiển thị trạng thái thay vì để màn hình trống.
- Khi đang gửi dữ liệu, phải có dấu hiệu hoạt động nhưng không gây nhiễu.

## 6. Trạng thái bắt buộc phải thiết kế

Mỗi màn hình có dữ liệu từ server phải có đủ:

- Loading.
- Loaded có dữ liệu.
- Loaded nhưng rỗng.
- Lỗi mạng.
- Server không phản hồi.
- Phiên đăng nhập hết hạn.
- Không có quyền camera.
- Camera bị ứng dụng khác sử dụng.
- Backend chưa sẵn sàng hoặc model chưa được nạp.

## 7. Luồng sử dụng chính

```text
Mở app
  -> Đăng nhập/kết nối server
  -> Kiểm tra quyền camera
  -> Home
  -> Bắt đầu giám sát
  -> Camera gửi dữ liệu đến backend
  -> Nhận kết quả normal/abnormal
  -> Hiển thị cảnh báo nếu bất thường
  -> Lưu sự kiện vào lịch sử
  -> Xem chi tiết hoặc thống kê
```

## 8. Hợp đồng dữ liệu dự kiến

### Kết quả phát hiện

```json
{
  "label": "abnormal",
  "confidence": 0.86,
  "timestamp": "2026-09-16T10:30:00Z",
  "source": "camera-01",
  "event_id": "evt_123"
}
```

### Trạng thái server

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "lstm_best.pt",
  "model_version": "1.0.0"
}
```

Đây là cấu trúc dự kiến; cần thống nhất chính thức khi xây dựng backend.

## 9. Yêu cầu phi chức năng

- Hiển thị kết quả mới mà không làm treo giao diện.
- Có cơ chế retry khi mất mạng và không gửi request vô hạn.
- Không lưu mật khẩu dạng plain text.
- Token và dữ liệu nhạy cảm phải được lưu bằng cơ chế bảo mật của hệ điều hành.
- Xin quyền camera theo đúng thời điểm người dùng bắt đầu giám sát.
- Có thể tạm dừng gửi dữ liệu khi app chạy nền.
- Tiết kiệm pin bằng cách giới hạn tần suất gửi frame.
- Có log lỗi đủ để chẩn đoán nhưng không ghi thông tin nhạy cảm.
- Hỗ trợ tối thiểu Android trước; iOS là mục tiêu mở rộng nếu có thiết bị kiểm thử.

## 10. Tiêu chí nghiệm thu MVP

- [ ] Người dùng kết nối được app với backend.
- [ ] App xin và xử lý đúng quyền camera.
- [ ] Người dùng bắt đầu và dừng giám sát được.
- [ ] Kết quả normal/abnormal hiển thị trong giao diện.
- [ ] Confidence và thời gian được hiển thị chính xác.
- [ ] Cảnh báo bất thường có màu, icon và text rõ ràng.
- [ ] Có chống lặp cảnh báo.
- [ ] Có lịch sử phát hiện và trạng thái empty/loading/error.
- [ ] Có màn hình cài đặt threshold, âm thanh và rung.
- [ ] App không bị vỡ bố cục trên màn hình nhỏ.
- [ ] Mất mạng và backend lỗi không làm app bị treo.
- [ ] Có kiểm thử luồng chính trên ít nhất một thiết bị Android thật.

## 11. Lộ trình triển khai

1. Chốt API backend và định dạng dữ liệu.
2. Tạo project mobile, navigation và theme giao diện.
3. Làm Connect/Login và kiểm tra trạng thái server.
4. Làm MonitorScreen với camera và mock response.
5. Kết nối MonitorScreen với backend thật.
6. Làm cảnh báo, lịch sử và chi tiết sự kiện.
7. Làm thống kê và cài đặt.
8. Kiểm thử quyền camera, mất mạng, backend lỗi và thiết bị màn hình nhỏ.
9. Đóng gói bản demo và cập nhật README.

## 12. Phạm vi MVP và phần mở rộng

### MVP

- Kết nối backend.
- Camera realtime.
- Hiển thị normal/abnormal và confidence.
- Cảnh báo âm thanh/rung tùy chọn.
- Lịch sử cơ bản.
- Cài đặt threshold.

### Mở rộng sau MVP

- Nhiều camera hoặc nhiều khu vực.
- Tài khoản và phân quyền.
- Đồng bộ cloud.
- Push notification khi app chạy nền.
- Dashboard quản trị.
- On-device inference bằng TFLite.
- Xuất báo cáo CSV/PDF.
