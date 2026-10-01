import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent

WEIGHTS = {
    "base": ROOT / "yolo26n.pt",
    "tuned": ROOT / "runs" / "turtle" / "weights" / "best.pt",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices = WEIGHTS.keys(), default = "base")
    args = parser.parse_args()

    model = YOLO(str(WEIGHTS[args.model]))
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        results = model(frame, verbose = False)
        annotated = results[0].plot()
        cv2.imshow(f"YOLO26n ({args.model})", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()