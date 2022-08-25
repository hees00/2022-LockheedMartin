from ArmingDrone import ArmingDrone
import cv2
import time
import pygame

'''
Keyboard를 이용하여 Drone을 조종.

Keyboard의 KEY 값을 입력 받으면 드론이 VIDEO streaming도 하고, 동시에 움직임

r : takeoff
e : land
f : stop

↑ : forward
↓ : back
← : left
→ : right

w : up
s : down
a : counter-clockwise
d : clockwise

'''

def main():
        def key_init():
            pygame.init()
            window = pygame.display.set_mode((400, 400))

        def getKey(keyName):
            ans = False
            for eve in pygame.event.get():  pass
            keyInput = pygame.key.get_pressed()
            myKey = getattr(pygame, 'K_{}'.format(keyName))

            if keyInput[myKey]:
                ans = True
            
            pygame.display.update()

            return ans

        def getKeyboardInput(drone):
            lr, fb, ud, yv = 0, 0, 0, 0
            speed = 50
            
            # TAKEOFF / LAND / STOP
            if getKey("r"): drone.takeoff()
            if getKey("e"): drone.land()
            if getKey("f"): drone.stop()

            # LEFT OR RIGHT
            if getKey("LEFT"): lr = -speed
            elif getKey("RIGHT"): lr = speed

            # FORWARD OR BACKWARD
            if getKey("UP"): fb = speed
            elif getKey("DOWN"): fb = -speed

            # UP OR DOWN
            if getKey("w"): ud = speed
            elif getKey("s"): ud = -speed

            # CLOCKWISE AND COUNTER_CLOCKWISE
            if getKey("a"): yv = speed
            elif getKey("d"): yv = -speed

            # CAPTURE
            if getKey('z'):
                cv2.imwrite(f'Resources/Images/{time.time()}.jpg', img)




            return [lr, fb, ud, yv]


        key_init()
        global img

        # CONNECT TO TELLO
        drone = ArmingDrone()
        drone.connect()
        print(drone.get_battery())

        drone.streamon()

        while True:
            vals = getKeyboardInput(drone)
            drone.send_rc_control(vals[0], vals[1], vals[2], vals[3])
            
            img = drone.get_frame_read().frame
            img = cv2.resize(img, (600, 600))

            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                drone.land()
                
if __name__ == "__main__":
    main()