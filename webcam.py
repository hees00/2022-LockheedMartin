import sys
import traceback
import cv2 # for avoidance of pylint error
import numpy
import time
from utils import *
import threading

######################################################
width = 700
height = 700
VIEW_FRAME = 60
CAPTURE_FRAME = VIEW_FRAME - 20
frame_skip = 300

PATH = {
  'images': './images/',
  'videos': './videos/',
  'result': './results/real/',
}

ACTIVITY = {
  'takeoff': 0,
  'red': 1,
  'b_g': 2,                     # Detect blue or green 
  'qr': 3,
  'land': 4,
}

SWITCH = {
  'down': True,
  'up': True,
  'clockwise': True,
}

drone_cmd =""
activity = 0
al = 0 ##고도

def streaming():

    while(True):
        ret, frame = cap.read()    # Read 결과와 frame

        if(ret) :
            gray = cv2.cvtColor(frame,  cv2.COLOR_BGR2GRAY)    # 입력 받은 화면 Gray로 변환

            cv2.imshow('frame_color', frame)    # 컬러 화면 출력
            cv2.imshow('frame_gray', gray)    # Gray 화면 출력
            if cv2.waitKey(1) == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()



def main():
    global cap
    cap = cv2.VideoCapture(0)

    streaming_video =threading.Thread(group=None, target = streaming ,name=None)
    streaming_video.start()

    i=0
    while True:
        print(i)
        i+=1
        key=cv2.waitKey(1)
        if key == ord("q"):
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    
        


    