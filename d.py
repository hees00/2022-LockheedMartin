import cv2
from ArmingDrone import ArmingDrone

drone = ArmingDrone()

frame = cv2.imread('two.jpg')
frame = cv2.resize(frame, (600, 600))

detect, frame, info = drone.identify_shapes(frame, shapes = 'circle', color = 'red')
detect_number, frame, number = drone.detect_number(frame, info)
print(f'DETECT : {detect_number} / Number : {number}')

cv2.imshow('VIDEO STREAMING', frame)
cv2.waitKey(0)