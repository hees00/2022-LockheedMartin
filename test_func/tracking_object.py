import cv2
import time
from math import sin, cos, radians
from ArmingDrone import ArmingDrone
from start import DISTANCE

def tracking_object():
    pError = 0
    track = True
    mission = True
    DISTANCE = 100

    objects = input('Detect Objects (A380 / Apache / F22 / KAU / KT-1) : ').split()

    drone = ArmingDrone()
    drone.connect()
    print(drone.get_battery())

    drone.streamon()
    drone.takeoff()
    drone.move_up(30)

    time.sleep(3)
    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (drone.WIDTH, drone.HEIGHT))

        _, frame, info = drone.detect_object(frame, objects = objects)
        print(info)

        if track is True and len(info) != 0:
            pError, track = drone.track_object(info[objects[0]], pError, objects = objects[0], speed = 25)
            
        elif track is False:
            drone.hover_sec(1)
            yaw = drone.get_yaw()

            # Calculate degree and rotate
            degree = 0                
            rotate = 0
            left = False
            if yaw >= 135 and yaw <= 180:
                degree = yaw - 135
                rotate = 225 - yaw
            elif yaw >= -180 and yaw < -135:
                degree = 225 - yaw
                rotate = yaw - 135
            elif yaw <= -45 and yaw >= -135:
                left = True
                degree = abs(yaw - 45)
                rotate = -135 - yaw
                
            # View in F22 Direction
            if rotate >= 20:
                drone.rotate_clockwise(rotate)
            elif rotate <= -20:
                drone.rotate_counter_clockwise(abs(rotate))
            else:
                drone.move_sec([0, 0, 0, rotate], 1)

            # Go landing zone
            rad = radians(degree)
            h = DISTANCE * sin(rad)
            fb = h - 40
            lr = DISTANCE * cos(rad)

            if left is True:
                lr = -lr
            
            drone.move_sec([lr, 0, 0, 0], 1)
            drone.hover_sec(0.5)
            drone.move_sec([0, fb, 0, 0], 1)
            drone.hover_sec(0.5)
            print('Arming Drone Landing !!!')
            drone.land()

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break