# Hướng dẫn thêm dataset mới vào dự án

Tài liệu này mô tả các yêu cầu bắt buộc, các lưu ý quan trọng và quy trình chuẩn hóa khi thêm dataset mới vào mô hình phát hiện bất thường bằng pose-based LSTM.

## 1. Mục tiêu

Dataset mới cần được chuyển về cùng định dạng với dataset hiện tại để có thể train cùng nhau mà không làm sai lệch mô hình.

Dự án hiện tại yêu cầu:

- dữ liệu ở dạng file `.npy`
- mỗi file chứa chuỗi pose sequence
- mỗi sequence có shape: `(N, 30, 51)`
- `30` = số frame trong 1 chuỗi
- `51` = 17 keypoints × 3 giá trị = `(x, y, confidence)`
- nhãn phải là:
  - `0` = normal
  - `1` = abnormal

---

## 2. Yêu cầu bắt buộc của dataset mới

### 2.1. Định dạng đầu vào

Dataset mới phải đảm bảo các điều kiện sau:

- Mỗi sample là một chuỗi frames 30 frame liên tiếp
- Mỗi frame phải có 51 giá trị
- Kiểu dữ liệu nên là `float32`
- Shape chuẩn: `(30, 51)` cho mỗi chuỗi
- Nếu dataset là video gốc thì cần trích xuất keypoint trước

### 2.2. Thư mục lưu trữ

Dự án hiện tại đọc dữ liệu theo cách sau:

```text
dataset/
  normal/
  abnormal/
```

Do đó, khi thêm dataset mới, cần lưu đúng vào các thư mục tương ứng:

```text
dataset/
  normal/
    <file_1.npy>
    <file_2.npy>
  abnormal/
    <file_1.npy>
    <file_2.npy>
```

### 2.3. Bản chất của nhãn

Mỗi file `.npy` phải tương ứng với một class rõ ràng:

- `normal`: hành vi bình thường
- `abnormal`: hành vi bất thường / nguy hiểm / vi phạm

Nếu dataset mới dùng nhãn khác, cần map lại trước khi đưa vào dự án:

- violent → abnormal
- non-violent → normal
- fighting → abnormal
- normal / safe → normal

### 2.4. Cùng cách chuẩn hóa pose

Nếu trích xuất từ video, dữ liệu phải có cùng cách chuẩn hóa như hiện tại:

- x được chuẩn hóa theo bề rộng frame
- y được chuẩn hóa theo chiều cao frame
- tọa độ trong khoảng gần `[0,1]`
- confidence keypoint phải ở khoảng `[0,1]`

Nếu không chuẩn hóa tương tự, model sẽ học sai và hiệu năng sẽ giảm đáng kể.

---

## 3. Các dạng dataset có thể thêm

### 3.1. Dataset video gốc

Ví dụ: video clip hành vi bất thường hoặc bình thường.

Yêu cầu:

- chuyển về dạng keypoint using YOLOv8-Pose
- lưu lại thành `.npy`
- đặt đúng thư mục `normal/` hoặc `abnormal/`

### 3.2. Dataset đã ở dạng `.npy`

Nếu dataset mới đã có sẵn keypoint sequence, chỉ cần đảm bảo:

- shape đúng
- label đúng
- không bị lệch class
- không có file lỗi hoặc file rỗng

### 3.3. Dataset có cùng task nhưng khác camera / góc quay

Có thể dùng được nếu được chuẩn hóa tốt, nhưng cần lưu ý:

- camera khác có thể tạo sai lệch dữ liệu
- góc quay khác có thể làm mờ phân biệt giữa normal và abnormal
- nên test trước trên validation set

---

## 4. Các lưu ý quan trọng khi thêm dataset mới

### 4.1. Không nên trộn dataset khác schema

Nếu dataset mới không đúng `shape = (30, 51)` hoặc không cùng định dạng pose, bạn sẽ gặp lỗi như:

- mismatch tensor shape
- train lỗi runtime
- accuracy kém hoặc không ổn định
- model học sai nhãn

### 4.2. Cần kiểm tra class imbalance

Nếu dataset mới quá mất cân bằng giữa normal và abnormal, mô hình dễ bị thiên lệch.

Ví dụ:

- normal quá nhiều
- abnormal quá ít

Khi đó cần:

- cân bằng dữ liệu
- chỉnh `class_weights` trong train
- hoặc random sampling khi merge dataset

### 4.3. Không nên dùng video không có người

Vì mô hình đang dựa trên keypoint người, các video không có người hoặc cực khó detect sẽ tạo ra vector zero / nhiễu.

Khi đó:

- nên loại bỏ clip không có người
- hoặc giữ nhưng kiểm tra kỹ phần detect pose

### 4.4. Dữ liệu phải thống nhất về chất lượng

Ví dụ:

- video mờ
- người bị che khuất nhiều
- camera quá xa
- góc quay rất lệch

Đều có thể làm giảm độ tin cậy của dataset mới.

### 4.5. Dữ liệu cần được chia rõ train/val

Không nên thêm toàn bộ dataset mới vào tập train mà không kiểm tra kết quả trên validation.

Nên làm:

- train trên dataset gốc + dataset mới
- đánh giá trên val set
- so sánh với baseline cũ

---

## 5. Quy trình khuyến nghị khi thêm dataset mới

### Bước 1: Kiểm tra định dạng

- file video hay `.npy` ?
- nếu là video, cần chạy YOLOv8-Pose
- nếu là `.npy`, kiểm tra shape và nhãn

### Bước 2: Gán nhãn đúng

```text
normal  -> 0
abnormal -> 1
```

### Bước 3: Đặt vào đúng thư mục

```text
dataset/normal/
dataset/abnormal/
```

### Bước 4: Kiểm tra một vài sample đầu

```python
import numpy as np
arr = np.load('dataset/normal/xxx.npy')
print(arr.shape)
print(arr.dtype)
```

### Bước 5: Train thử

```powershell
python scripts/train_lstm.py
```

### Bước 6: So sánh kết quả

- so với model cũ
- kiểm tra val accuracy
- kiểm tra loss
- kiểm tra precision/recall nếu có

---

## 6. Gợi ý cho dataset baru như xd-violence

Nếu bạn muốn dùng dataset `xd-violence`, cần làm thêm các bước sau:

- chỉ chọn clip có người rõ và hành vi rõ ràng
- map nhãn sang `normal/abnormal`
- trích xuất keypoint bằng YOLOv8-Pose
- lưu dưới dạng `.npy` để phù hợp với mô hình hiện tại
- cân bằng số lượng giữa 2 lớp
- train thử trước khi merge tất cả dữ liệu

---

## 7. Checklist cuối cùng

Trước khi thêm dataset mới, hãy xác nhận:

- [ ] dữ liệu có cùng format pose `(30, 51)`
- [ ] label đúng là `normal` hoặc `abnormal`
- [ ] file `.npy` được lưu trong đúng thư mục
- [ ] không có dữ liệu rỗng hoặc sai format
- [ ] không có imbalance quá lớn
- [ ] đã kiểm tra vài sample bằng tay
- [ ] đã train thử trên validation trước khi full train

---

## 8. Kết luận

Dataset mới có thể được thêm vào dự án nếu bạn chuẩn hóa đúng định dạng và nhãn. Điều quan trọng nhất là không bỏ qua bước kiểm tra định dạng và kiểm tra chất lượng dữ liệu, vì mô hình hiện tại học trên pose sequence và rất nhạy với sai lệch trong dữ liệu.

Nếu muốn, bạn có thể tiếp tục với 1 trong các bước sau:

1. tạo script tự động merge dataset mới vào `dataset/normal` và `dataset/abnormal`
2. tạo script chuẩn hóa từ dataset video gốc sang dataset `.npy`
3. viết hướng dẫn riêng cho dataset `xd-violence`
