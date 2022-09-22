from ArmingDrone import ArmingDrone
import cv2
import time

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()

# -10 ~ 10 ↑
# 

# START VIDEO STREAMING
drone.streamon()
print(f'Battery : {drone.get_battery()}/100')
drone.takeoff()

setting = True

while True:

    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (600, 600))
    detect, frame, message = drone.read_qr(frame)

    if detect is False:
        drone.send_rc_control(0, -20, 0, 0)

    elif detect is True:
        drone.hover_sec(5)
        drone.land()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f'Battery : {drone.get_battery()}/100')
        drone.land()
        break