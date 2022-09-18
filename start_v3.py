from threading import Thread
from ArmingDrone import ArmingDrone
import cv2
import time

##################### CONFIGURATION #########################
WIDTH = 700
HEIGHT = 700

PATH = {
    'images': './images/',
    'videos': './videos/',
    'result': './Results/',
}

COURSE = {
  'recognition_flag': 0,
  'tracking_kau': 1,
  'find_f22': 3,
}

ACTIVITY = {
    'hovering': 0,
    'detect_black': 1,
    'detect_red': 2,
    'detect_blue': 3,
    'land': 4,
}

SWITCH = {
    'search_up': True,
    'search_rotate': True,
    'detect_qr': False,
    'position': True,
    'go_center': True,
    'detect_handwritting': False,
}

SLEEP = {
    'skip_frame': 6,
    'hovering': 5,
    'search_up': 1,
    'position': 0.5,
    'sync': 0.03,
}

VELOCITY = {
    'search_up': 20,
    'search_down': -20,
    'rotate_ccw': -70,
    'rotate_cw': 70,
    'move_tracking': 25,
    'right': 60,
    'forward': 70,
    'go_center': 100,
}

track = True
seq = ('black', 'red', 'blue')

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
print(al_init)

############## THREAD : VIDEO STREAMING #################
def streaming():
    print('Start Video Stream')
    global course, detect_qr, message, detect_marker, info, activity, pError, mission, color, detect_hw

    course = COURSE['recognition_flag']
    activity = ACTIVITY['hovering']
    detect_qr = False
    message = False
    pError = 0
    mission = 0
    color = None
    detect_hw = False

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        # Course 1 : Recognize flags
        if course == COURSE['recognition_flag']:

            if activity == ACTIVITY['hovering']:
                detect_qr, frame, message = drone.read_qr(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(f'Battery : {drone.get_battery()}/100')
                    drone.land()
                    break

                continue

            if activity == ACTIVITY['detect_black']:
                color = 'black'
            elif activity == ACTIVITY['detect_red']:
                color = 'red'
            elif activity == ACTIVITY['detect_blue']:
                color = 'blue'

            detect_marker, frame, _ = drone.identify_shapes(frame, 'circle', color)

            # CAPTURE MARKER AND RECOGNIZE HANDWRITTING
            if detect_marker is True:

                # CAPTURE MARKER
                print(f'COURSE : RECOGNIZE FLAGS - CAPTURE {color.upper()} MARKER')
                path = PATH['result'] + f'{color}_marker.png'
                cv2.imwrite(path, frame)

            # RECOGNIZE HANDWRITTING
        
        elif course == COURSE['tracking_kau']:
            frame, info = drone.detect_object(frame, ['kau'])
        
        elif course == COURSE['find_f22']:
            frame, info = drone.detect_object(frame, ['F22'])        

        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'Battery : {drone.get_battery()}/100')
            drone.land()
            break

stream = Thread(target = streaming)
stream.start()

######################### DRONE MOVE #############################
time.sleep(SLEEP['skip_frame'])
i = 0
while True:
    # REGULATE SYNC WITH THREAD
    time.sleep(SLEEP['sync'])

    ############# COURSE 1 : RECOGNIZE FLAGS ##############
    if course == COURSE['recognition_flag']:

        ###################### HOVERING #######################
        if activity == ACTIVITY['hovering']:

            if detect_qr is False:
                print('Part : Hovering - Search QR CODE')
            
                # DOWN
                drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)
            
            elif detect_qr is True:
                print("Part : Hovering - Detect QR CODE → Hovering 5s")

                # HOVERING 5s
                drone.hover_sec(SLEEP['hovering'])

                # RETURN TO FIRST ALTITUDE
                al_now = drone.get_height()
                distance = abs(al_init - al_now) + 10

                if distance >= 20:
                    drone.move_up(distance)

                print("Part : Hovering - Finish")
                
                # CHANGE ACTIVITY
                activity = ACTIVITY[f'detect_{seq[i]}']
                i += 1

            continue
        
        # DRONE GO CENTER
        if SWITCH['go_center'] is True:
            print('COURSE : RECOGNIZE FLAGS - Drone go center')
            drone.go_xyz_speed(100, 200, 10, VELOCITY['go_center'])
            al_init = drone.get_height()
            SWITCH['go_center'] = False

        # RECOGNIZE FLAGS
        elif SWITCH['go_center'] is False:

            if SWITCH['search_rotate'] is True and detect_marker is False:
                print(f'COURSE : RECOGNIZE FLAGS - Search {color} Marker')

                # ROTATE
                drone.send_rc_control(0, 0, 0, VELOCITY['rotate_cw'])

            elif detect_marker is True:

                if SWITCH['position'] is True:
                    print(f'Part : Detect {color} - Positioning Drone')
                    drone.hover_sec(SLEEP['position'])
                    SWITCH['position'] = False

            if SWITCH['position'] is False and SWITCH['detect_handwritting'] is True:
                
                if detect_hw is False:
                    drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)

                elif detect_hw is True:
                    print(f'Mission Number : {mission}')

                    # START MISSION
                    print(f'Part : Detect Red - Start Mission {mission}')
                    drone.start_mission(mission)

                    # RETURN TO FIRST ALTITUDE
                    al_now = drone.get_height()
                    distance = int(abs(al_init - al_now)) + 10
                    if distance >= 20:
                        drone.move_up(distance)

                    # INITIAL VARIABLE
                    SWITCH['search_rotate'] = True
                    SWITCH['position'] = True
                    SWITCH['detect_handwritting'] = False
                    detect_marker = False
                    mission = 0

                    if i < len(seq):
                      # CHANGE ACTIVITY
                      activity = ACTIVITY[f'detect_{seq[i]}']
                      i += 1

                    else:
                      course = COURSE['tracking_kau']


    ########### COURSE 2 : TRACKING KAU MARKER ############
    elif course == COURSE['tracking_kau']:
        pass
  
    ################ COURSE 3 : FIND F-22 #################
    elif course == COURSE['find_f22']:
        pass


stream.join()