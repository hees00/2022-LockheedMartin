import cv2
from ArmingDrone import ArmingDrone



color = input('Set the color to detect (Black / Green / Blue / Red) : ')

drone = ArmingDrone()
drone.connect()
print(f'Battery : {drone.get_battery()}/100')

drone.streamon()
drone.set_video_fps(drone.FPS_30)
drone.set_video_resolution(drone.RESOLUTION_720P)

number = 0
while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (1280, 1280))

    detect, frame, info = drone.identify_shapes(frame, shapes = 'circle', color = color.lower())

    if detect is True:
        detect_number, frame, number = drone.detect_number(frame, info)
        print(f'DETECT : {detect_number} / Number : {number}')

    cv2.imshow('VIDEO STREAMING', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break