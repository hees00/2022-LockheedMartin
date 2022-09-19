from ArmingDrone import ArmingDrone

# CONNECT TO TELLO
drone = ArmingDrone()
drone.connect()

# -10 ~ 10 ↑
# 

# START VIDEO STREAMING
drone.streamon()
print(f'Battery : {drone.get_battery()}/100')
drone.takeoff()


print(drone.get_yaw())
drone.land()

