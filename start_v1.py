import sys
import traceback
import tellopy
import av
import cv2 # for avoidance of pylint error
import numpy
import time
from utils import *

######################################################
width = 640
height = 480
FRAME = 40

PATH = {
  'images': './images/',
  'videos': './videos/',
  'result': './results/real/',
}
######################################################

def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)

startCounter = 0
detect = False

# CONNECT TO TELLO
drone = tellopy.Tello()

# drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
drone.connect()
drone.wait_for_connection(60.0)
drone.start_video()

retry = 3
container = None
while container is None and 0 < retry:
    retry -= 1
    try:
        container = av.open(drone.get_video_stream())
    except av.AVError as ave:
        print(ave)
        print('retry...')

frame_skip = 500
view_frame = 0
cnt_frame = 0
per_frame = 33
start_option = 0

while True:
    for frame in container.decode(video = 0):
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue
        
        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

        if startCounter == 0:               # RED DETECTION
            drone.takeoff()
            cnt_frame += 1
            if cnt_frame % per_frame < 2:
                cnt_frame = 0
                drone.down(20)              # DRONE DOWN 50cm
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    drone.land()
                    break

                detect, image = identify_color(image, 'red')

                if detect:
                    view_frame += 1

                    if view_frame == FRAME:
                        view_frame = 0
                        drone.stop()        # DRONE STOP
                        time.sleep(3000)       # WAIT 3s

                        startCounter = 1    # RED DETECTION -> BLUE OR GREEN DETECTION
                        break

                    elif view_frame == FRAME // 2:
                            cv2.imwrite(PATH['result'] + 'red_marker.jpg', frame)

                cv2.imshow('Original', image)

        elif startCounter == 1:             # BLUE OR GREEN DETECTION
            detect, image = identify_color(image, 'blue')
            cnt_frame += 1
            if cnt_frame % per_frame < 2:
                cnt_frame = 0
                drone.clockwise(10)              # DRONE DOWN 50cm
            if detect:
                view_frame += 1

                if view_frame == FRAME:
                    view_frame =0
                    drone.stop()          # DRONE STOP
                    time.sleep(500)         # WAIT 1s
                    startCounter = 2      # BLUE OR GREEN DETECTION -> QR CODE DETECTION
                    break
                elif view_frame == FRAME // 2:
                        cv2.imwrite(PATH['result'] + 'blue_marker.jpg', frame)

            cv2.imshow('Original', image)

        elif startCounter == 2:             # QR CODE DETECTION
            cnt_frame += 1
            if cnt_frame % per_frame < 2:
                cnt_frame = 0
                drone.clockwise(10)              # DRONE DOWN 50cm
            detect, image = read_QR(image)
            
            if detect:
                view_frame += 1

                if view_frame == FRAME:
                    view_frame = 0
                    drone.stop()            # DRONE STOP
                    time.sleep(500)           # WAIT 1s
                    drone.land()            # DRONE LAND
                    drone.streamoff()       # VIDEO STEAM OFF
                    break

                elif view_frame == FRAME // 2:
                        cv2.imwrite(PATH['result'] + 'qr_marker.jpg', frame)

            cv2.imshow('Original', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        frame_skip = int((time.time() - start_time)/time_base)