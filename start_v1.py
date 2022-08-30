from ArmingDrone import ArmingDrone
import cv2
import time
<<<<<<< HEAD
=======
from utils import *
import threading
>>>>>>> 7e7f9ba7ac0e15cb0aac53c923d675ab1f60f5a7

##################### CONFIGURATION #########################
WIDTH = 700
HEIGHT = 700

VIEW_FRAME = 20
CAPTURE_FRAME = VIEW_FRAME - 20
SKIP_FRAME = 300
PER_FRAME = 33

PATH = {
'images': './images/',
'videos': './videos/',
'result': './results/real/',
}

ACTIVITY = {
'hovering': 0,
'detect_green': 1,
'detect_red': 2,
'detect_blue': 3,
'land': 4,
}

<<<<<<< HEAD
SWITCH = {
'down': True,
'search_up': True,
'clockwise': True,
'qr_clockwise': True
}

SLEEP = {
  'takeoff': 2,
  'hovering': 5,
  'search_up': 1,
  'stop_red': 2,
  'stop_b_g': 1,
  'stop_qr': 1,
}

VELOCITY = {
  'search_up': 20,
  'down': 60,
  'down_s': 20,
  'clockwise': 60,
}

activity = ACTIVITY['hovering']
view_frame = 0
cnt_frame = 0

##################### START TELLO ########################

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

# START VIDEO STREAMING
drone.streamon()

# DRONE TAKEOFF
drone.takeoff()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    ###################### HOVERING #######################
    if activity is ACTIVITY['hovering']:
        detect, frame, messages = drone.read_qr(frame)

        if detect is True:
            view_frame += 1

            if view_frame >= VIEW_FRAME:
                drone.stop()

                # HOVERING 5 sec
                sec = cnt_frame / PER_FRAME
                if sec < SLEEP['hovering']:
                    cnt_frame += 1
                    # STREAMING
                    cv2.imshow('TEAM : ARMING', frame)
                    continue
                else:
                    view_frame = 0
                    cnt_frame = 0
                    activity = ACTIVITY['detect_green']

        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT G #######################
    elif activity is ACTIVITY['detect_green']:
        detect, frame = drone.identify_shapes(frame, 'circle', 'green')

        # SEARCHING
        if SWITCH['search_up'] is True:
            drone.move_up(VELOCITY['search_up'])

            sec = cnt_frame / PER_FRAME
            if sec < SLEEP['search_up']:
                cnt_frame += 1
                # STREAMING
                cv2.imshow('TEAM : ARMING', frame)
                continue
            else:
                cnt_frame = 0
                SWITCH['search_up'] = False
        
        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT R #######################
    elif activity is ACTIVITY['detect_red']:
        pass
=======

def first_mission():
    drone.stop()        # DRONE STOP
    print("1")
    time.sleep(1)       # WAIT 1s
    print("2")
    time.sleep(1)       # WAIT 1s
    print("3")
    time.sleep(1)       # WAIT 1s

    startCounter = 1    # RED DETECTION -> BLUE OR GREEN DETECTION


def main():
    global drone

    startCounter = 0
    detect = False

    # CONNECT TO TELLO
    drone = tellopy.Tello()

    # drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
    drone.connect()
    drone.wait_for_connection(60.0)
    drone.start_video()

    drone.takeoff()

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
    cv2.namedWindow('Original')

    while True:
        for frame in container.decode(video = 0):
            if 0 < frame_skip:
                frame_skip = frame_skip - 1
                continue
            
            start_time = time.time()
            image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

            if startCounter == 0:               # RED DETECTION

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
                            m1 =threading.Thread(group=None, target = first_mission, name=None)
                            m1.start()
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
>>>>>>> 7e7f9ba7ac0e15cb0aac53c923d675ab1f60f5a7

    ###################### DETECT B #######################
    elif activity is ACTIVITY['detect_blue']:
        pass

<<<<<<< HEAD

    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break
=======
            if cv2.waitKey(1) & 0xFF == ord('q'):
                drone.land()
                break

            if frame.time_base < 1.0/60:
                time_base = 1.0/60
            else:
                time_base = frame.time_base
            frame_skip = int((time.time() - start_time)/time_base)
>>>>>>> 7e7f9ba7ac0e15cb0aac53c923d675ab1f60f5a7
