from ArmingDrone import ArmingDrone
import cv2
import time


def qr_detect():

    version = int(input('Select Detect QR version (1 / 2) : '))

    # CONNECT TO TELLO
    drone = ArmingDrone()
    drone.connect()

    # START VIDEO STREAMING
    drone.streamon()
    print(f'Battery : {drone.get_battery()}/100')
    drone.takeoff()

    yaw = drone.get_yaw()
    print(yaw)
    setting = True
    toggle = 0

    while True:
        time.sleep(0.03)
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (600, 600))
        detect, frame, message = drone.read_qr(frame)

        if detect is False:
            yaw = drone.get_yaw()
            print(yaw)
            if version == 1:
                drone.send_rc_control(0, -20, 0, 0)

            elif version == 2:
                if setting is True:
                    drone.rotate_counter_clockwise(45)
                    setting = False

                if toggle % 2 == 0:
                    if yaw < 35 and yaw > -45:
                        drone.send_rc_control(0, 0, -15, 40)
                    else:
                        drone.hover_sec(0.5)
                        toggle += 1

                elif toggle % 2 == 1:
                    if yaw < 45 and yaw > -35:
                        drone.send_rc_control(0, 0, -15, -40)
                    else:
                        drone.hover_sec(0.5)
                        toggle += 1

        elif detect is True:
            drone.hover_sec(5)
            print(f'QR Detect !!! / Message : {message}')
            drone.land()

        # DISPLAY
        cv2.imshow("TEAM : ARMING", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'Battery : {drone.get_battery()}/100')
            drone.land()
            break