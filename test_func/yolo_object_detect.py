from ArmingDrone import ArmingDrone
import cv2

def yolo_object_detect():

    objects = input('Detect Objects (A380 / Apache / F22 / KAU_Marker / KT-1) [공백으로 구분] : ').split()

    # CONNECT TO TELLO
    drone = ArmingDrone()
    drone.connect()

    # START VIDEO STREAMING
    drone.streamon()
    print(f'Battery : {drone.get_battery()}/100')

    while True:
          frame = drone.get_frame_read().frame
          frame = cv2.resize(frame, (800, 640))

          frame, info = drone.detect_object(frame, objects = objects)

          # DISPLAY
          cv2.imshow("TEAM : ARMING", frame)

          if cv2.waitKey(1) & 0xFF == ord('q'):
              print(f'Battery : {drone.get_battery()}/100')
              drone.land()
              break

