import cv2
import numpy as np

def detectLine(frame):
    h, w = frame.shape[:2]
    newFrame = frame.copy()

    # White = low saturation + high brightness
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 0, 180), (180, 50, 255))

    # Clean up noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    cv2.imshow("mask", mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    lineCenter = 0.0
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 3000:      
            x, y, bw, bh = cv2.boundingRect(c)
            cx, cy = x + bw // 2, y + bh // 2
            cv2.rectangle(newFrame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
            cv2.circle(newFrame, (cx, cy), 6, (0, 0, 255), -1)
            lineCenter = (cx - w / 2) / (w / 2)

    return lineCenter, newFrame

def main():
    cam = cv2.VideoCapture(0) 

    while cam.isOpened():
        ret, frame = cam.read()
        if not ret:
            break

        lineCenter, newFrame = detectLine(frame)

        cv2.imshow('Line Tracking', newFrame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
