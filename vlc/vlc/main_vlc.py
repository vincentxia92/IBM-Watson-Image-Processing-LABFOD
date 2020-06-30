import os
import vlc
import time
import cv2
from threading import Thread
import subprocess
import json
rtspAddr = "rtsp://admin:123456@10.43.3.200:554/ch01/0"
apikey = "3ZDDAJ5VMvcpJ2VstuEd3Iev0q6qxrArW_STqvYu4bka"
imgname = "vlc_snapshot.png"
workingDir = os.getcwd()

# set the rectangle background to white
rectangle_bgr = (0, 0, 255)
# texts
separator = ": "
font                   = cv2.FONT_HERSHEY_SIMPLEX
# set the text start position
text_offset_x          = 10
text_offset_y          = 70
fontScale              = 2
fontColor              = (255,255,255)
lineType               = 2
thickness              = 8     


def get_player(url=rtspAddr):
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(url)
    Media.get_mrl()
    player.set_media(Media)
    player.play()
    return player

def get_player_state(player):
      is_playing = player.is_playing()#playing:1 ;other:0
      will_play = player.will_play()
      get_state = player.get_state()
      print ('is_playing: ',is_playing)
      print ('will_play: ', will_play)
      print ('get_state: ', get_state)

def get_player_para(player):
    length = player.get_length()
    width = player.video_get_width()
    size = player.video_get_size()
    title = player.video_get_title_description()
    video_track = player.video_get_track_description()
    audio_track = player.audio_get_track_description()
    fps = player.get_fps()
    rate = player.get_rate()
    track_count = player.video_get_track_count()
    track = player.video_get_track()
    print ('length: ',length)
    print ('width: ',width)
    print ('size: ', size)
    print ('title: ',title)
    print ('video_track: ',video_track)
    print ('audio_track: ',audio_track)
    print ('fps: ',fps)
    print ('rate: ', rate)
    print ('track_count: ',track_count)
    print ('track: ',track)

def parse(res):
    try:
        for attr1 in res['images']:
            if bool(attr1['objects']): # if not empty dictionary
                for attr2 in attr1['objects']['collections']:
                            
                    for obj in attr2['objects']:
                        left,top,width,height,name, score =obj['location']['left'], obj['location']['top'], obj['location']['width'], obj['location']['height'], obj['object'], obj['score']
                        ob = [left,top,width,height,name, score]
                        print ('location', ob)
                        return ob
    except:
        return None
def mark(frame, loc):
        [left,top,width,height,name,score] = loc
        cv2.rectangle(frame,(left,top),(left+width,top+height),(0,0,255),15)

        result = [name, score]

        text = separator.join(str(v) for v in result)

        (text_width_n, text_height_n) = cv2.getTextSize(name, font, fontScale, thickness)[0]
        score = "Confidence: "+ str(score)
        (text_width_s, text_height_s) = cv2.getTextSize(score, font, fontScale, thickness)[0]
       
        # make the coords of the box with a small padding of two pixels (print confidence)
        box_coords_s = ((text_offset_x, text_offset_y), (text_offset_x + text_width_s + 2, text_offset_y - text_height_s - 2))
        # mark where the object
        box_coords_n = ((left, top), (left + text_width_n + 2, top - text_height_n - 2))
        
        cv2.rectangle(frame, box_coords_s[0], box_coords_s[1], rectangle_bgr, cv2.FILLED)
        cv2.rectangle(frame, box_coords_n[0], box_coords_n[1], rectangle_bgr, cv2.FILLED)
        cv2.putText(frame,name, (left, top),  font,  fontScale, fontColor, lineType, thickness)
        cv2.putText(frame,score, (text_offset_x  , text_offset_y),  font,  fontScale, fontColor, lineType, thickness)
        return frame

def cv_main(): # multiple threading (multi-threading causes query problems)
    time.sleep(1)

    startingTime = int(time.time())
    prev = 0
    count = 0
    loc= None
    interval_s = 2
    
    timestamp = time.time()
    while time.time()-timestamp < 400: # in s 
        print("current: ",time.time()-timestamp, "modified: ", time.time()-os.path.getmtime(imgname)) #since last modified
        frame = cv2.imread(os.path.join(workingDir, imgname))

        secondsElapsed = int(time.time()) - startingTime
        if(secondsElapsed % interval_s == 0 and secondsElapsed != prev): # every 2s
            count += 1

            cmdstr = 'curl -X POST -u "apikey:{api}" -F "features=objects" -F "collection_ids=7d48820c-4cdc-42cd-98eb-eaa7a728a443" -F "images_file=@{wd}{img}" "https://gateway.watsonplatform.net/visual-recognition/api/v4/analyze?version=2019-02-11"'.format(api= apikey, wd = r'', img = imgname) #
            
            res = subprocess.run(cmdstr, capture_output=True)
        
            res=res.stdout.decode()
            print("query result is:", res)
            res = json.loads(res)

            loc = parse(res)

            prev = secondsElapsed
            print("count = "+str(count))
        
        if not (loc is None):  # if none object detected when current interval starts, dirently move to next frame
            frame = mark(frame, loc) # only if object detected when current interval starts, mark the location 

        cv2.imshow('Result from Watson', frame)
        ch = cv2.waitKey(1000) # in ms
        if ch & 0xFF == 27:  #press Esc to exit
                break
def cv_call(): # single threading (multi-threading causes query problems) # single thread cause big delay

    startingTime = int(time.time())
    
    loc= None
    
    timestamp = time.time()
    
    print("current: ",time.time()-timestamp, "modified: ", time.time()-os.path.getmtime(imgname)) #since last modified
    frame = cv2.imread(os.path.join(workingDir, imgname))

    cmdstr = 'curl -X POST -u "apikey:{api}" -F "features=objects" -F "collection_ids=7d48820c-4cdc-42cd-98eb-eaa7a728a443" -F "images_file=@{wd}{img}" "https://gateway.watsonplatform.net/visual-recognition/api/v4/analyze?version=2019-02-11"'.format(api= apikey, wd = r'', img = imgname) #
            
    res = subprocess.run(cmdstr, capture_output=True)
        
    res=res.stdout.decode()
    print("query result is:", res)
    res = json.loads(res)

    loc = parse(res)
        
    if not (loc is None):  # if none object detected when current interval starts, dirently move to next frame
        frame = mark(frame, loc) # only if object detected when current interval starts, mark the location 

    cv2.imshow('snapshot taken', frame)
    ch = cv2.waitKey(100) # in ms


def vlc_main():
    timestamp = time.time()
    player = get_player() # create an instance and play
    while time.time()-timestamp < 400: # if exceed 400 secs cannot find the video: leave and print error
        time.sleep(0.4)  # must delay at least one second
        if player.is_playing(): 
            #time.sleep(0.1) # delay for 5 secs
            #get_player_para(player)
            player.video_take_snapshot(num=0, psz_filepath=os.path.join(workingDir, imgname), i_width=720, i_height=480) # take a snapshot and exit # save to a local vlcsnap-date-time.png #i_width=1280, i_height=720
            cv_call() # call open cv for processing # single threading (multi-threading causes query problems)
            #time.sleep(10)
            #player.release() # LEAVE
            #return

            continue
        player.release()
    player.release()
    print ('###########################')
    print ('Fail: cannot find any video')
    print ('###########################')

if __name__ == '__main__':
    #vlc_main()
    th_vlc = Thread(target=vlc_main) #args=()
    #th_cv = Thread(target=cv_main)

    th_vlc.start()

    #th_cv.start()
    # stop execution of current program until a thread is complete
    # wait until thread 1 is completely executed # wait until all threads finish 
    th_vlc.join() 
    # wait until thread 2 is completely executed 
    #th_cv.join() 