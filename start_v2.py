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

################### VIDEO STREAMING ######################
def video_stream():
    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        # # SKIP FRAME
        # if TIME['skip'] < SKIP_SEC:
        #     TIME['skip'] = time.time()
        #     cv2.imshow("TEAM : ARMING", frame)
        #     continue

        ###################### HOVERING #######################
        if activity is ACTIVITY['hovering']:
            detect_qr, frame, message = drone.read_qr(frame)




##################### START TELLO ########################

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

# START VIDEO STREAMING
drone.streamon()
skip_start = time.time()

# TAKE OFF
drone.takeoff()

stream = Thread(target = video_stream).start()

while True:
    if activity is ACTIVITY['hovering']:
        pass