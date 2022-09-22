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
  'find_f22': 2,
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
    'detect_kau': True,
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

# def streaming():
#     print('Team Arming : Start Video Stream')
#     global course, detect_qr, message, detect_marker, info, activity, pError, mission, color, detect_hw, detect_objects

#     course = COURSE['recognition_flag']
#     activity = ACTIVITY['hovering']
#     detect_qr = False
#     message = False
#     pError = 0
#     mission = 0
#     color = None
#     detect_hw = False

#     while True:
#         frame = drone.get_frame_read().frame
#         frame = cv2.resize(frame, (WIDTH, HEIGHT))

#         # DISPLAY
#         cv2.imshow("TEAM : ARMING", frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print(f'Battery : {drone.get_battery()}/100')
#             drone.land()
#             break

