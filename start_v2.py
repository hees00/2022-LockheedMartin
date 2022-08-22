import tellopy
import av
import cv2
import numpy
import time
from utils import identify_color, read_QR, stop


'''
예상 문제점

1. time.sleep을 했을 때, 영상 스트리밍은 ? → continue로 해결
2. 만약, cv2.imshow를 맨 아래에 놓는다면 continue 사용 시 이미지 출력 X → sleep 하는 부분(if 문) 내에 추가로 cv2.imshow를 넣어줌
3. Blue or Green 탐지할 때, 단순 clockwise로만 했을 때 찾지 못할 경우 → 

'''


def main():

        ##################### CONFIGURATION #########################
        width = 700
        height = 700

        VIEW_FRAME = 60
        CAPTURE_FRAME = VIEW_FRAME - 20
        SKIP_FRAME = 300
        PER_FRAME = 33
        CLOCKWISE = 6

        PATH = {
        'images': './images/',
        'videos': './videos/',
        'result': './results/real/',
        }

        ACTIVITY = {
        'takeoff': 0,
        'red': 1,
        'b_g': 2,
        'qr': 3,
        'land': 4,
        }

        SWITCH = {
        'takeoff': True,
        'down': True,
        'up': True,
        'clockwise': True,
        'qr_clockwise': True
        }

        SLEEP = {
            'takeoff': 2,
            'down': 1,
            'clockwise': 1,
            'stop_red': 2,
            'stop_b_g': 1,
            'stop_qr': 1,
        }

        VELOCITY = {
            'down': 60,
            'down_s': 20,
            'clockwise': 60,
        }


        ###########################################################

        def handler(event, sender, data, **args):
            drone = sender
            if event is drone.EVENT_FLIGHT_DATA:
                # print(data)
                pass

        retry = 3
        container = None
        view_frame = 0
        cnt_frame = 0
        activity = 0
        first_down = True
        cnt_clockwise = 0
        sec = 0

        # CONNECT TO TELLO
        drone = tellopy.Tello()
        drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)

        # drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
        drone.connect()
        drone.wait_for_connection(60.0)
        drone.start_video()

        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        drone.takeoff()
        time.sleep(3)
        activity = ACTIVITY['red']


        while True:
            for frame in container.decode(video = 0):
                if 0 < SKIP_FRAME:
                    SKIP_FRAME = SKIP_FRAME - 1
                    continue

                start_time = time.time()
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                
                ############################## MOVE  & DETECT ###############################
                
                if activity == ACTIVITY['red']:                                               # DETECT RED : 빨간색 사각형 탐지

                    detect, image = identify_color(image, 'red')

                    if SWITCH['down'] is True:
                        if first_down: 
                            drone.down(VELOCITY['down'])
                            first_down = False
                        else: drone.down(VELOCITY['down_s'])
                        ''' time.sleep(SLEEP['down']) '''
                        sec = cnt_frame / PER_FRAME
                        if sec < SLEEP['down']:
                            cnt_frame += 1
                            # STREAMING
                            cv2.imshow('TEAM : Arming', image)
                            continue

                        cnt_frame = 0
                    if detect is True:
                        view_frame =  view_frame + 1
                        SWITCH['down'] = False

                        if view_frame == CAPTURE_FRAME:
                            stop(drone)
                            ''' time.sleep(SLEEP['stop_red']) '''
                            # sec = cnt_frame / PER_FRAME

                            # if sec < SLEEP['stop_red']:
                            #     print(activity)
                            #     cnt_frame += 1
                            #     # STREAMING
                            #     cv2.imshow('TEAM : Arming', image)
                            #     continue

                            cnt_frame = 0
                            cv2.imwrite(PATH['result'] + 'red_marker.jpg', image)

                        elif view_frame == VIEW_FRAME:
                            activity = ACTIVITY['b_g']
                            view_frame = 0

                elif activity == ACTIVITY['b_g']:                                               # DETECT BLUE OR GREEN : 파란색 또는 초록색 사각형 탐지

                    detect, image = identify_color(image, 'green')

                    if SWITCH['clockwise'] is True:
                        drone.clockwise(VELOCITY['clockwise'])
                        ''' time.sleep(SLEEP['clockwise']) '''
                        sec = cnt_frame / PER_FRAME
                        if sec < SLEEP['clockwise']:
                            cnt_frame += 1
                            # STREAMING
                            cv2.imshow('TEAM : Arming', image) 
                            continue

                        cnt_frame = 0

                    if detect is True:
                        view_frame += 1
                        SWITCH['clockwise'] = False

                        if view_frame == CAPTURE_FRAME:
                            stop(drone)

                            ''' time.sleep(SLEEP['stop_b_g']) '''
                            sec = cnt_frame / PER_FRAME
                            # if sec < SLEEP['stop_b_g']:
                            #     cnt_frame += 1
                            #     # STREAMING
                            #     cv2.imshow('TEAM : Arming', image)
                            #     continue
                            
                            cnt_frame = 0
                            cv2.imwrite(PATH['result'] + 'green_marker.jpg', image)

                        elif view_frame == VIEW_FRAME:
                            activity = ACTIVITY['qr']
                            view_frame = 0

                elif activity == ACTIVITY['qr']:                                                # DETECT QR CODE : QR 코드 탐지

                    detect, image = read_QR(image)

                    if SWITCH['qr_clockwise'] is True:
                        drone.clockwise(VELOCITY['clockwise'])

                        ''' time.sleep(SLEEP['clockwise'])'''
                        sec = cnt_frame / PER_FRAME
                        if sec < SLEEP['stop_qr']:
                            cnt_frame += 1
                            # STREAMING
                            cv2.imshow('TEAM : Arming', image)
                            continue

                        cnt_frame = 0

                    if detect is True:
                        view_frame += 1
                        SWITCH['qr_clockwise'] = False

                        if view_frame == CAPTURE_FRAME:
                            stop(drone)

                            ''' time.sleep(SLEEP['stop_qr']) '''
                            sec = cnt_frame / PER_FRAME
                            # if sec < SLEEP['stop_qr']:
                            #     # STREAMING
                            #     cv2.imshow('TEAM : Arming', image)
                            #     cnt_frame += 1
                            #     continue

                            cnt_frame = 0
                            cv2.imwrite(PATH['result'] + 'qr_code.jpg', image)

                        elif view_frame == VIEW_FRAME:
                            activity = ACTIVITY['land']
                            view_frame = 0

                elif activity == ACTIVITY['land']:                                              # LAND : 착륙
                    drone.land()
                    break

                # STREAMING
                cv2.imshow('TEAM : Arming', image)
                ############################################################################

                # FORCE QUIT ( END PROGRAM )
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    drone.land()
                    break

                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                SKIP_FRAME = int((time.time() - start_time)/time_base)

if __name__ == "__main__":
    main()