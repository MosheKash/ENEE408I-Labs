from pathlib import Path

import torch
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "data.yaml"


def main():
    device = 0 if torch.cuda.is_available() else "cpu"

    model = YOLO(str(ROOT / "yolo26n.pt"))
    model.train(
        data = str(DATA),
        epochs = 50,
        imgsz = 640,
        batch = 16,
        patience = 15,
        device = device,
        project = str(ROOT / "runs"),
        name = "turtle",
        exist_ok = True,
    )

    best = YOLO(model.trainer.best)
    metrics = best.val(data = str(DATA), split = "test", device = device)
    print("mAP50:", metrics.box.map50)
    print("mAP50-95:", metrics.box.map)
    print("Best weights:", model.trainer.best)


if __name__ == "__main__":
    main()