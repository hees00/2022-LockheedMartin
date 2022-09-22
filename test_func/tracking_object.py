import cv2
from ArmingDrone import ArmingDrone

def tracking_object():
    pError = 0
    track = True
    mission = True
    w = 600
    h = 600

    objects = input('Detect Objects (A380 / Apache / F22 / KAU / KT-1) [공백으로 구분] : ').split()

    drone = ArmingDrone()
    drone.connect()
    print(drone.get_battery())

    drone.streamon()
    drone.takeoff()
    drone.move_up(30)

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (w, h))

        _, frame, info = drone.detect_object(frame, objects = objects)
        print(info)

        if track is True and len(info) != 0:
            pError, track = drone.track_object(info['KAU'], w, pError, objects = objects[0], speed = 40)
            
        elif track is False:
            print('Track is False')
            drone.land()

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            cv2.destroyAllWindows()
            break