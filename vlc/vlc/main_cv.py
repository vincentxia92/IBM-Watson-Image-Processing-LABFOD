import numpy as np
import cv2

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("rtsp://admin:123456@10.43.3.200:554/ch01/0")
# 定义解码器并创建VideoWrite对象
# linux: XVID、X264; windows:DIVX
# 20.0指定一分钟的帧数
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        frame = cv2.flip(frame, 0)

        # 写入帧
        out.write(frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# 释放内存
cap.release()
out.release()
cv2.destroyAllWindows()
