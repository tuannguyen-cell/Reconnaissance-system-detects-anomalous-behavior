import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import cv2
import torch
import numpy as np
import argparse
from ultralytics import YOLO

# ============================================================
# CONFIG
# ============================================================

MODEL_PATH   = "yolov8n-pose.pt"
CAMERA_INDEX = 0

DEVICE = 0 if torch.cuda.is_available() else "cpu"

# ------ Ke noi xuong (COCO 17 keypoints) ------
SKELETON = [
    (0, 1), (0, 2),           # mui - mat trai/phai
    (1, 3), (2, 4),           # mat - tai
    (5, 6),                   # vai trai - vai phai
    (5, 7), (7, 9),           # canh tay trai
    (6, 8), (8, 10),          # canh tay phai
    (5, 11), (6, 12),         # than nguoi
    (11, 12),                 # hong trai - hong phai
    (11, 13), (13, 15),       # chan trai
    (12, 14), (14, 16),       # chan phai
]

# Mau ve
COLOR_KP      = (0, 255, 0)      # xanh la: diem khop
COLOR_BONE    = (255, 165, 0)    # cam: xuong
COLOR_BOX     = (0, 200, 255)    # vang: bbox
COLOR_TEXT_BG = (0, 0, 0)
COLOR_TEXT    = (255, 255, 255)

CONF_THRESHOLD = 0.5  # nguong confidence de ve keypoint
CONF_THRESHOLD = 0.25  # nguong confidence de ve keypoint (0.25 giup nhan dien tot khi quay lung)


# ============================================================
# VE SKELETON LEN FRAME
# ============================================================

def draw_pose(frame, keypoints_xy, keypoints_conf):
    """Ve 17 keypoints va xuong len frame."""

    h, w = frame.shape[:2]
    kp_xy   = keypoints_xy.cpu().numpy()    # (17, 2)
    kp_conf = keypoints_conf.cpu().numpy()  # (17,)

    # -- Ve xuong --
    for (i, j) in SKELETON:
        if kp_conf[i] > CONF_THRESHOLD and kp_conf[j] > CONF_THRESHOLD:
            x1, y1 = int(kp_xy[i][0]), int(kp_xy[i][1])
            x2, y2 = int(kp_xy[j][0]), int(kp_xy[j][1])
            if 0 < x1 < w and 0 < y1 < h and 0 < x2 < w and 0 < y2 < h:
                cv2.line(frame, (x1, y1), (x2, y2), COLOR_BONE, 2)

    # -- Ve diem khop --
    for idx in range(len(kp_xy)):
        if kp_conf[idx] > CONF_THRESHOLD:
            x, y = int(kp_xy[idx][0]), int(kp_xy[idx][1])
            if 0 < x < w and 0 < y < h:
                cv2.circle(frame, (x, y), 4, COLOR_KP, -1)

    return frame


# ============================================================
# VE HUD (thong tin goc man hinh)
# ============================================================

def draw_hud(frame, fps, n_persons, device_name):
    h, w = frame.shape[:2]

    # Nen nua trong suot goc tren trai
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (280, 75), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    cv2.putText(frame, f"FPS: {fps:.1f}",         (8, 22),  cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    cv2.putText(frame, f"Persons: {n_persons}",   (8, 47),  cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    cv2.putText(frame, f"Device: {device_name}",  (8, 70),  cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

    # Huong dan phim tat goc duoi trai
    hint = "[Q] Thoat   [S] Chup anh   [P] Pause"
    cv2.putText(frame, hint, (8, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    return frame


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="YOLOv8-Pose Camera Demo")
    parser.add_argument("--camera",  type=int, default=CAMERA_INDEX, help="Index camera (mac dinh: 0)")
    parser.add_argument("--conf",    type=float, default=0.5,         help="Nguong tin cay detect nguoi (mac dinh: 0.5)")
    parser.add_argument("--conf",    type=float, default=0.25,        help="Nguong tin cay detect nguoi (mac dinh: 0.25)")
    parser.add_argument("--width",   type=int, default=1280,          help="Chieu rong camera (mac dinh: 1280)")
    parser.add_argument("--height",  type=int, default=720,           help="Chieu cao camera (mac dinh: 720)")
    parser.add_argument("--save",    action="store_true",             help="Luu video dau ra")
    args = parser.parse_args()

    # --- Khoi dong camera ---
    print(f"Khoi dong camera index {args.camera}...")
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print(f"Khong mo duoc camera {args.camera}!")
        return

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution: {actual_w}x{actual_h}")

    # --- Khoi dong model ---
    device_label = f"GPU - {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU"
    print(f"Dang tai model YOLOv8-Pose tren {device_label}...")
    model = YOLO(MODEL_PATH)
    print("Model da san sang!")
    print("Nhan [Q] de thoat, [S] de chup anh, [P] de tam dung.")

    # --- Writer neu luu video ---
    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter("output_pose.mp4", fourcc, 30, (actual_w, actual_h))
        print("Dang ghi video ra output_pose.mp4 ...")

    # --- Bien theo doi FPS ---
    import time
    fps        = 0.0
    frame_time = time.time()
    paused     = False
    snap_count = 0

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("Khong doc duoc frame!")
                break

            # --- Inference YOLO Pose ---
            results = model(
                frame,
                verbose=False,
                device=DEVICE,
                conf=args.conf,
            )
            result = results[0]

            n_persons = 0

            # --- Ve tung nguoi ---
            if result.keypoints is not None and result.boxes is not None:
                n_persons = len(result.keypoints)

                for i in range(n_persons):
                    # Bounding box
                    box  = result.boxes.xyxy[i].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = box
                    box_conf = float(result.boxes.conf[i])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_BOX, 2)
                    cv2.putText(
                        frame,
                        f"Person {box_conf:.2f}",
                        (x1, max(y1 - 8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_BOX, 2
                    )

                    # Skeleton
                    kp_xy   = result.keypoints.xy[i]
                    kp_conf = result.keypoints.conf[i]
                    draw_pose(frame, kp_xy, kp_conf)

            # --- Ve HUD ---
            now = time.time()
            fps = 0.9 * fps + 0.1 * (1.0 / max(now - frame_time, 1e-6))
            frame_time = now
            draw_hud(frame, fps, n_persons, device_label)

            if writer:
                writer.write(frame)

        # --- Hien thi ---
        cv2.imshow("YOLOv8-Pose | Camera", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:   # Q hoac ESC de thoat
            break
        elif key == ord('s'):              # S de chup anh
            snap_name = f"snapshot_{snap_count:03d}.jpg"
            cv2.imwrite(snap_name, frame)
            print(f"Da chup: {snap_name}")
            snap_count += 1
        elif key == ord('p'):              # P de tam dung / tiep tuc
            paused = not paused
            print("TAM DUNG" if paused else "TIEP TUC")

    cap.release()
    if writer:
        writer.release()
        print("Da luu video: output_pose.mp4")
    cv2.destroyAllWindows()
    print("Ket thuc.")


if __name__ == "__main__":
    main()

