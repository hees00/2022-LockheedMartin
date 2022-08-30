import sys
import traceback
import tellopy
import av
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

al = 0

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
######################################################

def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)
        al = data.data.height

def controll_drone(cmd,p):
    if cmd == "stop":
        drone.up(0)
        drone.down(0)
        drone.clockwise(0)
        drone.forward(0)
        drone.backward(0)
        drone.right(0)
        drone.left(0)
        
    elif cmd == "down":
        drone.down(p)
        controll_drone("stop",0)
    elif cmd == "up":
        drone.up(p)
        controll_drone("stop",0)
    elif cmd == "clocckwise":
        drone.clockwise(p)
        time.sleep(3)
        controll_drone("stop",0)


def main():
    global drone
    # CONNECT TO TELLO
    drone = tellopy.Tello()

    drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
    drone.connect()
    drone.wait_for_connection(60.0)
    # drone.start_video()

    retry = 3
    container = None
    view_frame = 0
    activity = 0

    while container is None and 0 < retry:
        retry -= 1
        try:
            container = av.open(drone.get_video_stream())
        except av.AVError as ave:
            print(ave)
            print('retry...')


    while True:
        for frame in container.decode(video = 0):
            if 0 < frame_skip:
                frame_skip = frame_skip - 1
                continue

            start_time = time.time()
            image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
            

            #######################################################################
            if activity == ACTIVITY['takeoff']:
                drone.takeoff()
                time.sleep(2)
                activity = ACTIVITY['red']

            elif activity == ACTIVITY['red']:
                if SWITCH['down'] is True:
                    drone.down(10)
                    time.sleep(2)
                
                detect, image = identify_color(image, 'red')
                if detect is True:
                    SWITCH['down'] = False
                    view_frame += 1

                    if view_frame == CAPTURE_FRAME:
                        controll_drone("stop",0)
                        time.sleep(3)
                        cv2.imwrite(PATH['result'] + 'red_marker.jpg', image)

                    elif view_frame == VIEW_FRAME:
                        activity == ACTIVITY['b_g']
                        view_frame = 0
                
            elif activity == ACTIVITY['b_g']:
                if SWITCH['clockwise'] is True:
                    turning =threading.Thread(group=None, target = controll_drone, args=("clockwise",60),name=None)
                    turning.start()

                detect_blue, image_blue = identify_color(image, 'blue')
                detect_green, image_green = identify_color(image, 'green')
                if detect_blue is True:
                    detect = detect_blue
                    image = image_blue
                    detect_color = "blue"
                elif detect_green is True:
                    detect = detect_green
                    image = image_green
                    detect_color = "green"
                else :
                    detect = False

                if detect is True:
                    SWITCH['clockwise'] = False
                    view_frame += 1

                    if view_frame == CAPTURE_FRAME:
                        drone.stop()
                        time.sleep(0.5)
                        cv2.imwrite(PATH['result'] + 'blue_marker.jpg', image)
                        print(detect_color)

                    elif view_frame == VIEW_FRAME:
                        activity == ACTIVITY['qr']
                        SWITCH['clockwise'] = True
                        view_frame = 0

            elif activity == ACTIVITY['qr']:
                if SWITCH['clockwise'] is True:
                    turning =threading.Thread(group=None, target = controll_drone, args=("clockwise",60),name=None)
                    turning.start()
                    

                detect, image = read_QR(image)
                if detect is True:
                    view_frame += 1
                    SWITCH['clockwise'] = False

                    if view_frame == CAPTURE_FRAME:
                        drone.stop()
                        time.sleep(0.5)
                        cv2.imwrite(PATH['result'] + 'blue_marker.jpg', image)

                    elif view_frame == VIEW_FRAME:
                        activity == ACTIVITY['land']
                        view_frame = 0

            elif activity == ACTIVITY['land']:
                drone.land()

            cv2.imshow('TEAM : Arming', image)
            #######################################################################

            if cv2.waitKey(1) & 0xFF == ord('q'):
                drone.land()
                break

            if frame.time_base < 1.0/60:
                time_base = 1.0/60
            else:
                time_base = frame.time_base
            frame_skip = int((time.time() - start_time)/time_base)