import cv2
import time
from ArmingDrone import ArmingDrone

def tracking_object():
    pError = 0
    track = True
    mission = True

    objects = input('Detect Objects (A380 / Apache / F22 / KAU / KT-1) : ').split()

    drone = ArmingDrone()
    drone.connect()
    print(drone.get_battery())

    drone.streamon()
    drone.takeoff()
    drone.move_up(120)

    time.sleep(3)
    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (drone.WIDTH, drone.HEIGHT))

        _, frame, info = drone.detect_object(frame, objects = objects)
        print(info)

        if track is True and len(info) != 0:
            pError, track = drone.track_object(info[objects[0]], pError, objects = objects[0], speed = 40)
            
        elif track is False:
            print('Track is False')
            drone.hover()

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            cv2.destroyAllWindows()
            break