

###################### CONFIGURATION #######################

from .test_func import video_stream_for_detect
from test_func import hsv_measure, tracking_shape, detect_shape_by_color, yolo_object_detect

TEST = {
    'detect_shape': 1,
    'yolo_object_detect': 2,
    'measure_hsv': 3,
    'basic_video_stream': 4,
    'tracking_shape': 5,
}

######################### START ###########################
message = \
'''
============= SELECT TEST =============
1 : Detect Shape by Color
2 : Detect Object by Yolo
3 : HSV measurements
4 : Basic Drone Video Streaming
5 : Tracking Shape
'''

print(message)
option = int(input('SELECT OPTION (1 ~ 5) : '))

while option < 1 or option > 5:
    option = int(input('SELECT OPTION (1 ~ 5) : '))

if option == TEST['detect_shape']:
    detect_shape_by_color()

elif option == TEST['yolo_object_detect']:
    yolo_object_detect()

elif option == TEST['measure_hsv']:
    hsv_measure()

elif option == TEST['basic_video_stream']:
    video_stream_for_detect()

elif option == TEST['tracking_shape']:
    tracking_shape()