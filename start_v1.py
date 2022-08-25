from ArmingDrone import ArmingDrone
import cv2
import time

##################### CONFIGURATION #########################
width = 700
height = 700

RED_VIEW_PRAME = 90
VIEW_FRAME = 60
CAPTURE_FRAME = VIEW_FRAME - 20
SKIP_FRAME = 300
PER_FRAME = 33

PATH = {
'images': './images/',
'videos': './videos/',
'result': './results/real/',
}

ACTIVITY = {
'takeoff': 0,
'red': 1,
'b_g': 2,
'qr': 3,
'land': 4,
}

SWITCH = {
'takeoff': True,
'down': True,
'up': True,
'clockwise': True,
'qr_clockwise': True
}

SLEEP = {
  'takeoff': 2,
  'down': 1,
  'clockwise': 1,
  'stop_red': 2,
  'stop_b_g': 1,
  'stop_qr': 1,
}

VELOCITY = {
  'down': 60,
  'down_s': 20,
  'clockwise': 60,
}

CLOCKWISE = 360 // VELOCITY['clockwise']

##################### START TELLO ########################

 # CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

# START VIDEO STREAMING
drone.streamon()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (width, height))

    #################### HOVERING ########################


    #################### DETECT G ########################


    #################### DETECT R ########################


    #################### DETECT B ########################


    cv2.imshow("TEAM : ARMING", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break