from ArmingDrone import ArmingDrone
import time


def test_mission():
    mission = int(input('Input mission number (1 ~ 9) : '))

    # CONNECT TO TELLO
    drone = ArmingDrone()
    drone.connect()

    # START VIDEO STREAMING
    print(f'Battery : {drone.get_battery()}/100')
    drone.takeoff()

    drone.start_mission(mission)

    time.sleep(2)
    drone.land()