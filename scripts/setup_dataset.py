import sys
import io
# Reconfigure stdout/stderr for utf-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import zipfile
import tarfile
import os
import cv2
from pathlib import Path
from tqdm import tqdm

class ChainedStream(io.RawIOBase):
    def __init__(self, streams):
        self.streams = list(streams)
        self.idx = 0

    def readinto(self, b):
        while self.idx < len(self.streams):
            n = self.streams[self.idx].readinto(b)
            if n:
                return n
            self.idx += 1
        return 0

    def readable(self):
        return True

def main():
    zip_path = Path("OneDrive_2_9-8-2026.zip")
    if not zip_path.exists():
        print(f"Khong tim thay {zip_path}")
        return

    print("Dang mo file zip va chuan bi giai nen ShanghaiTech...")
    z = zipfile.ZipFile(zip_path)
    parts = sorted([n for n in z.namelist() if 'shanghaitech.tar.gz.' in n])
    print(f"Tim thay {len(parts)} phan cua file tar.gz")

    streams = [z.open(p) for p in parts]
    chained = io.BufferedReader(ChainedStream(streams))

    normal_dir = Path("videos/normal")
    normal_dir.mkdir(parents=True, exist_ok=True)
    
    abnormal_dir = Path("videos/abnormal")
    abnormal_dir.mkdir(parents=True, exist_ok=True)

    annot_dir = Path("dataset/annotations")
    annot_dir.mkdir(parents=True, exist_ok=True)

    temp_testing = Path("temp_testing")
    temp_testing.mkdir(parents=True, exist_ok=True)

    print("Dang giai nen video normal, annotations va testing frames...")
    with tarfile.open(fileobj=chained, mode='r:gz') as tar:
        for member in tqdm(tar, desc="Giai nen"):
            # 1. Trich xuat video training vao videos/normal
            if "training/videos/" in member.name and member.isfile():
                filename = Path(member.name).name
                dest = normal_dir / filename
                if not dest.exists():
                    with tar.extractfile(member) as f_in, open(dest, 'wb') as f_out:
                        f_out.write(f_in.read())

            # 2. Trich xuat annotations (test_frame_mask, test_pixel_mask)
            elif "test_frame_mask" in member.name and member.isfile():
                sub_dir = annot_dir / "test_frame_mask"
                sub_dir.mkdir(parents=True, exist_ok=True)
                dest = sub_dir / Path(member.name).name
                if not dest.exists():
                    with tar.extractfile(member) as f_in, open(dest, 'wb') as f_out:
                        f_out.write(f_in.read())

            # 3. Trich xuat test frames tam thoi
            elif "testing/frames/" in member.name and member.isfile():
                rel_parts = Path(member.name).parts
                idx = rel_parts.index('frames')
                sub_path = Path(*rel_parts[idx+1:])
                dest = temp_testing / sub_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    with tar.extractfile(member) as f_in, open(dest, 'wb') as f_out:
                        f_out.write(f_in.read())

    print("\nDang ghep cac frame testing thanh video avi vao videos/abnormal...")
    clip_dirs = sorted([d for d in temp_testing.iterdir() if d.is_dir()])
    for clip_dir in tqdm(clip_dirs, desc="Ghep video abnormal"):
        frames = sorted(list(clip_dir.glob("*.jpg")), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem)
        if not frames:
            continue
        first_frame = cv2.imread(str(frames[0]))
        if first_frame is None:
            continue
        h, w = first_frame.shape[:2]
        out_video_path = abnormal_dir / f"{clip_dir.name}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(out_video_path), fourcc, 24.0, (w, h))
        for fpath in frames:
            img = cv2.imread(str(fpath))
            if img is not None:
                out.write(img)
        out.release()

    print("Dang don dep thu muc anh tam...")
    import shutil
    shutil.rmtree(temp_testing, ignore_errors=True)

    print("\nHoan tat!")
    print(f"Videos binh thuong (normal): {len(list(normal_dir.glob('*.avi')))} files trong {normal_dir}")
    print(f"Videos bat thuong (abnormal): {len(list(abnormal_dir.glob('*.avi')))} files trong {abnormal_dir}")
    print(f"Annotations nhan ground-truth: luu tai {annot_dir}")

if __name__ == "__main__":
    main()