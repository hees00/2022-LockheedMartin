from email import message
from threading import Thread
from ArmingDrone import ArmingDrone
import cv2
import time

'''
Centor Altitude of Circle = 70cm
Size of QR = 7cm x 7cm
ALitude of QR = 40 ~ 60cm

1. Takeoff 할 때, QR을 인식했는가 ? 
2. 그래서 5초간 멈췄는가 ? 
3. Green Marker를 탐색하기 위해 UP 했는가 ? 
4. Green Marker를 Tracking 하는가 ? 
5. Green Marker 근처까지 이동하는가 ? 
6. QR을 Detect하기 위해, 아래로 잘 내려가는가 ? 
7. QR message를 읽어, 미션을 수행하는가 ? 
'''

##################### CONFIGURATION #########################
WIDTH = 700
HEIGHT = 700

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
    'skip_frame': 6,
    'hovering': 3,
    'search_up': 1,
}

VELOCITY = {
    'search_up': 20,
    'search_down': -20,
    'rotate_ccw': -40,
    'move_tracking': 24,
}

# activity = ACTIVITY['hovering']
# detect_qr = False
# detect_marker = False
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
al_init = drone.get_height()

################### VIDEO STREAMING ######################
def streaming():
    print('Start Video Stream')
    global detect_qr, message, detect_marker, info, activity

    activity = ACTIVITY['hovering']
    detect_qr = False


    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        detect_marker = False
        ###################### HOVERING #######################
        if activity == ACTIVITY['hovering']:
            detect_qr, frame, message = drone.read_qr(frame)

        ###################### DETECT G #######################
        elif activity == ACTIVITY['detect_green']:
            detect_marker, frame, info = drone.identify_shapes(frame, 'circle', 'green')

        ###################### DETECT R #######################
        elif activity == ACTIVITY['detect_green']:
            detect_marker, frame, info = drone.identify_shapes(frame, 'circle', 'red')
        
        ###################### DETECT B #######################
        elif activity == ACTIVITY['detect_green']:
            detect_marker, frame, info = drone.identify_shapes(frame, 'circle', 'blue')

        if track is False:
            detect_qr, frame, message = drone.read_qr(frame)

        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'Battery : {drone.get_battery()}/100')
            drone.land()
            break

stream = Thread(target = streaming)
stream.start()

################ THREAD : DRONE MOVE ####################
time.sleep(SLEEP['skip_frame'])
detect_marker = False

while True:

    ###################### HOVERING #######################
    if activity == ACTIVITY['hovering']:

        if detect_qr is False:
            print('Part : Hovering - Search QR CODE')
            
            # DOWN
            drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)
        
        elif detect_qr is True:
            print("Part : Hovering - Detect QR CODE > Hovering 5s")
            
            # HOVERING 5s
            start = time.time()
            while True:
                end = time.time()
                sec = end - start
                # drone.send_rc_control(0, 0, 0, 0)
                drone.hover()

                print(f'\n\tHovering time : {sec}\n')
                if sec > SLEEP['hovering']:
                    break
            
            # RETURN TO FIRST ALTITUDE
            al_now = drone.get_height()
            distance = abs(al_init - al_now)
            drone.move_up(distance)

            # CHANGE ACTIVITY
            activity = ACTIVITY['detect_green']


    ###################### DETECT G #######################
    elif activity == ACTIVITY['detect_green']:

        # SEARCHING
        if SWITCH['search_rotate'] is True and detect_marker is False:
            print('Part : Detect G - Search Green Marker')
            drone.send_rc_control(0, 0, 0, VELOCITY['rotate_ccw'])
        
        # TRACKING
        elif detect_marker is True:
            SWITCH['search_rotate'] = False

            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
                print('Part : Detect G - Tracking . . .')
                print(f'Now Marker Area : {info[3]}')
            
            # DETECT QR
            elif track is False:
                print('Part : Detect G - Searching QR CODE')

                # DOWN
                if detect_qr is False:
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                # GET MISSION NUMBER
                elif detect_qr is True:
                    mission = eval(message)
            
            # START MISSION
            if mission != 0:
                print(f'Part : Detect G - Start Mission {message}')
                drone.start_mission(mission)

                # RETURN TO FIRST ALTITUDE
                al_now = drone.get_height()
                distance = abs(al_init - al_now)
                drone.move_up(distance)

                # Plus Movement

                # INITIAL VARIABLE
                SWITCH['search_rotate'] = True
                track = False
                pError = 0
                mission = 0

                # CHANGE ACTIVITY
                activity = ACTIVITY['detect_red']

        ###################### DETECT R #######################
        elif activity == ACTIVITY['detect_red']:

            # SEARCHING
            if SWITCH['search_rotate'] is True and detect_marker is False:
                print('Part : Detect R - Search Red Marker')
                drone.send_rc_control(0, 0, 0, VELOCITY['rotate_ccw'])

            # TRACKING
            elif detect_marker is True:
                SWITCH['search_rotate'] = False

                # TRACKING GREEN MARKER
                if track is True:
                    pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
                    print('Part : Detect R - Tracking . . .')
                    print(f'Now Marker Area : {info[3]}')

                # DETECT QR
                elif track is False:
                    print('Part : Detect R - Searching QR CODE')

                    # DOWN
                    if detect_qr is False:
                        drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                    # GET MISSION NUMBER
                    elif detect_qr is True:
                        mission = eval(message)
                
                # START MISSION
                if mission != 0:
                    print(f'Part : Detect R - Start Mission {message}')
                    drone.start_mission(mission)

                    # RETURN TO FIRST ALTITUDE
                    al_now = drone.get_height()
                    distance = abs(al_init - al_now)
                    drone.move_up(distance)

                    # Plus Movement

                    # INITIAL VARIABLE
                    SWITCH['search_rotate'] = True
                    track = False
                    pError = 0
                    mission = 0

                    # CHANGE ACTIVITY
                    activity = ACTIVITY['detect_blue']
        
        ###################### DETECT B #######################
        elif activity == ACTIVITY['detect_red']:

            # SEARCHING
            if SWITCH['search_rotate'] is True and detect_marker is False:
                print('Part : Detect B - Search Blue Marker')
                drone.send_rc_control(0, 0, 0, VELOCITY['rotate_ccw'])

            # TRACKING
            elif detect_marker is True:
                SWITCH['search_rotate'] = False

                # TRACKING GREEN MARKER
                if track is True:
                    pError, track = drone.track_shape(info, WIDTH, pError, speed = VELOCITY['move_tracking'])
                    print('Part : Detect B - Tracking . . .')
                    print(f'Now Marker Area : {info[3]}')

                # DETECT QR
                elif track is False:
                    print('Part : Detect B - Searching QR CODE')

                    # DOWN
                    if detect_qr is False:
                        drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                    # GET MISSION NUMBER
                    elif detect_qr is True:
                        mission = eval(message)
                
                # START MISSION
                if mission != 0:
                    print(f'Part : Detect B - Start Mission {message}')
                    drone.start_mission(mission)

                    # RETURN TO FIRST ALTITUDE
                    al_now = drone.get_height()
                    distance = abs(al_init - al_now)
                    drone.move_up(distance)

                    # Plus Movement

                    # INITIAL VARIABLE
                    SWITCH['search_rotate'] = True
                    track = False
                    pError = 0
                    mission = 0

                    # DRONE LAND
                    drone.land()
                    break
            

stream.join()