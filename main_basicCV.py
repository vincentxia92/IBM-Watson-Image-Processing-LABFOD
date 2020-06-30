import numpy as np
import cv2

rtspAddr = "rtsp://admin:123456@10.43.3.200:554/ch01/0"

# this basic implementation has a 4s delay, coming from the camera
cap = cv2.VideoCapture(rtspAddr)

if cap.isOpened() == False:
    print('Cannot open file or video stream')

while True:
    ret, frame = cap.read()

    if ret == True:
        cv2.imshow('Frame', frame)

        if cv2.waitKey(25) & 0xFF == 27:
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()

