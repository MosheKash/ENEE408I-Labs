import cv2
import os
import urllib.request

img = cv2.imread("people.jpg")

# Problem 1:
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("gray.png", gray)

# Problem 2:
edges = cv2.Canny(gray, 100, 200)
cv2.imwrite("edges.png", edges)

# Problem 3:

CASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
cascade_path = "haarcascade_frontalface_default.xml"
 
if not os.path.exists(cascade_path):
    print("Cascade file not found locally, downloading once...")
    urllib.request.urlretrieve(CASCADE_URL, cascade_path)

face_cascade = cv2.CascadeClassifier(cascade_path)

faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 5, minSize = (30, 30))

face_img = img.copy()
for (x, y, w, h) in faces:
    cv2.rectangle(face_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imwrite("faces.png", face_img)

print(f"Detected {len(faces)} face(s)")