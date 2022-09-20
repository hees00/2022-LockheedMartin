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


drone.start_mission(4)
time.sleep(3)
drone.land()

