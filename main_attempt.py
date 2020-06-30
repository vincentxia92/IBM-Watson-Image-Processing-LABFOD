import cv2, queue, threading, time
#### Constants

apikey = "3ZDDAJ5VMvcpJ2VstuEd3Iev0q6qxrArW_STqvYu4bka"
imgname = "currFrame.jpg"
workingDir = R''
interval_s = 2 # seconds
rtspAddr = "rtsp://admin:123456@10.43.3.200:554/ch01/0"


# bufferless VideoCapture
class VideoCapture:
  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()

cap = VideoCapture(rtspAddr)
while True:
  frame = cap.read()
  #time.sleep(.5)   # simulate long processing
  cv2.imshow("frame", frame)
  if chr(cv2.waitKey(1)&255) == 'q':
    break
