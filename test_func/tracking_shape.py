import cv2
from ArmingDrone import ArmingDrone

def tracking_shape():
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
    al_init = drone.get_height()
    
    print(" 이륙 직후 고도 : ",al_init)

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (w, h))

        detect, frame, info = drone.identify_shapes(frame, shapes = shape, color = color)

        if track is True:
            pError, track = drone.track_shape(info, w, pError)
            
        elif track is False and mission is True:
            qr_detect,frame,qr_message = drone.read_qr(frame)

            if qr_detect is False:
                drone.send_rc_control(0, 0, -20, 0)

            elif qr_detect:
                drone.start_mission(eval(qr_message))
                mission = False
                print("qr mission Complete")
                al_now = drone.get_height()
                distance = abs(al_init - al_now)
                if distance > 20:
                    drone.move_up(int(distance))
                print("미션 끝난 후 고도 : ",al_now )
                print("올라간 후 고도 : ",  drone.get_height())

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            cv2.destroyAllWindows()
            break