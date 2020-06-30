import numpy
import cv2
from os import system as cmd
import time
from threading import Thread

print("script has started")

#### Constants

apikey = "3ZDDAJ5VMvcpJ2VstuEd3Iev0q6qxrArW_STqvYu4bka"
imgname = "currFrame.jpg"
workingDir = R'C:\Users\kxia\Github\IBM-Watson-Image-Processing-LABFOD/'
interval_s = 2 # seconds
rtspAddr = "rtsp://admin:123456@10.43.3.200:554/ch01/0"


class ThreadedCamera(object):
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)

        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(self.FPS)

    def show_frame(self):
        cv2.imshow('frame', self.frame)
        cv2.waitKey(self.FPS_MS)

if __name__ == '__main__':

    stream = ThreadedCamera(rtspAddr)

    startingTime = int(time.time())
    prev = 0
    count = 0

    while(True):
        try:
            stream.show_frame()
            cv2.imwrite("currFrame.jpg", stream.frame)

            secondsElapsed = int(time.time()) - startingTime
            if(secondsElapsed % interval_s == 0 and secondsElapsed != prev):
                count += 1

                cmdstr = 'curl -X POST -u "apikey:{api}" -F "features=objects" -F "collection_ids=7d48820c-4cdc-42cd-98eb-eaa7a728a443" -F "images_file=@{wd}{img}" "https://gateway.watsonplatform.net/visual-recognition/api/v4/analyze?version=2019-02-11"'.format(api= apikey, wd = workingDir, img = imgname)
                cmd(cmdstr)
                f.seek(0)
                output = f.read()
                print("output is", output)
                prev = secondsElapsed
                print("count = "+str(count))
        except AttributeError:
            pass
