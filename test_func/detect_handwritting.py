import cv2
from ArmingDrone import ArmingDrone

def detect_handwritting():

    # CONNECT TO TELLO
    drone = ArmingDrone()
    drone.connect()

    # START VIDEO STREAMING
    drone.streamon()
    print(f'Battery : {drone.get_battery()}/100')

    while True:
          frame = drone.get_frame_read().frame
          frame = cv2.resize(frame, (800, 640))

          frame, number = drone.detect_number(frame)

          print(number)

          # DISPLAY
          cv2.imshow("TEAM : ARMING", frame)

          if cv2.waitKey(1) & 0xFF == ord('q'):
              print(f'Battery : {drone.get_battery()}/100')
              break