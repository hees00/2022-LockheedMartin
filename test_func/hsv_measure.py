import cv2
import numpy as np
from ArmingDrone import ArmingDrone

def empty():
    pass

def hsv_measure():

    task = input('Select Detect task : (Image / Stream) : ')
    task = task.lower()
    drone = ArmingDrone()

    cv2.namedWindow("HSV")
    cv2.resizeWindow("HSV", drone.WIDTH, drone.HEIGHT)
    # HUE : 색상
    cv2.createTrackbar("HUE Min", "HSV", 20, 179, empty)
    cv2.createTrackbar("HUE Max", "HSV", 40, 179, empty)
    # SAT : 채도
    cv2.createTrackbar("SAT Min", "HSV", 148, 255, empty)
    cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
    # VALUE : 명도
    cv2.createTrackbar("VALUE Min", "HSV", 89, 255, empty)
    cv2.createTrackbar("VALUE Max", "HSV", 250, 255, empty)

    if task == 'stream':
        drone.connect()
        drone.streamon()
    elif task == 'image':
        path = input('Input image file path : ')
        image = cv2.imread(f'./Resources/Images/{path}')

    while True:
        if task == 'stream':
            frame = drone.get_frame_read().frame
        elif task == 'image':
            frame = image
            
        frame = cv2.resize(frame, (drone.WIDTH, drone.HEIGHT))
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
