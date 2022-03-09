import cv2

for i in range(1000):
    try:
        cap = cv2.VideoCapture(i)
    except:
        continue
    if cap.isOpened():
        print(i)
        continue