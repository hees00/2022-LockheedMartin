from test_func.detect_handwritting import detect_handwritting
from test_func.test_mission import test_mission
from test_func.yolo_object_detect import yolo_object_detect
from test_func.hsv_measure import hsv_measure
from test_func.video_stream_for_detect import video_stream_for_detect
from test_func.tracking_object import tracking_object
from test_func.qr_detect import qr_detect

###################### CONFIGURATION #######################
TEST = {
    'detect_handwritting': 1,
    'yolo_object_detect': 2,
    'measure_hsv': 3,
    'basic_video_stream': 4,
    'tracking_shape': 5,
    'detect_qr': 6,
    'test_mission': 7,
}

######################### START ###########################
message = \
'''
============= SELECT TEST =============
1 : Detect handwritting
2 : Detect Object by Yolo
3 : HSV measurements
4 : Basic Drone Video Streaming
5 : Tracking Object
6 : Detect QR Code to hovering
7 : Test Drone Mission
'''

print(message)
option = int(input('SELECT OPTION (1 ~ 7) : '))

while option < 1 or option > 7:
    option = int(input('SELECT OPTION (1 ~ 7) : '))

if option == TEST['detect_handwritting']:
    detect_handwritting()

elif option == TEST['yolo_object_detect']:
    yolo_object_detect()

elif option == TEST['measure_hsv']:
    hsv_measure()

elif option == TEST['basic_video_stream']:
    video_stream_for_detect()

elif option == TEST['tracking_shape']:
    tracking_object()

elif option == TEST['detect_qr']:
    qr_detect()

elif option == TEST['detect_qr']:
    test_mission()