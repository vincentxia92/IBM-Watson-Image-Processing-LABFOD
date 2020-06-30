import numpy
import cv2
from os import system as cmd
import time
from threading import Thread
import subprocess
import json
import queue
print("script has started")

#### Constants

apikey = "3ZDDAJ5VMvcpJ2VstuEd3Iev0q6qxrArW_STqvYu4bka"
imgname = "currFrame.jpg"
workingDir = R''
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
        self.thread = Thread(target=self.update, args=())  #update: change the frame. 
        self.thread.daemon = True
        self.thread.start()

        # use a queue to get the most recent frame
        self.q = queue.Queue()

    def update(self):
        while True:
            if self.capture.isOpened():
                (ret, frame) = self.capture.read()
                
                # read frames as soon as they are available, keeping only most recent one
                if not ret:
                    break
                if not self.q.empty():
                    try:
                        self.q.get_nowait()   # discard previous (unprocessed) frame #Remove and return an item from the queue without blocking
                        
                    except queue.Empty:
                        pass
                self.q.put(frame)

    def read(self):
        return self.q.get()

    def parse(self, res):
        for attr1 in res['images']:
            if bool(attr1['objects']): # if not empty dictionary
                for attr2 in attr1['objects']['collections']:
                            
                    for obj in attr2['objects']:
                        left,top,width,height=obj['location']['left'], obj['location']['top'], obj['location']['width'], obj['location']['height']
                        print ('location', left,top,width,height)
                        return [left,top,width,height]

    def mark(self, loc):
        [left,top,width,height]=loc
        cv2.rectangle(self.frame,(left,top),(left+width,top+height),(0,0,255),15)


if __name__ == '__main__':

    stream = ThreadedCamera(rtspAddr)

    startingTime = int(time.time())
    prev = 0
    count = 0
    loc= None

    while(True):
        try:
            stream.frame=stream.read()
            
            # the 5s delay comes from either security camera or opencv, not from the code below 
            cv2.imwrite("currFrame.jpg", stream.frame)

            secondsElapsed = int(time.time()) - startingTime
            if(secondsElapsed % interval_s == 0 and secondsElapsed != prev): # every 2s
                count += 1

                cmdstr = 'curl -X POST -u "apikey:{api}" -F "features=objects" -F "collection_ids=7d48820c-4cdc-42cd-98eb-eaa7a728a443" -F "images_file=@{wd}{img}" "https://gateway.watsonplatform.net/visual-recognition/api/v4/analyze?version=2019-02-11"'.format(api= apikey, wd = workingDir, img = imgname)
                #cmd(cmdstr) #no outputs
                #res = subprocess.check_output(cmdstr).decode('ascii') #slow
                res = subprocess.run(cmdstr, capture_output=True)
                #print("result", res.stdout)
                res=res.stdout.decode()
                
                res = json.loads(res)

                loc = stream.parse(res)

                prev = secondsElapsed
                print("count = "+str(count))
            if not (loc is None):  # if none object detected when current interval starts, dirently move to next frame
                stream.mark(loc) # only if object detected when current interval starts, mark the location 
            cv2.imshow('frame', stream.frame)
            ch = cv2.waitKey(stream.FPS_MS)
            if ch & 0xFF == 27:  #press Esc to exit
                break
        except AttributeError:
            pass
        
        
