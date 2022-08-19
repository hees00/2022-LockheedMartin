from xml.dom.pulldom import START_DOCUMENT
import cv2
import numpy as np
import time
from utils import *

######################################################
width = 640
height = 480
FRAME = 40

PATH = {
  'images': './images/',
  'videos': './videos/',
  'result': './results/practice/',
}

TEST = {
    'detect_QR': 0,
    'identify_COLOR': 1,
    'start_cv': 2,
}
######################################################

test_num = 2

############ TEST : DETECTION OF QR CODE ############
# Video 불러오기
video = cv2.VideoCapture(PATH['videos'] + 'test_02.mp4')

if test_num == TEST['detect_QR']:
    cv2.namedWindow('QR CODE Detection')
    try:
        while video.isOpened():
            # 실행 내역 및 프레임 가져오기
            ret, frame = video.read()
            frame = cv2.resize(frame, (width, height))

            # 실행 내역이 true이면 프레임 출력
            if ret:
                # QR CODE 인식
                detect, frame = read_QR(frame)
                # 프레임 출력
                cv2.imshow('QR CODE Detection', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("예외")
                break

    except Exception as e:
        print(e)

    finally:
        video.release()
        cv2.destroyAllWindows()

############ TEST : DETECTION OF COLOR #############
elif test_num == TEST['identify_COLOR']:
    cv2.namedWindow('COLOR DETECTION')
    try:
        while video.isOpened():
            # 실행 내역 및 프레임 가져오기
            ret, frame = video.read()
            frame = cv2.resize(frame, (width, height))

            # 실행 내역이 true이면 프레임 출력
            if ret:
                detect, frame = identify_color(frame, 'blue')
                cv2.imshow('COLOR DETECTION', frame)


                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("예외")
                break

    except Exception as e:
        print(e)

    finally:
        video.release()
        cv2.destroyAllWindows()

################### TEST : ALL #####################
elif test_num == TEST['start_cv']:
    cv2.namedWindow('COLOR DETECTION')
    startCount = 0
    view_frame = 0

    try:
        while video.isOpened():
            # 실행 내역 및 프레임 가져오기
            ret, frame = video.read()
            frame = cv2.resize(frame, (width, height))

            # 실행 내역이 true이면 프레임 출력
            if ret:
                if startCount == 0:
                    detect, frame = identify_color(frame, 'red')

                    if detect:
                        view_frame += 1
                        if view_frame == FRAME:
                            startCount = 1
                            view_frame = 0
                        
                        elif view_frame == FRAME // 2:
                            cv2.imwrite(PATH['result'] + 'red_marker.jpg', frame)
                
                elif startCount == 1:
                    detect, frame = identify_color(frame, 'blue')

                    if detect:
                        view_frame += 1
                        if view_frame == FRAME:
                            startCount = 2
                            view_frame = 0

                        elif view_frame == FRAME // 2:
                            cv2.imwrite(PATH['result'] + 'blue_marker.jpg', frame)
                
                elif startCount == 2:
                    detect, frame = read_QR(frame)

                    if detect:
                        view_frame += 1
                        if view_frame == FRAME:
                            startCount = 3
                            view_frame = 0

                        elif view_frame == FRAME // 2:
                            cv2.imwrite(PATH['result'] + 'qr_code.jpg', frame)

                cv2.imshow('COLOR DETECTION', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except Exception as e:
        print(e)

    finally:
        video.release()
        cv2.destroyAllWindows()