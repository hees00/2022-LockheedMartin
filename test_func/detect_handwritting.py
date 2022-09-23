import cv2
from ArmingDrone import ArmingDrone

def detect_handwritting():

    task = input('Select Detect task : (Image / Stream) : ')
    task = task.lower()

    drone = ArmingDrone()

    if task == 'stream':
        # CONNECT TO TELLO
        
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
    
    elif task == 'image':
        image_name = input('Enter the name of the file to detect : ')
        color = input('Input Detect Color : (Black / Blue / Red) : ')
        frame = cv2.imread(f'./Resources/Images/number/{image_name}.jpg')
        frame = cv2.resize(frame, (drone.WIDTH, drone.HEIGHT))

        detect, frame, info = drone.identify_shapes(frame, shapes = 'circle', color = color)
        detect_number, frame, number = drone.detect_number(frame, info)
        print(f'DETECT : {detect_number} / Number : {number}')

        cv2.imshow('VIDEO STREAMING', frame)
        cv2.waitKey(0)
