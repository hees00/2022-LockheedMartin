import tellopy
import av
import cv2
import numpy
import time
from utils import *

##################### CONFIGURATION #########################
width = 700
height = 700

VIEW_FRAME = 60
CAPTURE_FRAME = VIEW_FRAME - 20
SKIP_FRAME = 300

INIT_STREAM = 300

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
  'takeoff': True,
  'down': True,
  'up': True,
  'clockwise': True,
}

SLEEP = {
    'takeoff': 1,
    'down': 2,
    'clockwise': 1,
    'stop_red': 3,
    'stop_b_g': 1,
    'stop_qr': 1,
}
###########################################################

def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)


# CONNECT TO TELLO
drone = tellopy.Tello()

# drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
drone.connect()
drone.wait_for_connection(60.0)
drone.start_video()

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
        if 0 < SKIP_FRAME:
            SKIP_FRAME = SKIP_FRAME - 1
            continue

        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        
        #######################################################################
        if activity == ACTIVITY['takeoff']:
            if SWITCH['takeoff'] is True:
                drone.takeoff()
                activity = ACTIVITY['red']

        elif activity == ACTIVITY['red']:
            if SWITCH['down'] is True:
                drone.down(50)
                time.sleep(SLEEP['down'])
                SWITCH['down'] = False
            
            detect, image = identify_color(image, 'red')
            if detect is True:
                view_frame += 1

                if view_frame == CAPTURE_FRAME:
                    drone.stop()
                    time.sleep(SLEEP['stop_red'])
                    cv2.imwrite(PATH['result'] + 'red_marker.jpg', image)

                elif view_frame == VIEW_FRAME:
                    activity == ACTIVITY['b_g']
                    view_frame = 0
            
        elif activity == ACTIVITY['b_g']:
            if SWITCH['clockwise'] is True:
                drone.clockwise(60)
                time.sleep(SLEEP['clockwise'])
                SWITCH['clockwise'] = False

            detect, image = identify_color(image, 'blue')
            if detect is True:
                view_frame += 1

                if view_frame == CAPTURE_FRAME:
                    drone.stop()
                    time.sleep(0.5)
                    cv2.imwrite(PATH['result'] + 'blue_marker.jpg', image)

                elif view_frame == VIEW_FRAME:
                    activity == ACTIVITY['qr']
                    SWITCH['clockwise'] = True
                    view_frame = 0

        elif activity == ACTIVITY['qr']:
            if SWITCH['clockwise'] is True:
                drone.clockwise(60)
                time.sleep(SLEEP['clockwise'])
                SWITCH['clockwise'] = False

            detect, image = read_QR(image)
            if detect is True:
                view_frame += 1

                if view_frame == CAPTURE_FRAME:
                    drone.stop()
                    time.sleep(SLEEP['stop_qr'])
                    cv2.imwrite(PATH['result'] + 'qr_code.jpg', image)

                elif view_frame == VIEW_FRAME:
                    activity == ACTIVITY['land']
                    view_frame = 0

        elif activity == ACTIVITY['land']:
            drone.land()

        if SWITCH['takeoff'] is True:
            time.sleep(SLEEP['takeoff'])
            SWITCH['takeoff'] = False

        cv2.imshow('TEAM : Arming', image)
        #######################################################################

        # FORCE QUIT ( END PROGRAM )
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        SKIP_FRAME = int((time.time() - start_time)/time_base)