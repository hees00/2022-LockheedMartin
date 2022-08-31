import cv2
import time
from threading import Thread
from utils import *
from ArmingDrone import ArmingDrone

###################### CONFIGURATION #######################
width = 640
height = 480
FRAME = 60

PATH = {
  'images': './Resources/Images/',
  'videos': './Resources/Videos/',
  'result': './results/practice/',
  'log': './results/log/',
}

TEST = {
    'detect_shape': 1,
    'test_drone_move': 2,
    'measure_hsv': 3,
    'basic_video_stream': 4,
    'tracking_shape': 5,
}

def empty():
    pass


######################## FUNCTION #########################
def detect_shape_by_color():
    select = int(input('Select Test (Image = 1 / Video = 2) : '))
    color = input('Enter a color to identify (red / green / blue) : ')
    shape = input('Enter a shape to identify (triangle / rectangle / circle) : ')
    

    cv2.namedWindow('DETECT CIRCLE BY COLOR')

    if select == 1:
        use_shape = input('Enter a shape to check (triangle / rectangle / circle) : ')
        src = input('Test file name : ')
        path = PATH['images'] + f'{use_shape}/' + src
        image = cv2.imread(path)

        if image is None:
            print('Image open failed!')
            return

        image = cv2.resize(image, (width, height))
        
        detect, image, info = identify_shapes(image, shapes = shape, color = color)
        print(f'DETECT : {detect}')
        cv2.imshow('DETECT CIRCLE BY COLOR', image)
        print(info)

        cv2.waitKey(0)

    elif select == 2:
        src = input('Test file name : ')
        path = PATH['videos'] + src
        video = cv2.VideoCapture(path)

        try:
            while video.isOpened():
                # 실행 내역 및 프레임 가져오기
                ret, frame = video.read()
                frame = cv2.resize(frame, (width, height))

                # 실행 내역이 true이면 프레임 출력
                if ret:
                    detect, frame, info = identify_shapes(frame, shapes = shape, color = color)

                    cv2.imshow('DETECT CIRCLE BY COLOR', frame)
                    print(info)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    print("예외")
                    break

        except Exception as e:
            print(e)

        finally:
            video.release()
            cv2.destroyAllWindows()

    else:
        print("Please enter valid values.")
        return

def test_drone_move():
    message = \
    '''
    ============= SELECT TEST =============
    1 : UP
    2 : DOWN
    3 : RIGHT
    4 : LEFT
    5 : CLOCKWISE
    6 : COUNTER-CLOCKWISE
    7 : FLIP
    0 : END
    '''

    COMMAND = {
        1: 'UP',
        2: 'DOWN',
        3: 'RIGHT',
        4: 'LEFT',
        5: 'CLOCKWISE',
        6: 'COUNTER-CLOCKWISE',
        7: 'FLIP'
    }
    sequence = []
    command = None
    speed = 0
    dir = None

    # CONNECT TO TELLO
    drone = ArmingDrone()
    drone.connect()
    print(drone.get_battery())

    # START VIDEO STREAMING
    drone.streamon()

    # INPUT TEST COMMAND
    while True:
        print(message)
        command = int(input('Input move to test : '))

        if command <= 4:
            speed = int(input('Input moving speed (20 ~ 500) : '))
            command_info = (command, speed)
        elif command == 5 or command == 6:
            speed = int(input('Input moving angle (1 ~ 360) :'))
            command_info = (command, speed)
        elif command == 7:
            direction = input('Input flip direction (forward = l / back = r / right = f / left = b) :')
            command_info = (command, direction)
        elif command == 0:
            break
        else:
            continue
        
        sequence.append(command_info)

    
    num = len(sequence)
    switch = True
    index = 0
    sec = 0

    # DRONE TAKEOFF
    drone.takeoff()

    # START TEST
    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (600, 600))

        command = sequence[num]
        move = command[0]
        val = command[1]

        if switch is True:
            if COMMAND[move] == 'UP':
                drone.move_up(val)
            elif COMMAND[move] == 'DOWN':
                drone.move_down(val)
            elif COMMAND[move] == 'RIGHT':
                drone.move_right(val)
            elif COMMAND[move] == 'LEFT':
                drone.move_left(val)
            elif COMMAND[move] == 'CLOCKWISE':
                drone.rotate_clockwise(val)
            elif COMMAND[move] == 'COUNTER-CLOCKWISE':
                drone.rotate_counter_clockwise(val)
            elif COMMAND[move] == 'FLIP':
                drone.flip(val)
            
            start = time.time()
            
            switch = False
        
        else:
            end = time.time()
            sec = end - start
            cv2.imshow("TEST MOVE", frame)

            if sec < 2:
                continue

            index += 1
            
            if index == num:
                drone.land()
                break

        cv2.imshow("TEST MOVE", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

def hsv_measure():

    cv2.namedWindow("HSV")
    cv2.resizeWindow("HSV", 640, 240)
    # HUE : 색상
    cv2.createTrackbar("HUE Min", "HSV", 20, 179, empty)
    cv2.createTrackbar("HUE Max", "HSV", 40, 179, empty)
    # SAT : 채도
    cv2.createTrackbar("SAT Min", "HSV", 148, 255, empty)
    cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
    # VALUE : 명도
    cv2.createTrackbar("VALUE Min", "HSV", 89, 255, empty)
    cv2.createTrackbar("VALUE Max", "HSV", 250, 255, empty)

    drone = ArmingDrone()
    drone.connect()

    drone.streamon()

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (600, 600))
        frameHsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h_min = cv2.getTrackbarPos("HUE Min", "HSV")
        h_max = cv2.getTrackbarPos("HUE Max", "HSV")
        s_min = cv2.getTrackbarPos("SAT Min", "HSV")
        s_max = cv2.getTrackbarPos("SAT Max", "HSV")
        v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
        v_max = cv2.getTrackbarPos("VALUE Max", "HSV")

        lower = np.array([h_min, s_min, v_min], dtype = np.uint8)
        upper = np.array([h_max, s_max, v_max], dtype = np.uint8)

        mask = cv2.inRange(frameHsv, lower, upper)
        res = cv2.bitwise_and(frame, frame, mask = mask)
        (h, s, v) = cv2.split(res)

        blur = cv2.medianBlur(s, 5)
        el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        tmp = cv2.erode(blur, el, iterations = 1)
        (_, mask) = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)

        cv2.imshow('mask', mask)
        cv2.imshow('Original', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()  

    
def basic_drone_video_streaming():
    drone = ArmingDrone()
    drone.connect()

    drone.streamon()

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (600, 600))

        detect, frame, info = drone.identify_shapes(frame, shapes = 'rectangle', color = 'green')
        
        print(f'DETECT : {detect} / info : {info}')

        cv2.imshow('VIDEO STREAMING', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

def tracking_shape():
    pError = 0
    track = True
    mission = True
    w = 600
    h = 600

    shape = input('Enter a shape to track ( Rectangle / Circle ) : ')
    color = input('Enter a color to detect ( Red / Blue / Green ) : ')
    shape = shape.lower()
    color = color.lower()

    drone = ArmingDrone()
    drone.connect()
    print(drone.get_battery())

    drone.streamon()
    drone.takeoff()

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (w, h))

        detect, frame, info = drone.identify_shapes(frame, shapes = shape, color = color)

        if track is True:
            pError, track = drone.track_shape(info, w, pError)
        elif track is False and mission is True:
            drone.start_mission(1)
            drone.rotate_clockwise(180)
            drone.move_up(30)
            mission = False
            print("Finish")

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            cv2.destroyAllWindows()
            break


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
    test_drone_move()

elif option == TEST['measure_hsv']:
    hsv_measure()

elif option == TEST['basic_video_stream']:
    basic_drone_video_streaming()

elif option == TEST['tracking_shape']:
    tracking_shape()