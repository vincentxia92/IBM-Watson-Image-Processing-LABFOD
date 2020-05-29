import numpy
import cv2
from os import system as cmd
import time

print("script has started")

#### Constants

apikey = "3ZDDAJ5VMvcpJ2VstuEd3Iev0q6qxrArW_STqvYu4bka"
imgname = "currFrame.jpg"
workingDir = R'C:\Users\lamn\Github\IBM-Watson-Image-Processing-LABFOD/'
interval_s = 10 # seconds


stream = cv2.VideoCapture("rtsp://admin:123456@10.43.3.200:554/ch01/0")

startingTime = int(time.time())
prev = 0

while(True):

    ret, frame = stream.read()
    cv2.imshow('VIDEO', frame)
    cv2.waitKey(1)
    cv2.imwrite("currFrame.jpg", frame)

    secondsElapsed = int(time.time()) - startingTime
    if(secondsElapsed % interval_s == 0 and secondsElapsed != prev):
        cmdstr = 'curl -X POST -u "apikey:{api}" -F "features=objects" -F "collection_ids=7d48820c-4cdc-42cd-98eb-eaa7a728a443" -F "images_file=@{wd}{img}" "https://gateway.watsonplatform.net/visual-recognition/api/v4/analyze?version=2019-02-11"'.format(api= apikey, wd = workingDir, img = imgname)
        cmd(cmdstr)
        prev = secondsElapsed

    
