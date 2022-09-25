from threading import Thread
from ArmingDrone import ArmingDrone
import cv2
import time

##################### CONFIGURATION #########################

PATH = {
    'images': './Resources/Images/',
    'videos': './Resources/Videos/',
    'result': './Resources/Results/',
}

COURSE = {
  'recognition_flag': 0,
  'tracking_kau': 1,
  'find_f22': 2,
}

ACTIVITY = {
    'hovering': 0,
    'detect_black': 1,
    'detect_red': 2,
    'detect_blue': 3,
}

SWITCH = {
    'search_up': True,
    'search_rotate': True,
    'detect_qr': False,
    'position': True,
    'go_center': True,
    'detect_hw': False,
    'detect_kau': True,
    'detect_f22': True,
    'setting_yaw': True,
    'capture': True,
    'toggle': True,
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
    'search_down_slow': -15,
    'rotate_ccw': -70,
    'rotate_ccw_slow': -40,
    'rotate_cw': 70,
    'rotate_cw_slow': 40,
    'move_tracking': 25,
    'move_tracking_fast': 35,
    'up': 30,
    'right': 60,
    'left': 50,
    'forward': 70,
    'forward_far': 100,
    'back': 35,
}

track = True
seq = ('black', 'red', 'blue')
rot = ''
yaw = 0
detect_yaw = 0
count = 0

######################## READY ###########################

save = input("Video Save ? (Y / N) : ").lower()

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()

if save == 'y':
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(f'{PATH["videos"]}save.avi', fourcc, 35.0, (drone.WIDTH, drone.HEIGHT))

# START VIDEO STREAMING
drone.streamon()
# drone.set_video_fps(drone.FPS_30)

print(f'Battery : {drone.get_battery()}/100')

# TAKE OFF
drone.takeoff()

############## THREAD : VIDEO STREAMING #################
def streaming():
    print('Team Arming : Start Video Stream')

    WIDTH = drone.WIDTH
    HEIGHT = drone.HEIGHT

    global course, detect_qr, message, detect_marker, info_object, info_circle,\
           activity, pError, mission, color, detect_hw, detect_objects

    course = COURSE['recognition_flag']
    activity = ACTIVITY['hovering']
    detect_objects = {
        'KAU': False,
        'F22': False,
    }

    detect_qr = False
    message = False
    pError = 0
    mission = 0
    color = None
    detect_hw = False

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        ################## RECOGNIZE FLAGS ###################
        if course == COURSE['recognition_flag']:

            ###################### HOVERING #######################
            if activity == ACTIVITY['hovering']:
                detect_qr, frame, message = drone.read_qr(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(f'Battery : {drone.get_battery()}/100')
                    drone.land()
                    break

                # DISPLAY
                cv2.imshow("TEAM : ARMING", frame)
                if save == 'y':
                    out.write(frame)

                continue

            ##################### DETECT FLAGS #####################
            if activity == ACTIVITY['detect_black']:
                color = 'black'
            elif activity == ACTIVITY['detect_red']:
                color = 'red'
            elif activity == ACTIVITY['detect_blue']:
                color = 'blue'

            detect_marker, frame, info_circle = drone.identify_shapes(frame, 'circle', color)

            # CAPTURE MARKER AND RECOGNIZE HANDWRITTING
            if detect_marker is True:

                # CAPTURE MARKER
                if SWITCH['capture'] is True:
                    print(f'COURSE : RECOGNIZE FLAGS - CAPTURE {color.upper()} MARKER')
                    path = PATH['result'] + f'{color}_marker.png'
                    cv2.imwrite(path, frame)
                    SWITCH['capture'] = False

                # RECOGNIZE HANDWRITTING
                SWITCH['detect_hw'] = True
                detect_hw, frame, number = drone.detect_number(frame, info_circle)
                mission = int(number)

                if mission == 9:
                    path = PATH['result'] + 'num9.png'
                    cv2.imwrite(path, frame)
        
            elif detect_marker is False:
                SWITCH['detect_hw'] = False

        ################ TRACKING & LANDING #################
        elif course == COURSE['tracking_kau']:
            detect_objects, frame, info_object = drone.detect_object(frame, ['KAU'])

            if detect_objects['KAU'] is True:
                print('KAU Detect Success !!!')

                # CAPTURE KAU
                if SWITCH['capture'] is True:
                    print('COURSE : TRACKING KAU - CAPTURE KAU')
                    path = PATH['result'] + 'kau.png'
                    cv2.imwrite(path, frame)
                    SWITCH['capture'] = False
        
        elif course == COURSE['find_f22']:
            detect_objects, frame, info_object = drone.detect_object(frame, ['F22'])        

        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

        if save == 'y':
            out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'Battery : {drone.get_battery()}/100')
            drone.land()
            break

stream = Thread(target = streaming)
stream.start()

######################### DRONE MOVE #############################
time.sleep(SLEEP['skip_frame'])

al_init = drone.get_height()
print(al_init)
detect_marker = False
i = 0

while True:
    # REGULATE SYNC WITH THREAD
    time.sleep(SLEEP['sync'])

    # GET DRONE YAW
    yaw = drone.get_yaw()
    print(SWITCH['capture'])

    ############# COURSE 1 : RECOGNIZE FLAGS ##############
    if course == COURSE['recognition_flag']:

        ###################### HOVERING #######################
        if activity == ACTIVITY['hovering']:

            if detect_qr is False:
                print('Part : Hovering - Search QR CODE')

                if SWITCH['setting_yaw'] is True:
                    drone.move_back(VELOCITY['back'])
                    drone.rotate_counter_clockwise(45)
                    SWITCH['setting_yaw'] = False

                if SWITCH['toggle'] is True:
                    drone.send_rc_control(0, 0, VELOCITY['search_down_slow'], VELOCITY['rotate_cw_slow'])

                    if yaw > 40:
                        SWITCH['toggle'] = False

                elif SWITCH['toggle'] is False:
                    drone.send_rc_control(0, 0, VELOCITY['search_down_slow'],  VELOCITY['rotate_ccw_slow'])

                    if yaw < -40:
                        SWITCH['toggle'] = True
            
            elif detect_qr is True:
                print("Part : Hovering - Detect QR CODE → Hovering 5s")

                # HOVERING 5s
                drone.hover_sec(SLEEP['hovering'])

                # RETURN TO FIRST ALTITUDE
                al_now = drone.get_height()
                distance = abs(al_init - al_now) + 10

                yaw = drone.get_yaw()
                if yaw >= -45:
                    rotate = 135 - yaw
                elif yaw < -45:
                    rotate = -225 - yaw

                # View in Flag Direction
                drone.move_sec([0, 0, distance, 0], 1)
                if rotate >= 20:
                    drone.rotate_clockwise(rotate)
                elif rotate <= -20:
                    drone.rotate_counter_clockwise(abs(rotate))

                print("Part : Hovering - Finish")
                SWITCH['toggle'] = True

                # CHANGE ACTIVITY
                activity = ACTIVITY[f'detect_{seq[i]}']
                i += 1
                time.sleep(SLEEP['sync'])

            continue

        ################### DETECT FLAGS ####################
        if SWITCH['search_rotate'] is True and detect_marker is False:
            print(f'COURSE : RECOGNIZE FLAGS - Search {color} Marker')

            if activity == ACTIVITY['detect_black']:
                if SWITCH['toggle'] is True and yaw < -120 and yaw < 0:
                    drone.hover_sec(0.5)
                    drone.move_forward(40)
                    SWITCH['toggle'] = False

                elif SWITCH['toggle'] is False and yaw < 110 and yaw > 0:
                    drone.hover_sec(0.5)
                    drone.move_right(40)
                    SWITCH['toggle'] = True

            # ROTATE
            if SWITCH['toggle'] is True:
                rot = 'cw'
            else:
                rot = 'ccw'

            drone.send_rc_control(0, 0, 0, VELOCITY[f'rotate_{rot}'])
            
        elif detect_marker is True:
            SWITCH['search_rotate'] = True

            if track is True:
                if SWITCH['position'] is True:
                    print(f'Part : Detect {color} - Positioning Drone')
                    drone.hover_sec(SLEEP['position'])
                    SWITCH['position'] = False

                # TRACKING SHAPE
                pError, track = drone.track_object(info_circle, pError, speed = VELOCITY['move_tracking'])
                print(f'Part : Detect {color} - Tracking . . .')
                print(f'Now Marker Area : {info_circle[3]} / Track : {track}')

        elif track is False:
            print(f'Part : Detect {color} - Searching handwritting')

            if detect_hw is False:
                drone.send_rc_control(0, 0, VELOCITY['search_down'], 0)
                
        if SWITCH['detect_hw'] is True and detect_hw is True:
            print(f'Part : Detect {color} - Start Mission {mission}')
            drone.hover_sec(0.5)

            # START MISSION
            drone.start_mission(mission)

            # INITIAL VARIABLE
            SWITCH['search_rotate'] = True
            SWITCH['position'] = True
            SWITCH['detect_hw'] = False
            SWITCH['capture'] = True
            SWITCH['toggle'] = True
            detect_marker = False
            detect_hw = False
            mission = 0
            track = True

            if i < len(seq):
                
                # CHANGE ACTIVITY
                drone.hover_sec(0.5)
                detect_yaw = drone.get_yaw()

                # Find the best direction of rotation to find the next flag
                # using the angle at the moment of detecting the flag
                if detect_yaw <= 135 and detect_yaw >= 45:      # ↖
                    SWITCH['toggle'] = True
                elif detect_yaw > 135 and detect_yaw <= -135:   # ↗
                    SWITCH['toggle'] = False
                elif detect_yaw <= -45 and detect_yaw > -135:   # ↘
                    SWITCH['toggle'] = True
                elif detect_yaw > -45 and detect_yaw < 45:      # ↙
                    SWITCH['toggle'] = False

                al_now = drone.get_height()
                distance = al_init - al_now + 10
                drone.move_sec([0, 0, distance, 0], 1)
                
                activity = ACTIVITY[f'detect_{seq[i]}']
                i += 1

            else:
                
                yaw = drone.get_yaw()
                time.sleep(SLEEP['sync'])

                # ROTATE TO LOOK AT KAU
                rotate = 0
                rotate = 0
                if yaw <= 45 and yaw > -120:
                    rotate = -135 - yaw
                elif (yaw > 45 and yaw <= 180) or (yaw < -150 and yaw > -180):
                    rotate = 225 - yaw
                
                if rotate >= 20 and rotate < 300:
                    drone.rotate_clockwise(rotate)
                elif rotate <= -20 and rotate > -300:
                    drone.rotate_counter_clockwise(abs(rotate))

                SWITCH['capture'] = True
                SLEEP['sync'] = 0.1
                drone.move_up(VELOCITY['up'])
                course = COURSE['tracking_kau']
                time.sleep(0.5)

    ########### COURSE 2 : TRACKING KAU MARKER ############
    elif course == COURSE['tracking_kau']:
        if SWITCH['detect_kau'] is True:
            print('Course : Tracking KAU Marker - Search KAU Marker')
            SWITCH['capture'] = True

            yaw = drone.get_yaw()
            if SWITCH['toggle'] is True:
                drone.send_rc_control(0, 0, 0, VELOCITY['rotate_cw_slow'])
                if yaw <= -90 and yaw > -110:
                    SWITCH['toggle'] = False
                    count += 1

            elif SWITCH['toggle'] is False:
                drone.send_rc_control(0, 0, 0,  VELOCITY['rotate_ccw_slow'])
                if yaw > -180 and yaw < -160:
                    SWITCH['toggle'] = True
                    count += 1

            if detect_objects['KAU'] is True:
                SWITCH['detect_kau'] = False
                drone.hover_sec(0.5)

            if count == 2:
                yaw = drone.get_yaw()
                drone.rotate_clockwise(abs(-135 - yaw))
                drone.move_forward(VELOCITY['forward_far'])
                count = 0

        elif SWITCH['detect_kau'] is False:
            print('Course : Tracking KAU Marker - Tracking . . .')
            time.sleep(SLEEP['sync'])

            if detect_objects['KAU'] is True and len(info_object) != 0:
                pError, track = drone.track_object(info_object['KAU'], pError, objects = 'KAU' ,speed = VELOCITY['move_tracking_fast'])

            if track is False:
                print('Course : Tracking KAU - Finish !!!')
                SWITCH['toggle'] = True
                pError = 0
                track = True

                # ROTATE TO LOOK AT F22
                yaw = drone.get_yaw()
                rotate = 0
                if yaw <= 45 and yaw > -120:
                    rotate = -135 - yaw
                elif (yaw > 45 and yaw <= 180) or (yaw < -150 and yaw > -180):
                    rotate = 225 - yaw
                
                if rotate >= 20:
                    drone.rotate_clockwise(rotate)
                elif rotate <= -20:
                    drone.rotate_counter_clockwise(abs(rotate))

                drone.move_up(120)   # 지워줘야 하는 부분

                # drone.move_sec([0, 0, 10, 0], 1)
                course = COURSE['find_f22']
                time.sleep(1)

    ################ COURSE 3 : LANDING F-22 #################
    elif course == COURSE['find_f22']:
        if SWITCH['detect_f22'] is True:
            print('Course : Landing F22 - Searching F22')

            yaw = drone.get_yaw()
            if SWITCH['toggle'] is True:
                drone.send_rc_control(0, 0, 0, VELOCITY['rotate_cw_slow'])

                if yaw > 0:
                    SWITCH['toggle'] = False

            elif SWITCH['toggle'] is False:
                drone.send_rc_control(0, 0, 0,  VELOCITY['rotate_ccw_slow'])

                if yaw < -90:
                    SWITCH['toggle'] = True

            if detect_objects['F22'] is True:
                SWITCH['detect_f22'] = False
                drone.hover_sec(0.5)

        elif SWITCH['detect_f22'] is False:
            print('Course : LANDING F22 - Tracking . . .')

            if detect_objects['F22'] is True and len(info_object) != 0:
                pError, track = drone.track_object(info_object['F22'], pError, objects = 'F22' ,speed = VELOCITY['move_tracking_fast'])

            if track is False:
                print('Course : LANDING F22 - Finish !!!')
                drone.hover()
                # drone.land()
