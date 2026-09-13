# Phat hien hanh vi bat thuong

Du an su dung YOLOv8-Pose de trich xuat 17 diem khop nguoi, sau do dung mo hinh LSTM de phan loai chuoi 30 frame thanh `normal` hoac `abnormal`.

## 1. Yeu cau

- Windows 10/11 hoac Linux
- Python 3.10 hoac 3.11
- Webcam neu muon chay realtime
- GPU NVIDIA va CUDA la tuy chon, nhung duoc khuyen nghi khi trich xuat keypoint va train
- Khoang trong dia cung lon khi giai nen dataset ShanghaiTech

## 2. Tai ve

### Da co trong repository

Khong can tai lai cac file sau:

```text
yolov8n-pose.pt
models/lstm_best.pt
models/lstm_last.pt
requirements.txt
```

### Can tu tai

Dataset video khong duoc commit len GitHub vi kich thuoc rat lon. Hay tai bo **ShanghaiTech Campus Dataset** tu trang du an:

- Trang dataset: <https://www.svcl.ucsd.edu/projects/shanghaitech/>

Dat file dataset vao thu muc goc cua du an va doi ten thanh:

```text
OneDrive_2_9-8-2026.zip
```

`setup_dataset.py` dang cho archive nay chua cac phan `shanghaitech.tar.gz.*`. Neu ban tai mot goi co ten hoac cau truc khac, can doi ten/dieu chinh script truoc khi chay.

Neu can tai lai model YOLO, co the dung ban Pose nho:

- <https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n-pose.pt>

## 3. Cai dat

Mo PowerShell tai thu muc du an:

```powershell
git clone https://github.com/tuannguyen-cell/Reconnaissance-system-detects-anomalous-behavior.git
cd Reconnaissance-system-detects-anomalous-behavior

python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Neu PowerShell chan kich hoat moi truong:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

Voi Linux/macOS, lenh kich hoat la:

```bash
source venv/bin/activate
```

## 4. Chuan bi dataset

Dat `OneDrive_2_9-8-2026.zip` vao thu muc goc, sau do chay:

```powershell
python scripts/setup_dataset.py
```

Script se tao cac thu muc video va annotation:

```text
videos/
  normal/
  abnormal/
dataset/
  annotations/
```

Dataset va video nam trong `.gitignore`, khong bi day len GitHub.

## 5. Trich xuat keypoint

Tao file `.npy` tu video:

```powershell
python scripts/extract_keypoints.py
```

Tiep tuc bo qua video da xu ly neu qua trinh bi gian doan:

```powershell
python scripts/extract_keypoints.py --resume
```

Chi xu ly mot so luong video de kiem tra:

```powershell
python scripts/extract_keypoints.py --limit 5
```

Ket qua duoc luu tai:

```text
dataset/normal/*.npy
dataset/abnormal/*.npy
```

## 6. Train LSTM

Sau khi co dataset keypoint:

```powershell
python scripts/train_lstm.py
```

Tuy chinh tham so, vi du:

```powershell
python scripts/train_lstm.py --epochs 50 --batch 64 --lr 0.001 --hidden 128
```

Model duoc luu vao `models/lstm_best.pt` va `models/lstm_last.pt`.

## 7. Chay nhan dien

### Webcam

```powershell
python scripts/realtime.py
```

### File video

```powershell
python scripts/realtime.py --video videos/abnormal/01_0051.avi
```

### Tuy chinh nguong canh bao

```powershell
python scripts/realtime.py --video videos/abnormal/01_0051.avi --threshold 0.6 --no-loop
```

Phim dieu khien trong cua so video:

- `q` hoac `Esc`: thoat
- `p`: tam dung/tiep tuc
- `s`: chup snapshot

Video dau ra duoc ghi khi them tuy chon `--save`.

## 8. Demo YOLO Pose

Neu chi muon kiem tra webcam va skeleton, khong dung LSTM:

```powershell
python scripts/camera_pose.py
```

Mot so tuy chon:

```powershell
python scripts/camera_pose.py --camera 0 --conf 0.5 --width 1280 --height 720 --save
```

## 9. Cau truc project

```text
.
|-- models/                  # Mo hinh LSTM da train
|-- scripts/
|   |-- setup_dataset.py     # Giai nen dataset
|   |-- extract_keypoints.py # Video -> keypoint .npy
|   |-- train_lstm.py        # Train bo phan loai LSTM
|   |-- realtime.py          # YOLO + LSTM realtime
|   `-- camera_pose.py       # Demo YOLO Pose
|-- yolov8n-pose.pt          # Mo hinh YOLOv8 Pose
|-- requirements.txt
`-- PROJECT_PLAN_SUMMARY.md
```

## 10. Xu ly loi thuong gap

- **Khong tim thay `yolov8n-pose.pt`**: dat file model vao thu muc goc project.
- **Khong tim thay `models/lstm_best.pt`**: train model bang `python scripts/train_lstm.py` hoac dat model da train vao thu muc `models/`.
- **Khong tim thay `OneDrive_2_9-8-2026.zip`**: dat dung ten file vao thu muc goc project.
- **Khong tim thay webcam**: thu `--camera 1` hoac dong ung dung dang su dung camera.
- **CUDA khong kha dung**: chuong trinh tu dong chuyen sang CPU, nhung toc do co the cham hon.

## Luu y ve Git

`dataset/`, `videos/`, file ZIP, virtual environment va Python cache duoc ignore trong `.gitignore`. Khong commit cac file du lieu lon vao repository.
