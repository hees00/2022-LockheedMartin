from threading import Thread
import cv2
import time
import numpy as np
import av

from ArmingDrone import ArmingDrone

def streaming():

    while True:
        # GET THE IMAGE FROM TELLO
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (width, height))
        cv2.imshow('Move', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

######################################################
width = 640
height = 480
######################################################

switch = False

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()
drone.streamon()

drone.takeoff()

drone.send_rc_control(0, 50, 0, 0)
drone.land()
