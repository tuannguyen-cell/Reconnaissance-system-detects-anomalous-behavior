import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import cv2
import torch
import torch.nn as nn
import numpy as np
import argparse
import time
from pathlib import Path
from collections import deque
from ultralytics import YOLO


# ============================================================
# CONFIG
# ============================================================

YOLO_MODEL  = "yolov8n-pose.pt"
LSTM_MODEL  = Path("models/lstm_best.pt")
CAMERA_INDEX = 0

SEQUENCE_LENGTH = 30
INPUT_SIZE      = 51    # 17 keypoints x (x, y, conf)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Nguong xac suat de canh bao "BAT THUONG"
ANOMALY_THRESHOLD = 0.6

# Skeleton COCO 17 keypoints
SKELETON = [
    (0,1),(0,2),(1,3),(2,4),
    (5,6),(5,7),(7,9),(6,8),(8,10),
    (5,11),(6,12),(11,12),
    (11,13),(13,15),(12,14),(14,16),
]


# ============================================================
# LSTM MODEL (phai giong voi train_lstm.py)
# ============================================================

class LSTMAnomalyDetector(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=2, num_classes=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size, hidden_size=hidden_size,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_size),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


# ============================================================
# VE SKELETON
# ============================================================

def draw_skeleton(frame, kp_xy, kp_conf, conf_thr=0.25):
    h, w = frame.shape[:2]
    xy   = kp_xy.cpu().numpy()
    conf = kp_conf.cpu().numpy()
    for i, j in SKELETON:
        if conf[i] > conf_thr and conf[j] > conf_thr:
            x1,y1 = int(xy[i][0]), int(xy[i][1])
            x2,y2 = int(xy[j][0]), int(xy[j][1])
            if all(0 < v < d for v, d in [(x1,w),(y1,h),(x2,w),(y2,h)]):
                cv2.line(frame, (x1,y1), (x2,y2), (255,140,0), 2)
    for idx in range(len(xy)):
        if conf[idx] > conf_thr:
            x,y = int(xy[idx][0]), int(xy[idx][1])
            if 0 < x < w and 0 < y < h:
                cv2.circle(frame, (x,y), 4, (0,255,0), -1)


# ============================================================
# VE CANH BAO
# ============================================================

def draw_status(frame, prob_abnormal, n_frames_buffered, fps, device_name, n_persons, frame_info=""):
    h, w = frame.shape[:2]

    # Xac dinh trang thai
    ready = n_frames_buffered >= SEQUENCE_LENGTH

    if not ready:
        status_text  = f"Dang khoi dong... ({n_frames_buffered}/{SEQUENCE_LENGTH})"
        bar_color    = (100, 100, 100)
        status_color = (200, 200, 200)
    elif prob_abnormal >= ANOMALY_THRESHOLD:
        status_text  = f"!! CANH BAO: HANH VI BAT THUONG !!"
        bar_color    = (0, 0, 255)
        status_color = (0, 0, 255)
        # Flash vien do
        cv2.rectangle(frame, (0,0), (w-1, h-1), (0,0,255), 6)
    else:
        status_text  = "BINH THUONG"
        bar_color    = (0, 200, 80)
        status_color = (0, 200, 80)

    # ---- Thanh xac suat (probability bar) ----
    bar_w   = 250
    bar_h   = 18
    bar_x   = w - bar_w - 10
    bar_y   = 10
    fill    = int(bar_w * prob_abnormal) if ready else 0

    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50,50,50), -1)
    if fill > 0:
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill, bar_y + bar_h), bar_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (180,180,180), 1)
    # Duong nguong
    thr_x = bar_x + int(bar_w * ANOMALY_THRESHOLD)
    cv2.line(frame, (thr_x, bar_y - 3), (thr_x, bar_y + bar_h + 3), (255,255,0), 1)
    cv2.putText(frame, f"Bat thuong: {prob_abnormal:.0%}" if ready else "...",
                (bar_x, bar_y + bar_h + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (220,220,220), 1)

    # ---- HUD goc tren trai ----
    hud_h = 105 if frame_info else 85
    overlay = frame.copy()
    cv2.rectangle(overlay, (0,0), (290, hud_h), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    cv2.putText(frame, f"FPS: {fps:.1f}",           (8,22),  cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0,255,255), 2)
    cv2.putText(frame, f"Nguoi: {n_persons}",        (8,45),  cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0,255,255), 2)
    cv2.putText(frame, f"Device: {device_name}",     (8,66),  cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180,180,180), 1)
    cv2.putText(frame, f"Nguong: {ANOMALY_THRESHOLD:.0%}", (8,84), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (180,180,180), 1)
    if frame_info:
        cv2.putText(frame, frame_info, (8,102), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0,220,150), 1)

    # ---- Trang thai chinh (giua cuoi man hinh) ----
    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
    tx = (w - text_size[0]) // 2
    ty = h - 20
    cv2.putText(frame, status_text, (tx+1, ty+1), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 3)
    cv2.putText(frame, status_text, (tx, ty),     cv2.FONT_HERSHEY_SIMPLEX, 0.75, status_color, 2)

    # ---- Phim tat ----
    cv2.putText(frame, "[Q] Thoat  [S] Chup anh  [P] Dung/Tiep",
                (8, h-8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160,160,160), 1)


# ============================================================
# MAIN
# ============================================================

def main():
    global ANOMALY_THRESHOLD

    parser = argparse.ArgumentParser(description="YOLO + LSTM Realtime Anomaly Detection")
    parser.add_argument("--camera",    type=int,   default=CAMERA_INDEX, help="Index webcam (mac dinh 0)")
    parser.add_argument("--video",     type=str,   default=None,         help="Duong dan video file de test (vi du videos/abnormal/01_0051.avi)")
    parser.add_argument("--model",     type=str,   default=YOLO_MODEL,   help="Model YOLO Pose (mac dinh yolov8n-pose.pt)")
    parser.add_argument("--loop",      action="store_true", default=True, help="Tu dong lap lai video khi het (mac dinh: True)")
    parser.add_argument("--no-loop",   dest="loop", action="store_false",help="Khong lap lai video")
    parser.add_argument("--threshold", type=float, default=ANOMALY_THRESHOLD,
                        help=f"Nguong canh bao (mac dinh {ANOMALY_THRESHOLD})")
    parser.add_argument("--conf",      type=float, default=0.25,
                        help="Nguong confidence phat hien nguoi (mac dinh 0.25)")
    parser.add_argument("--width",     type=int,   default=1280)
    parser.add_argument("--height",    type=int,   default=720)
    parser.add_argument("--save",      action="store_true", help="Luu video dau ra")
    args = parser.parse_args()

    ANOMALY_THRESHOLD = args.threshold

    # ---- Kiem tra model LSTM ----
    if not LSTM_MODEL.exists():
        print(f"Chua tim thay LSTM model: {LSTM_MODEL}")
        print("Hay chay 'python scripts/train_lstm.py' truoc!")
        return

    # ---- Tai LSTM model ----
    print(f"Dang tai LSTM model tu {LSTM_MODEL}...")
    ckpt   = torch.load(LSTM_MODEL, map_location=DEVICE, weights_only=False)
    lstm   = LSTMAnomalyDetector(
        input_size  = ckpt.get("input_size",  INPUT_SIZE),
        hidden_size = ckpt.get("hidden_size", 128),
        num_layers  = ckpt.get("num_layers",  2),
        num_classes = ckpt.get("num_classes", 2),
    ).to(DEVICE)
    lstm.load_state_dict(ckpt["model_state"])
    lstm.eval()
    print(f"LSTM loaded! Val Acc khi train: {ckpt.get('val_acc', 0):.2%}")

    # ---- Tai YOLO ----
    device_label = f"GPU - {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU"
    print(f"Dang tai YOLO-Pose ({args.model}) tren {device_label}...")
    yolo = YOLO(args.model)
    print("Ca hai model da san sang!")
    print("Nhan [Q] de thoat, [S] de chup anh, [P] de tam dung/tiep tuc.")

    # ---- Nguon video (Webcam hoac Video file) ----
    is_video_file = False
    video_fps = 30.0
    total_frames = 0

    if args.video:
        video_path = Path(args.video).resolve()
        if not video_path.exists():
            print(f"Khong tim thay file video: {args.video}")
            return
        print(f"Dang doc tu video file: {video_path.name}...")
        cap = cv2.VideoCapture(str(video_path))
        is_video_file = True
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if not video_fps or video_fps <= 0 or video_fps > 120:
            video_fps = 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        loop_status = "ON (lap vo tan)" if args.loop else "OFF"
        print(f"Video FPS: {video_fps:.1f} | Tong so frames: {total_frames} | Che do Loop: {loop_status}")
    else:
        print(f"Dang doc tu webcam index {args.camera}...")
        cap = cv2.VideoCapture(args.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        source_name = args.video if args.video else f"camera {args.camera}"
        print(f"Khong mo duoc {source_name}!")
        return

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter("output_realtime.mp4", fourcc, 30, (actual_w, actual_h))

    # ---- Buffer sliding window (30 frames) ----
    pose_buffer  = deque(maxlen=SEQUENCE_LENGTH)
    prob_abnormal = 0.0
    fps           = 0.0
    frame_time    = time.time()
    paused        = False
    snap_count    = 0
    frame_idx     = 0
    target_frame_duration = 1.0 / video_fps if is_video_file else 0.0

    with torch.no_grad():
        while True:
            t_frame_start = time.time()

            if not paused:
                ret, frame = cap.read()
                if not ret:
                    if is_video_file:
                        if args.loop:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            pose_buffer.clear()
                            frame_idx = 0
                            print("\n[LOOP] Video da het, dang phat lai tu dau...")
                            continue
                        else:
                            print(f"\nDa phat xong toan bo video ({total_frames} frames)!")
                            break
                    else:
                        print("\nKhong doc duoc frame tu camera!")
                        break

                frame_idx += 1
                h, w = frame.shape[:2]

                # ---- YOLO Pose inference ----
                results = yolo(frame, verbose=False, device=DEVICE, conf=args.conf)
                result  = results[0]
                n_persons = 0

                # ---- Lay keypoints nguoi chinh (do tin cay cao nhat) ----
                pose_vec = np.zeros(INPUT_SIZE, dtype=np.float32)

                if result.keypoints is not None and result.boxes is not None and len(result.keypoints) > 0:
                    n_persons = len(result.keypoints)

                    # Chon nguoi co bounding box lon nhat (nguoi trung tam)
                    areas = []
                    for i in range(n_persons):
                        box = result.boxes.xyxy[i].cpu().numpy()
                        areas.append((box[2]-box[0]) * (box[3]-box[1]))
                    main_idx = int(np.argmax(areas))

                    kp_xy   = result.keypoints.xy[main_idx]
                    kp_conf = result.keypoints.conf[main_idx]

                    # Normalize + flatten
                    xy_np   = kp_xy.cpu().numpy().copy()
                    xy_np[:, 0] /= w
                    xy_np[:, 1] /= h
                    c_np = kp_conf.cpu().numpy()

                    # Nguoi hop le neu co cac diem khop than/tay/chan ro rang (ke ca khi quay lung)
                    if len(c_np) > 0 and (np.mean(c_np) > 0.15 or np.max(c_np) > 0.35):
                        pose_vec = np.concatenate([xy_np.flatten(), c_np])

                    # Ve skeleton tung nguoi
                    for i in range(n_persons):
                        box = result.boxes.xyxy[i].cpu().numpy().astype(int)
                        x1,y1,x2,y2 = box
                        is_main = (i == main_idx)
                        box_col = (0, 200, 255) if is_main else (120,120,120)
                        cv2.rectangle(frame, (x1,y1), (x2,y2), box_col, 2)
                        draw_skeleton(frame, result.keypoints.xy[i], result.keypoints.conf[i])

                # ---- Them vao buffer ----
                pose_buffer.append(pose_vec)

                # ---- LSTM inference khi du 30 frames ----
                if len(pose_buffer) == SEQUENCE_LENGTH:
                    seq = np.array(pose_buffer, dtype=np.float32)  # (30, 51)
                    X   = torch.tensor(seq).unsqueeze(0).to(DEVICE) # (1,30,51)
                    logits = lstm(X)
                    probs  = torch.softmax(logits, dim=1)[0]
                    prob_abnormal = float(probs[1])

                # ---- Ve trang thai / canh bao ----
                now        = time.time()
                fps        = 0.9 * fps + 0.1 / max(now - frame_time, 1e-6)
                frame_time = now
                frame_info = f"Frame: {frame_idx}/{total_frames}" if is_video_file else ""
                draw_status(frame, prob_abnormal, len(pose_buffer), fps, device_label, n_persons, frame_info)

                if writer:
                    writer.write(frame)

            # Canh thoi gian delay de video chay dung toc do tu nhien
            if is_video_file and not paused:
                elapsed = time.time() - t_frame_start
                wait_time = max(1, int((target_frame_duration - elapsed) * 1000))
            else:
                wait_time = 1

            cv2.imshow("YOLO + LSTM | Phat Hien Hanh Vi Bat Thuong", frame)
            key = cv2.waitKey(wait_time) & 0xFF
            if key in (ord('q'), 27):
                break
            elif key == ord('s'):
                name = f"snapshot_realtime_{snap_count:03d}.jpg"
                cv2.imwrite(name, frame)
                print(f"Da chup: {name}")
                snap_count += 1
            elif key == ord('p'):
                paused = not paused
                print("TAM DUNG" if paused else "TIEP TUC")

    cap.release()
    if writer:
        writer.release()
        print("Da luu: output_realtime.mp4")
    cv2.destroyAllWindows()
    print("Ket thuc.")


if __name__ == "__main__":
    main()
