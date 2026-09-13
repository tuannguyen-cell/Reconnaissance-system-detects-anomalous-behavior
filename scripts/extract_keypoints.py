import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import cv2
import numpy as np
import argparse
import torch
from pathlib import Path
from ultralytics import YOLO
from tqdm import tqdm


# ============================================================
# CONFIG
# ============================================================

DEVICE = 0 if torch.cuda.is_available() else "cpu"

MODEL_PATH = "yolov8n-pose.pt"

VIDEO_DIR = Path("videos")
OUTPUT_DIR = Path("dataset")

# Mỗi sequence gồm 30 frames
SEQUENCE_LENGTH = 30

# Confidence tối thiểu của người
PERSON_CONFIDENCE = 0.5
# Confidence tối thiểu của người (0.25 tối ưu cho góc nhìn camera giám sát và khi quay lưng)
PERSON_CONFIDENCE = 0.25


# ============================================================
# LOAD YOLOv8-POSE
# ============================================================

model = YOLO(MODEL_PATH)


# ============================================================
# EXTRACT KEYPOINTS FROM ONE VIDEO
# ============================================================

def extract_video(video_path, output_path):

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"❌ Không thể mở video: {video_path}")
        return

    frames = []

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    with tqdm(
        total=total_frames,
        desc=video_path.name
    ):

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            # ------------------------------------------------
            # Kích thước frame
            # ------------------------------------------------

            h, w = frame.shape[:2]

            # ------------------------------------------------
            # YOLOv8-Pose
            # ------------------------------------------------

            results = model(
                frame,
                verbose=False,
                device=DEVICE
            )

            result = results[0]

            # ------------------------------------------------
            # Không phát hiện keypoint
            # ------------------------------------------------

            if result.keypoints is None:

                pose = np.zeros(
                    51,
                    dtype=np.float32
                )

            else:

                keypoints = result.keypoints

                # ------------------------------------------------
                # Không có người
                # ------------------------------------------------

                if len(keypoints) == 0:

                    pose = np.zeros(
                        51,
                        dtype=np.float32
                    )

                else:

                    # ------------------------------------------------
                    # Lấy người đầu tiên
                    # ------------------------------------------------

                    xy = keypoints.xy[0].cpu().numpy()

                    conf = keypoints.conf[0].cpu().numpy()

                    # ------------------------------------------------
                    # NORMALIZE X, Y
                    #
                    # x = x / width
                    # y = y / height
                    #
                    # Sau normalize:
                    # x ∈ [0, 1]
                    # y ∈ [0, 1]
                    # ------------------------------------------------

                    xy[:, 0] = xy[:, 0] / w
                    xy[:, 1] = xy[:, 1] / h

                    # ------------------------------------------------
                    # Kiểm tra confidence của người
                    # ------------------------------------------------

                    # Lấy confidence trung bình
                    # của 17 keypoints

                    mean_confidence = np.mean(conf)
                    # Nguoi hop le neu co cac khop ro rang (ke ca khi quay lung)
                    #if len(conf) == 0 or (np.mean(conf) < 0.15 and np.max(conf) < 0.35):

                    if mean_confidence < PERSON_CONFIDENCE:

                        pose = np.zeros(
                            51,
                            dtype=np.float32
                        )

                    else:

                        # ------------------------------------------------
                        # Flatten keypoints
                        #
                        # 17 keypoints × 2
                        # = 34 giá trị
                        #
                        # confidence
                        # = 17 giá trị
                        #
                        # Tổng:
                        # 34 + 17 = 51
                        # ------------------------------------------------

                        pose = np.concatenate(
                            [
                                xy.flatten(),
                                conf.flatten()
                            ]
                        )

                        pose = pose.astype(
                            np.float32
                        )

            # ------------------------------------------------
            # Thêm frame vào danh sách
            # ------------------------------------------------

            frames.append(pose)

    cap.release()

    # ========================================================
    # CONVERT TO NUMPY ARRAY
    # ========================================================

    frames = np.array(
        frames,
        dtype=np.float32
    )

    print(
        f"\n📌 {video_path.name}"
    )

    print(
        f"   Tổng số frames: {len(frames)}"
    )

    print(
        f"   Shape: {frames.shape}"
    )

    # ========================================================
    # CREATE SEQUENCES
    # ========================================================

    sequences = []

    for start in range(
        0,
        len(frames) - SEQUENCE_LENGTH + 1,
        SEQUENCE_LENGTH
    ):

        sequence = frames[
            start:start + SEQUENCE_LENGTH
        ]

        sequences.append(sequence)

    # --------------------------------------------------------
    # Video quá ngắn
    # --------------------------------------------------------

    if len(sequences) == 0:

        print(
            f"⚠️ Video quá ngắn: {video_path.name}"
        )

        print(
            f"   Cần ít nhất {SEQUENCE_LENGTH} frames."
        )

        return

    # ========================================================
    # CONVERT SEQUENCES TO NUMPY
    # ========================================================

    sequences = np.array(
        sequences,
        dtype=np.float32
    )

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # SAVE
    # ========================================================

    np.save(
        output_path,
        sequences
    )

    print(
        f"✅ Đã lưu: {output_path}"
    )

    print(
        f"   Shape: {sequences.shape}"
    )


# ============================================================
# PROCESS ALL VIDEOS
# ============================================================

def main():

    # --------------------------------------------------------
    # Parse arguments
    # --------------------------------------------------------

    parser = argparse.ArgumentParser(
        description="Trich xuat keypoints tu video dung YOLOv8-Pose"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Bo qua video da co file .npy (tiep tuc tu cho dung)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Gioi han so video moi class de chay thu. Mac dinh: None (chay toan bo)"
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Thong bao che do chay
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("YOLOv8-Pose Keypoint Extractor")
    print("=" * 60)
    print(f"Device  : {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}"
          + (f" - {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else ""))
    print(f"Resume  : {'ON  -> Bo qua video da trich xuat' if args.resume else 'OFF -> Chay lai tu dau neu da co file'}")
    print(f"Limit   : {f'TEST MODE - {args.limit} video/class' if args.limit else 'FULL - Toan bo video'}")
    print("=" * 60)

    # --------------------------------------------------------
    # Kiem tra thu muc videos
    # --------------------------------------------------------

    if not VIDEO_DIR.exists():
        print(f"Khong tim thay thu muc: {VIDEO_DIR}")
        return

    # --------------------------------------------------------
    # Duyet tung class
    # --------------------------------------------------------

    for class_dir in sorted(VIDEO_DIR.iterdir()):

        if not class_dir.is_dir():
            continue

        output_class_dir = (
            OUTPUT_DIR / class_dir.name
        )

        # ----------------------------------------------------
        # Tim video
        # ----------------------------------------------------

        videos = []

        videos += list(class_dir.glob("*.mp4"))
        videos += list(class_dir.glob("*.avi"))
        videos += list(class_dir.glob("*.mov"))
        videos += list(class_dir.glob("*.mkv"))

        videos = sorted(videos)

        # ----------------------------------------------------
        # Resume: loc bo video da co file .npy
        # ----------------------------------------------------

        if args.resume:
            pending = []
            skipped = 0
            for v in videos:
                out = output_class_dir / f"{v.stem}.npy"
                if out.exists():
                    skipped += 1
                else:
                    pending.append(v)
            videos = pending
        else:
            skipped = 0

        # ----------------------------------------------------
        # Test mode: gioi han so luong video
        # ----------------------------------------------------

        if args.limit is not None:
            videos = videos[: args.limit]

        print()
        print("=" * 60)
        print(f"CLASS : {class_dir.name}")
        if args.resume and skipped > 0:
            print(f"Da co  : {skipped} video (bo qua)")
        print(f"Se chay: {len(videos)} video")
        print("=" * 60)

        if not videos:
            print("-> Khong con video nao can xu ly.")
            continue

        # ----------------------------------------------------
        # Xu ly tung video
        # ----------------------------------------------------

        for idx, video_path in enumerate(videos, 1):

            output_path = (
                output_class_dir
                / f"{video_path.stem}.npy"
            )

            print(f"\n[{idx}/{len(videos)}] {video_path.name}")

            extract_video(
                video_path,
                output_path
            )

    print()
    print("=" * 60)
    print("HOAN TAT!")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    main()
