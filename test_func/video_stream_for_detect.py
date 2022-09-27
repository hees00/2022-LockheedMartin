import cv2
from ArmingDrone import ArmingDrone

def video_stream_for_detect():

    color = input('Set the color to detect (Black / Green / Blue / Red) : ')

    drone = ArmingDrone()
    drone.connect()
    print(f'Battery : {drone.get_battery()}/100')
    
    drone.streamon()
    drone.set_video_fps(drone.FPS_30)
    drone.set_video_resolution(drone.RESOLUTION_720P)

    while True:
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (drone.WIDTH, drone.HEIGHT))

        detect, frame, info = drone.identify_shapes(frame, shapes = 'circle', color = color.lower())
        
        print(f'DETECT : {detect} / info : {info}')

        cv2.imshow('VIDEO STREAMING', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break