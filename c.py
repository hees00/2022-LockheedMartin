from ArmingDrone import ArmingDrone
import time

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()

# -10 ~ 10 ↑
# 

# START VIDEO STREAMING
drone.streamon()
print(f'Battery : {drone.get_battery()}/100')
drone.takeoff()

# ↑
# drone.go_xyz_speed(-150, 150, 10, 100)

print(drone.get_yaw())
drone.rotate_counter_clockwise(30)
print(drone.get_yaw())

# →
drone.go_xyz_speed(-150, -150, 50, 100)


time.sleep(3)
drone.land()

