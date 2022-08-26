import cv2
import math
import numpy as np
from djitellopy import tello
from pyzbar.pyzbar import decode

from utils import SHAPE


class ArmingDrone(tello.Tello):

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    # Values of HSV Color
    COLOR = {
      'all': [[0, 0, 0], [255, 255, 255]],
      'red': [[0, 0, 50], [50, 50, 255]],
      'blue': [[50, 0, 0], [255, 50, 50]],
      'green': [[0, 50, 0], [50, 255, 50]],
    }

    # Detecting of Shapes
    SHAPE = {
    'triangle': False,
    'rectangle': False,
    'circle': False,
    }


    def __init__(self):
        super.__init__()

    ''' Drone stop ( Hovering ) '''
    def stop():
        super.send_rc_control(0, 0, 0, 0)

    ''' Detect Shapes by color '''
    def identify_shapes(self, frame, shapes = 'all', color = 'all'):
        detect = False

        self.__initShapes()
        if shapes == 'all':
          for shape in SHAPE:
              self.SHAPE[shape] = True
        elif type(shapes) is tuple:
          for shape in shapes:
              self.SHAPE[shape] = True
        elif type(shapes) is str:
            self.SHAPE[shapes] = True

        color = color.lower()
        lower_color = np.array(self.COLOR[color][0])
        upper_color = np.array(self.COLOR[color][1])

        mask = cv2.inRange(frame, lower_color, upper_color)
        mask = cv2.erode(mask, None)

        contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for pts in contours:
            if cv2.contourArea(pts) < 400:
                continue
            approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)
            vtc = len(approx)

            # Triangle ( ▲ )
            if vtc == 3:
                print(f"DETECT COLOR\t:    {color.upper()}")
                self.__setLabel(frame, pts, f'{color.upper()} Marker')
                detect = True

            # Rectangle ( ■ )
            elif vtc == 4:
                print(f"DETECT COLOR\t:    {color.upper()}")
                self.__setLabel(frame, pts, f'{color.upper()} Marker')
                detect = True

            # Circle ( ● )
            elif SHAPE['circle'] and vtc > 4:
                area = cv2.contourArea(pts)
                _, radius = cv2.minEnclosingCircle(pts)

                ratio = radius * radius * math.pi / area

                if int(ratio) == 1:
                    self.__setLabel(frame, pts, f'{color.upper()} Marker')

        return detect, frame
    
    ''' Detect QR CODE '''
    def read_qr(self, frame):
        detect = False
        messages = []

        try:
            # 바코드 정보 decoding
            qrs = decode(frame)
            detect = False

            # 바코드 정보가 여러 개 이기 때문에 하나씩 해석
            for qr in qrs:
                # 바코드 rect정보
                x, y, w, h = qr.rect
                # 바코드 데이터 디코딩
                message = qr.data.decode('utf-8')
                messages.append(message)
                # 인식한 바코드 사각형 표시
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                # 인식한 바코드 사각형 위에 글자 삽입
                cv2.putText(frame, message, (x , y - 20), self.FONT, 0.5, (0, 0, 255), 1)
                detect = True
                print(f'QR CODE\t\t:    {message}')

            return detect, frame, messages

        except Exception as e:
            print(e)

    ''' Start Mission 01 ~ 05 '''
    def start_mission(self, mission_number):
        if mission_number == 1:
            self.move_up(30)
            self.move_down(30)

        elif mission_number == 2:
            self.flip_forward()

        elif mission_number == 3:
            self.move_down(30)
            self.move_up(30)

        elif mission_number == 4:
            self.flip_left()

        elif mission_number == 5:
            self.rotate_clockwise(360)
    
    ''' Draw rectangle and text '''
    def __setLabel(self, frame, points, label):
        # 입력받은 사각형의 정보 추출
        (x, y, w, h) = cv2.boundingRect(points)
        point1 = (x, y)
        point2 = (x + w, y + h)

        # Bounding Box 그리기
        cv2.rectangle(frame, point1, point2, (0, 255, 0), 2)

        # 중심 찾기
        centroid_1= int((x + x + w) / 2)
        centroid_2 = int((y + y + h) / 2)
        centroid = (centroid_1, centroid_2)

        # 중심 원 그리기
        cv2.circle(frame, centroid, 5, (255,255,255), 2)
        # Labeling
        cv2.putText(frame, label, point1, self.FONT, 1, (0, 0, 255))

    ''' Initialization SHAPE '''
    def __initShapes(self):
        for shape in self.SHAPE:
            self.SHAPE[shape] = False
