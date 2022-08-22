# import tellopy
# import av
# import cv2
# import numpy
# import time
# import pygame
# from utils import stop, send_rc_control

# '''
# Keyboard를 이용하여 Drone을 조종.

# Keyboard의 KEY 값을 입력 받으면 드론이 VIDEO streaming도 하고, 동시에 움직임

# r : takeoff
# e : land
# f : stop

# ↑ : forward
# ↓ : back
# ← : left
# → : right

# w : up
# s : down
# a : counter-clockwise
# d : clockwise

# '''

# def key_init():
#     pygame.init()
#     window = pygame.display.set_mode((400, 400))

# def getKey(keyName):
#     ans = False
#     for eve in pygame.event.get():  pass
#     keyInput = pygame.key.get_pressed()
#     myKey = getattr(pygame, 'K_{}'.format(keyName))

#     if keyInput[myKey]:
#         ans = True
    
#     pygame.display.update()

#     return ans

# def getKeyboardInput(drone):
#     lr, fb, ud, yv = 0, 0, 0, 0
#     speed = 50 / 100.0

#     if getKey("LEFT"): lr = -speed
#     elif getKey("RIGHT"): lr = speed

#     if getKey("UP"): fb = speed
#     elif getKey("DOWN"): fb = -speed

#     if getKey("w"): ud = speed
#     elif getKey("s"): ud = -speed

#     if getKey("a"): yv = speed
#     elif getKey("d"): yv = -speed

#     if getKey("r"): drone.takeoff()
#     if getKey("e"): drone.land()
#     if getKey("f"): stop(drone)


#     return [lr, fb, ud, yv]


# key_init()
# # CONNECT TO TELLO
# drone = tellopy.Tello()

# # drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
# drone.connect()
# drone.wait_for_connection(60.0)

# retry = 3
# container = None
# view_frame = 0
# activity = 0
# SKIP_FRAME = 300

# while container is None and 0 < retry:
#     retry -= 1
#     try:
#         container = av.open(drone.get_video_stream())
#     except av.AVError as ave:
#         print(ave)
#         print('retry...')


# while True:
#     for frame in container.decode(video = 0):
#         if 0 < SKIP_FRAME:
#             SKIP_FRAME = SKIP_FRAME - 1
#             continue

#         start_time = time.time()

#         vals = getKeyboardInput(drone)
#         send_rc_control(drone, vals[0], vals[1], vals[2], vals[3])
#         image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
#         cv2.imshow('TEAM : Arming', image)

#         # FORCE QUIT ( END PROGRAM )
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             drone.land()
#             break

#         if frame.time_base < 1.0/60:
#             time_base = 1.0/60
#         else:
#             time_base = frame.time_base
#         SKIP_FRAME = int((time.time() - start_time)/time_base)