from time import sleep
import tellopy
import cv2
import time

al = 0


def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        al = data.height


def controll_drone(cmd,p):
    if cmd == "stop":
        drone.up(0)
        drone.down(0)
        drone.clockwise(0)
        drone.forward(0)
        drone.backward(0)
        drone.right(0)
        drone.left(0)
        print("stop")
    elif cmd == "down":
        drone.down(p)
        controll_drone("stop",0)
        print("down ",p)
    elif cmd == "up":
        drone.up(p)
        controll_drone("stop",0)
        print("up ",p)
    elif cmd == "clocckwise":
        print("clockwise ",p)
        drone.clockwise(p)
        time.sleep(3)
        controll_drone("stop",0)



def test():
    global drone
    drone = tellopy.Tello()
    try:
        drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)

        drone.connect()
        drone.wait_for_connection(60.0)
        drone.takeoff()
        sleep(5)
        drone.down(10)
        sleep(5)
        
    except Exception as ex:
        print(ex)

    while(1):
        print("******고도 : ", al , "   **************")
        if al < 5:
            drone.up(10)
            sleep(5)
        if al > 100:
            drone.down(10)
            sleep(5)
            
        key = cv2.waitKey(1)
        if key == ord("u"):
            controll_drone("up",10)
        elif key == ord("d"):
            controll_drone("down",10)
        elif key == ord("s"):
            controll_drone("stop",0)
        elif key == ord("c"):
            controll_drone("clockwise",20)
        elif key == ord("q"):
            drone.land()
            break
    
    drone.quit()

if __name__ == '__main__':
    test()
