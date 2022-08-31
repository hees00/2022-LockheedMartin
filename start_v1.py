from termios import VEOL
from ArmingDrone import ArmingDrone
import cv2
import time

'''
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
    'takeoff': True,
    'down': True,
    'stop': True,
    'search_up': True,
    'detect_qr': False,
    'clockwise': True,
    'qr_clockwise': True,
}

SLEEP = {
    'hovering': 5,
    'search_up': 1,
}

VELOCITY = {
    'search_up': 20,
    'search_down': -20,
}

END = {
    'skip': 0,
    'hovering': 0,
    'search_up': 0,
}

activity = ACTIVITY['hovering']
track = True
pError = 0
mission = 0
view_frame = 0
skip_end = 0

##################### START TELLO ########################

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

# START VIDEO STREAMING
drone.streamon()
skip_start = time.time()

drone.takeoff()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # SKIP FRAME
    if END['skip'] < SKIP_SEC:
        END['skip'] = time.time()
        cv2.imshow("TEAM : ARMING", frame)
        continue
    
    ###################### HOVERING #######################
    if activity is ACTIVITY['hovering']:
        detect_qr, frame, message = drone.read_qr(frame)

        if detect_qr is True:
            view_frame += 1
            print(view_frame)
            if view_frame == VIEW_FRAME:
                time.sleep(SLEEP['hovering'])
                print('HOVERING FINISH')
                view_frame = 0
                activity = ACTIVITY['detect_green']
        else:
            # DOWN
            drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)


        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT G #######################
    elif activity is ACTIVITY['detect_green']:
        detect, frame, info = drone.identify_shapes(frame, 'circle', 'green')
        detect_qr = False

        # SEARCHING
        if SWITCH['search_up'] is True:
            SWITCH['search_up'] = False
            drone.move_up(VELOCITY['search_up'])
        
        elif SWITCH['search_up'] is False:
            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError, speed = 30)
            
            # DETECT QR
            elif track is False:
                detect_qr, frame, message = drone.read_qr(frame)

                if detect_qr is False:
                    # DOWN
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)
                
                elif detect_qr is True:
                    time.sleep(0.2)
                    mission = eval(message)

            # START MISSION
            if detect_qr is True and mission:
                print(message)
                drone.start_mission(mission)
                drone.move_up(VELOCITY['search_up'])
                activity = ACTIVITY['detect_red']
        
        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT R #######################
    elif activity is ACTIVITY['detect_red']:
        pass

    ###################### DETECT B #######################
    elif activity is ACTIVITY['detect_blue']:
        pass


    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break