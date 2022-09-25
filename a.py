import cv2
import time
from ArmingDrone import ArmingDrone

drone = ArmingDrone()
drone.connect()
print(drone.get_battery())

drone.takeoff()
time.sleep(2)


drone.rotate_clockwise(120)
print(drone.get_yaw())

yaw = drone.get_yaw()

# ROTATE TO LOOK AT KAU
rotate = 0
if yaw <= 45 and yaw > -120:
    rotate = -135 - yaw
elif (yaw > 45 and yaw <= 180) or (yaw < -150 and yaw > -180):
    rotate = 225 - yaw

print(rotate)

if rotate >= 20 and rotate < 300:
    drone.rotate_clockwise(rotate)
elif rotate <= -20 and rotate > -300:
    drone.rotate_counter_clockwise(abs(rotate))

print(drone.get_yaw())

drone.land()
