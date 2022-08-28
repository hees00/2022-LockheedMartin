from ArmingDrone import ArmingDrone
import cv2
import time

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

    ###################### DETECT B #######################
    elif activity is ACTIVITY['detect_blue']:
        pass


    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break