import cv2
import time
from ArmingDrone import ArmingDrone
from math import sin, cos, radians

DISTANCE = 80

drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

drone.takeoff()
time.sleep(5)


drone.rotate_clockwise(200)
drone.hover_sec(1)
yaw = drone.get_yaw()

# Calculate degree and rotate
degree = 0                
rotate = 0
right = False
if yaw >= 135 and yaw <= 180:
    degree = yaw - 135
    rotate = 225 - yaw
elif yaw >= -180 and yaw < -135:
    degree = 225 + yaw
    rotate = -135 - yaw
elif yaw <= -45 and yaw >= -135:
    right = True
    degree = -35 - yaw
    rotate = -135 - yaw
    
# View in F22 Direction
if rotate >= 20:
    drone.rotate_clockwise(rotate)
elif rotate <= -20:
    drone.rotate_counter_clockwise(abs(rotate))
else:
    drone.move_sec([0, 0, 0, rotate], 1)

# Go landing zone
rad = radians(degree)
h = int(DISTANCE * sin(rad))
fb = h

lr = int(DISTANCE * cos(rad)) - 15
fb = max(fb, 20)
lr = max(lr, 20)

if right is False:
    drone.move_left(lr)
else:
    drone.move_right(lr)

drone.move_forward(fb)

print('Arming Drone Landing !!!')
print(f'Rotate : {rotate} / Degree : {degree} / fb : {fb} / lr : {lr} / yaw : {yaw}')
print(f'Rotate : {rotate} / Degree : {degree} / fb : {fb} / lr : {lr} / yaw : {yaw}')
drone.land()



drone.land()
