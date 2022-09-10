import cv2
from ArmingDrone import ArmingDrone


def video_stream_for_detect():
    drone = ArmingDrone()
    drone.connect()

    drone.streamon()

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (600, 600))

        detect, frame, info = drone.identify_shapes(frame, shapes = 'circle', color = 'green')
        
        print(f'DETECT : {detect} / info : {info}')

        cv2.imshow('VIDEO STREAMING', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break