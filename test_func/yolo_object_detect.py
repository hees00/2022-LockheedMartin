import cv2
from ArmingDrone import ArmingDrone

def yolo_object_detect():

    objects = input('Detect Objects (A380 / Apache / F22 / KAU / KT-1) [공백으로 구분] : ').split()
    task = input('Select Detect task : (Image / Stream) : ')
    task = task.lower()

    drone = ArmingDrone()

    if task == 'stream':
        # CONNECT TO TELLO
        drone.connect()

        # START VIDEO STREAMING
        drone.streamon()
        print(f'Battery : {drone.get_battery()}/100')

        drone.setIou(0.1)

        while True:
            frame = drone.get_frame_read().frame
            frame = cv2.resize(frame, (drone.WIDTH, drone.HEIGHT))

            _, frame, info = drone.detect_object(frame, objects = objects)
            print(info)

            # DISPLAY
            cv2.imshow("TEAM : ARMING", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(f'Battery : {drone.get_battery()}/100')
                drone.land()
                break

    elif task == 'image':
        path = input('Image name : ')
        path = f'./Resources/Images/{path}'

        img = cv2.imread(path)
        _, img, info = drone.detect_object(img, objects = objects)

        cv2.imshow("TEAM : ARMING", img)
        cv2.waitKey(0)