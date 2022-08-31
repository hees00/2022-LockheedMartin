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
    'skip_frame': True,
    'search_up': True,
    'search_rotate': True,
    'detect_qr': False,
}

SLEEP = {
    'hovering': 5,
    'search_up': 1,
}

VELOCITY = {
    'search_up': 20,
    'search_down': -20,
    'rotate': 30,
    'move_tracking': 30,
}

TIME = {
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
start = time.time()

# TAKE OFF
drone.takeoff()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # SKIP FRAME
    if SWITCH['skip_frame'] is True and TIME['skip'] - start < SKIP_SEC:
        TIME['skip'] = time.time()
        cv2.imshow("TEAM : ARMING", frame)
        continue
    
    ###################### HOVERING #######################
    if activity is ACTIVITY['hovering']:
        detect_qr, frame, message = drone.read_qr(frame)

        if detect_qr is True:
            view_frame += 1
            if view_frame == VIEW_FRAME:
                time.sleep(SLEEP['hovering'])
                view_frame = 0

                start = time.time()
                activity = ACTIVITY['detect_green']
        else:
            # DOWN
            drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT G #######################
    elif activity is ACTIVITY['detect_green']:
        detect, frame, info = drone.identify_shapes(frame, 'circle', 'green')
        detect_qr = False

        # SEARCHING
        if SWITCH['search_up'] is True:
            # drone.move_up(VELOCITY['search_up'])
            TIME['search_up'] = time.time()

            if TIME['search_up'] - start < SLEEP['search_up']:
                drone.send_rc_control(0, 0, VELOCITY['search_up'], 0)
            else:
                SWITCH['search_up'] = False
        
        # TRACKING
        elif SWITCH['search_up'] is False:
            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
            
            # DETECT QR
            elif track is False:
                detect_qr, frame, message = drone.read_qr(frame)

                if detect_qr is False:
                    # DOWN
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)
                
                elif detect_qr is True:
                    mission = eval(message)

            # START MISSION
            if detect_qr is True and mission:
                drone.start_mission(mission)

                # INITIAL VARIABLE
                SWITCH['search_up'] = True
                track = True
                pError = 0
                mission = 0
                start = time.time()

                # CHANGE ACTIVITY
                activity = ACTIVITY['detect_red']
        
        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT R #######################
    elif activity is ACTIVITY['detect_red']:
        detect, frame, info = drone.identify_shapes(frame, 'circle', 'red')
        detect_qr = False

        # SEARCHING
        if SWITCH['search_up'] is True:
            # drone.move_up(VELOCITY['search_up'])
            TIME['search_up'] = time.time()

            if TIME['search_up'] - start < SLEEP['search_up']:
                drone.send_rc_control(0, 0, VELOCITY['search_up'], 0)
            else:
                SWITCH['search_up'] = False

        elif SWITCH['search_rotate'] is True and detect is False:
            drone.send_rc_control(0, 0, 0, VELOCITY['rotate'])
        
        # TRACKING
        elif detect is True:
            SWITCH['search_rotate'] = False

            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
            
            # READ QR
            elif track is False:
                detect_qr, message = drone.read_qr(frame)

                if detect_qr is False:
                    # DOWN
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                elif detect_qr is True:
                    mission = eval(message)
            
            # START MISSION
            if mission:
                drone.start_mission(mission)

                # INITIAL VARIABLE
                SWITCH['search_up'] = True
                SWITCH['search_rotate'] = True
                track = True
                pError = 0
                mission = 0
                start = time.time()

                # CHANGE ACTIVITY
                activity = ACTIVITY['detect_blue']

    ###################### DETECT B #######################
    elif activity is ACTIVITY['detect_blue']:
        detect, frame, info = drone.identify_shapes(frame, 'circle', 'blue')
        detect_qr = False

        # SEARCHING
        if SWITCH['search_up'] is True:
            # drone.move_up(VELOCITY['search_up'])
            TIME['search_up'] = time.time()

            if TIME['search_up'] - start < SLEEP['search_up']:
                drone.send_rc_control(0, 0, VELOCITY['search_up'], 0)
            else:
                SWITCH['search_up'] = False

        elif SWITCH['search_rotate'] is True and detect is False:
            drone.send_rc_control(0, 0, 0, VELOCITY['rotate'])

        # TRACKING
        elif detect is True:
            SWITCH['search_rotate'] = False

            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
            
            # READ QR
            elif track is False:
                detect_qr, message = drone.read_qr(frame)

                if detect_qr is False:
                    # DOWN
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                elif detect_qr is True:
                    mission = eval(message)
            
            # START MISSION
            if mission:
                drone.start_mission(mission)

                # FINISH : DRONE LAND
                drone.land()
                break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break

cv2.destroyAllWindows()