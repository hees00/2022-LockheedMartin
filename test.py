

###################### CONFIGURATION #######################

from test_func import hsv_measure, tracking_shape, video_stream_for_detect, detect_shape_by_color

TEST = {
    'detect_shape': 1,
    'test_drone_move': 2,
    'measure_hsv': 3,
    'basic_video_stream': 4,
    'tracking_shape': 5,
}

######################### START ###########################
message = \
'''
============= SELECT TEST =============
1 : Detect Shape by Color
2 : Test Drone Movement
3 : Video Streaming for HSV measurements
4 : Basic Drone Video Streaming
5 : Tracking Shape
'''

print(message)
option = int(input('SELECT OPTION (1 ~ 5) : '))

while option < 1 or option > 5:
    option = int(input('SELECT OPTION (1 ~ 5) : '))

if option == TEST['detect_shape']:
    detect_shape_by_color()

elif option == TEST['test_drone_move']:
    pass

elif option == TEST['measure_hsv']:
    hsv_measure()

elif option == TEST['basic_video_stream']:
    video_stream_for_detect()

elif option == TEST['tracking_shape']:
    tracking_shape()