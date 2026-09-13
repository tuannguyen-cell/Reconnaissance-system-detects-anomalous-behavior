import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path
import argparse
import time


# ============================================================
# CONFIG
# ============================================================

DATASET_DIR    = Path("dataset")
MODEL_SAVE_DIR = Path("models")

SEQUENCE_LENGTH = 30      # so frame moi sequence
INPUT_SIZE      = 51      # 17 keypoints x (x, y, conf)
HIDDEN_SIZE     = 128     # so neuron LSTM
NUM_LAYERS      = 2       # so lop LSTM xep chong
DROPOUT         = 0.3     # dropout chong overfitting
NUM_CLASSES     = 2       # 0=normal, 1=abnormal

BATCH_SIZE      = 64
EPOCHS          = 50
LR              = 1e-3
WEIGHT_DECAY    = 1e-4
VAL_SPLIT       = 0.2     # 20% du lieu danh cho validation

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ============================================================
# DATASET
# ============================================================

class PoseDataset(Dataset):
    """Load tat ca file .npy trong dataset/normal va dataset/abnormal."""

    def __init__(self, dataset_dir: Path):
        self.data   = []  # (sequence, label)

        label_map = {"normal": 0, "abnormal": 1}

        for class_name, label in label_map.items():
            class_dir = dataset_dir / class_name
            if not class_dir.exists():
                print(f"Canh bao: Khong tim thay thu muc {class_dir}")
                continue
            files = sorted(class_dir.glob("*.npy"))
            for f in files:
                sequences = np.load(f)        # shape (N, 30, 51)
                for seq in sequences:
                    self.data.append(
                        (seq.astype(np.float32), label)
                    )

        print(f"Dataset: {len(self.data)} sequences da nap")

        # Thong ke phan phoi class
        labels = [d[1] for d in self.data]
        n_normal   = labels.count(0)
        n_abnormal = labels.count(1)
        print(f"  Normal  : {n_normal}")
        print(f"  Abnormal: {n_abnormal}")
        print(f"  Ti le   : {n_normal/max(n_abnormal,1):.1f}:1 (normal:abnormal)")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq, label = self.data[idx]
        return torch.tensor(seq), torch.tensor(label, dtype=torch.long)


# ============================================================
# MODEL: LSTM CLASSIFIER
# ============================================================

class LSTMAnomalyDetector(nn.Module):
    """
    LSTM 2 lop -> Fully-connected -> Phan loai 2 class
    Input : (batch, seq_len=30, input_size=51)
    Output: (batch, num_classes=2)
    """

    def __init__(
        self,
        input_size  = INPUT_SIZE,
        hidden_size = HIDDEN_SIZE,
        num_layers  = NUM_LAYERS,
        num_classes = NUM_CLASSES,
        dropout     = DROPOUT,
    ):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size  = input_size,
            hidden_size = hidden_size,
            num_layers  = num_layers,
            batch_first = True,
            dropout     = dropout if num_layers > 1 else 0.0,
            bidirectional = False,
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
        # x: (batch, seq_len, input_size)
        out, _ = self.lstm(x)      # out: (batch, seq_len, hidden)
        last    = out[:, -1, :]    # lay hidden state cuoi: (batch, hidden)
        logits  = self.head(last)  # (batch, num_classes)
        return logits


# ============================================================
# TRAIN / VALIDATE
# ============================================================

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(X)
        loss   = criterion(logits, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()
        total_loss += loss.item() * len(y)
        correct    += (logits.argmax(1) == y).sum().item()
        total      += len(y)
    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        logits = model(X)
        loss   = criterion(logits, y)
        total_loss += loss.item() * len(y)
        correct    += (logits.argmax(1) == y).sum().item()
        total      += len(y)
    return total_loss / total, correct / total


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Train LSTM Anomaly Detector")
    parser.add_argument("--epochs",  type=int,   default=EPOCHS,    help=f"So epoch (mac dinh {EPOCHS})")
    parser.add_argument("--batch",   type=int,   default=BATCH_SIZE,help=f"Batch size (mac dinh {BATCH_SIZE})")
    parser.add_argument("--lr",      type=float, default=LR,        help=f"Learning rate (mac dinh {LR})")
    parser.add_argument("--hidden",  type=int,   default=HIDDEN_SIZE,help=f"LSTM hidden size (mac dinh {HIDDEN_SIZE})")
    args = parser.parse_args()

    MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 60)
    print("LSTM Anomaly Detector - Training")
    print("=" * 60)
    print(f"Device : {DEVICE}" + (f" ({torch.cuda.get_device_name(0)})" if torch.cuda.is_available() else ""))
    print(f"Epochs : {args.epochs}  |  Batch: {args.batch}  |  LR: {args.lr}  |  Hidden: {args.hidden}")
    print("=" * 60)

    # ---- Dataset ----
    dataset = PoseDataset(DATASET_DIR)
    n_val   = int(len(dataset) * VAL_SPLIT)
    n_train = len(dataset) - n_val
    train_ds, val_ds = random_split(
        dataset, [n_train, n_val],
        generator=torch.Generator().manual_seed(42)
    )
    print(f"\nTrain: {len(train_ds)}  |  Val: {len(val_ds)}")

    # Class weights de xu ly mat can bang (330 normal : 107 abnormal ~ 7:1)
    labels  = [dataset[i][1].item() for i in range(len(dataset))]
    n0 = labels.count(0)
    n1 = labels.count(1)
    w0 = 1.0 / n0 if n0 > 0 else 1.0
    w1 = 1.0 / n1 if n1 > 0 else 1.0
    total_w = w0 + w1
    class_weights = torch.tensor([w0/total_w, w1/total_w], dtype=torch.float32).to(DEVICE) * 2
    print(f"Class weights: normal={class_weights[0]:.4f}, abnormal={class_weights[1]:.4f}")

    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True,  num_workers=0, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch, shuffle=False, num_workers=0, pin_memory=True)

    # ---- Model ----
    model = LSTMAnomalyDetector(hidden_size=args.hidden).to(DEVICE)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model params: {total_params:,}")

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-5)

    # ---- Training loop ----
    best_val_acc = 0.0
    best_model_path = MODEL_SAVE_DIR / "lstm_best.pt"

    print()
    print(f"{'Epoch':>5}  {'Train Loss':>10}  {'Train Acc':>9}  {'Val Loss':>8}  {'Val Acc':>8}  {'LR':>8}  {'Time':>6}")
    print("-" * 70)

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()

        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss,   val_acc   = evaluate(model, val_loader, criterion, DEVICE)
        scheduler.step()

        elapsed = time.time() - t0
        current_lr = scheduler.get_last_lr()[0]

        marker = " <-- BEST" if val_acc > best_val_acc else ""
        print(f"{epoch:>5}  {train_loss:>10.4f}  {train_acc:>8.2%}  {val_loss:>8.4f}  {val_acc:>8.2%}  {current_lr:>8.2e}  {elapsed:>5.1f}s{marker}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "epoch"       : epoch,
                "model_state" : model.state_dict(),
                "val_acc"     : val_acc,
                "hidden_size" : args.hidden,
                "input_size"  : INPUT_SIZE,
                "num_layers"  : NUM_LAYERS,
                "num_classes" : NUM_CLASSES,
            }, best_model_path)

    print("-" * 70)
    print(f"\nBest Val Acc : {best_val_acc:.2%}")
    print(f"Model da luu : {best_model_path}")

    # ---- Luu model cuoi ----
    last_model_path = MODEL_SAVE_DIR / "lstm_last.pt"
    torch.save({
        "epoch"       : args.epochs,
        "model_state" : model.state_dict(),
        "val_acc"     : val_acc,
        "hidden_size" : args.hidden,
        "input_size"  : INPUT_SIZE,
        "num_layers"  : NUM_LAYERS,
        "num_classes" : NUM_CLASSES,
    }, last_model_path)
    print(f"Model cuoi   : {last_model_path}")


if __name__ == "__main__":
    main()
