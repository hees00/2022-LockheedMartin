from ArmingDrone import ArmingDrone
import cv2
import time

'''
1. Takeoff 할 때, QR을 인식했는가 ?
2. 그래서 5초간 멈췄는가 ?
3. 
'''

##################### CONFIGURATION #########################
WIDTH = 700
HEIGHT = 700

VIEW_FRAME = 20
CAPTURE_FRAME = VIEW_FRAME - 20
SKIP_SEC = 10

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
cnt_frame = 0


##################### START TELLO ########################

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

# START VIDEO STREAMING
drone.streamon()
skip_start = time.time()
skip_end = 0

drone.takeoff()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # # SKIP FRAME
    # if END['skip'] < SKIP_SEC:
    #     END['skip'] = time.time()
    #     cv2.imshow("TEAM : ARMING", frame)
    #     continue
    
    # elif END['skip'] > SKIP_SEC and SWITCH['takeoff'] is True:
    #     # DRONE TAKEOFF
    #     drone.takeoff()
    #     SWITCH['takeoff'] = False
    #     continue
    

    ###################### HOVERING #######################
    if activity is ACTIVITY['hovering']:
        detect_qr, frame, message = drone.read_qr(frame)

        if detect_qr is True:
            view_frame += 1

            if view_frame == VIEW_FRAME:
                time.sleep(5)
                print('ㅃㅃㅃㅃㅃㅃ')
                view_frame = 0
                activity = ACTIVITY['detect_green']

        cv2.imshow("TEAM : ARMING", frame)

    ###################### DETECT G #######################
    elif activity is ACTIVITY['detect_green']:
        detect, frame, info = drone.identify_shapes(frame, 'circle', 'green')
        detect_qr = False

        # SEARCHING
        if SWITCH['search_up'] is True:
            SWITCH['search_up'] = False
            drone.move_up(30)
        
        elif SWITCH['search_up'] is False:
            # TRACKING GREEN MARKER
            if track is True:
                pError, track = drone.track_shape(info, WIDTH, pError)
            
            # DETECT QR
            elif track is False:
                detect_qr, frame, message = drone.read_qr(frame)

                if detect_qr is False:
                    # DOWN
                    drone.send_rc_control(0, 0, -20, 0)
                
                elif detect_qr is True:
                    time.sleep(0.2)
                    mission = eval(message)

            # START MISSION
            if detect_qr is True and mission:
                drone.start_mission(mission)
                drone.rotate_clockwise(180)
                drone.move_up(40)
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