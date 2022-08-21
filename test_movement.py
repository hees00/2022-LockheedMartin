import tellopy
import av
import cv2
import numpy
import time
from utils import key_init, getKeyboardInput, send_rc_control

'''
Keyboard를 이용하여 Drone을 조종.

Keyboard의 KEY 값을 입력 받으면 드론이 VIDEO streaming도 하고, 동시에 움직임

↑ : forward
↓ : back
← : left
→ : right

w : up
s : down
a : counter-clockwise
d : clockwise
'''

key_init()
# CONNECT TO TELLO
drone = tellopy.Tello()

# drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
drone.connect()
drone.wait_for_connection(60.0)
drone.start_video()

retry = 3
container = None
view_frame = 0
activity = 0

while container is None and 0 < retry:
    retry -= 1
    try:
        container = av.open(drone.get_video_stream())
    except av.AVError as ave:
        print(ave)
        print('retry...')


while True:
    for frame in container.decode(video = 0):
        if 0 < SKIP_FRAME:
            SKIP_FRAME = SKIP_FRAME - 1
            continue

        start_time = time.time()

        vals = getKeyboardInput(drone)
        send_rc_control(drone, vals[0], vals[1], vals[2], vals[3])
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        cv2.imshow('TEAM : Arming', image)

        # FORCE QUIT ( END PROGRAM )
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        SKIP_FRAME = int((time.time() - start_time)/time_base)