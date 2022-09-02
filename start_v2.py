from email import message
from threading import Thread
from ArmingDrone import ArmingDrone
import cv2
import time

'''
Centor Altitude of Circle = 70cm
Size of QR = 7cm x 7cm
ALitude of QR = 40 ~ 60cm

1. Takeoff 할 때, QR을 인식했는가 ? OK
2. 그래서 5초간 멈췄는가 ? OK
3. Green Marker를 탐색하기 위해 UP 했는가 ? OK
4. Green Marker를 Tracking 하는가 ? OK
5. Green Marker 근처까지 이동하는가 ? OK
6. QR을 Detect하기 위해, 아래로 잘 내려가는가 ? OK
7. QR message를 읽어, 미션을 수행하는가 ? OK
'''

##################### CONFIGURATION #########################
WIDTH = 700
HEIGHT = 700

VIEW_FRAME = 2
SKIP_SEC = 5

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

SWITCH = {
    'search_up': True,
    'search_rotate': True,
    'detect_qr': False,
}

SLEEP = {
    'hovering': 3,
    'search_up': 1,
}

VELOCITY = {
    'search_up': 20,
    'search_down': -10,
    'rotate': -40,
    'move_tracking': 24,
}

TIME = {
    'skip': 0,
    'hovering': 0,
    'search_up': 0,
}

# activity = ACTIVITY['hovering']
# detect_qr = False
# detect_marker = False
info = None
track = True
message = ''
pError = 0
mission = 0

######################## READY ###########################

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()

# START VIDEO STREAMING
drone.streamon()
print(f'Battery : {drone.get_battery()}/100')

# TAKE OFF
drone.takeoff()

################### VIDEO STREAMING ######################
def streaming():
    print('Start Video Stream')
    global detect_qr, message, detect_marker, info, activity
    activity = ACTIVITY['hovering']
    detect_qr = False


    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        ###################### HOVERING #######################
        if activity == ACTIVITY['hovering']:
            detect_qr, frame, message = drone.read_qr(frame)

        ###################### DETECT G #######################
        elif activity == ACTIVITY['detect_green']:
            detect_marker, frame, info = drone.identify_shapes(frame, 'circle', 'blue')

            if track is False:
                detect_qr, frame, message = drone.read_qr(frame)
        
        elif activity == ACTIVITY['land']:
            break

        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'Battery : {drone.get_battery()}/100')
            drone.land()
            break

stream = Thread(target = streaming)
stream.start()

################ THREAD : DRONE MOVE ####################
time.sleep(7)
detect_marker = False

while True:

    # TIMER

    ###################### HOVERING #######################
    if activity == ACTIVITY['hovering']:
        
        # DOWN
        if detect_qr is False:
            drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)
        
        # HOVERING
        elif detect_qr is True:
            drone.send_rc_control(0, 0, 0, 0)

            time.sleep(5)

            # CHANGE ACTIVITY
            activity = ACTIVITY['detect_green']

    ###################### DETECT G #######################
    elif activity == ACTIVITY['detect_green']:
        
        # SEARCHING
        if SWITCH['search_up'] is True:
            # drone.move_up(30)
            SWITCH['search_up'] = False
        
        elif SWITCH['search_rotate'] is True and detect_marker is False:
            drone.send_rc_control(0, 0, 0, VELOCITY['rotate'])

        # TRACKING
        elif detect_marker is True:
            SWITCH['search_rotate'] = False

            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
                print('Part : Green | Tracking . . .')

            # SEARCHING QR CODE
            elif track is False:
                
                if detect_qr is False:
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                elif detect_qr is True:
                    mission = eval(message)

                if mission:
                    drone.start_mission(mission)

                    # INITIAL VARIABLE
                    SWITCH['search_up'] = True
                    SWITCH['search_rotate'] = True
                    detect_marker = False
                    detect_qr = False
                    track = True
                    pError = 0
                    mission = 0
                    start = time.time()

                    # CHANGE ACTIVITY
                    activity = ACTIVITY['detect_red']
    
    elif activity == ACTIVITY['detect_red']:
        print(f'Battery : {drone.get_battery()}/100')
        activity = ACTIVITY['land']
        drone.land()
        break

stream.join()