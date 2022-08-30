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
      'red': [[161, 155, 84], [179, 255, 255]],
      'blue': [[94, 80, 2], [126, 255, 255]],
      'green': [[25, 52, 72], [102, 255, 255]],
    }

    # Detecting of Shapes
    SHAPE = {
        'triangle': False,
        'rectangle': False,
        'circle': False,
    }

    MOVE = {
        'shape': [10000, 10500],
    }

    PID = [0.4, 0.4, 0]


    ''' Drone stop ( Hovering ) '''
    # def stop():
    #     super.send_rc_control(0, 0, 0, 0)
        
    ''' Detect Shapes by color '''
    def identify_shapes(self, frame, shapes = 'all', color = 'all'):
        detect = False
        info = ((0, 0), (0, 0), (0, 0), 0)
        tri, rec, cir = False, False, False

        if shapes == 'all':
            tri, rec, cir = True, True, True
        elif shapes == 'triangle':
            tri = True
        elif shapes == 'rectangle':
            rec = True
        elif shapes == 'circle':
            cir = True

        color = color.lower()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_color = np.array(self.COLOR[color][0], dtype = np.uint8)
        upper_color = np.array(self.COLOR[color][1], dtype = np.uint8)

        mask = cv2.inRange(hsv, lower_color, upper_color)
        res = cv2.bitwise_and(frame, frame, mask = mask)
        (h, s, v) = cv2.split(res)
        
        blur = cv2.medianBlur(s, 5)
        el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        tmp = cv2.erode(blur, el, iterations = 1)

        (_, mask) = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)

        cv2. imshow('mask', mask)
        contours,_ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for pts in contours:
            if cv2.contourArea(pts) < 100:
                continue
            approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)
            vtc = len(approx)

            # Triangle ( ▲ )
            if tri and vtc == 3:
                info = self.__getRectInfo(pts)
                print(f"DETECT COLOR\t:    {color.upper()}")
                self.__setLabel(frame, info, f'{color.upper()} Marker')
                detect = True

            # Rectangle ( ■ )
            elif rec and vtc == 4:
                info = self.__getRectInfo(pts)
                print(f"DETECT COLOR\t:    {color.upper()}")
                self.__setLabel(frame, info, f'{color.upper()} Marker')
                detect = True

            # Circle ( ● )
            elif cir and vtc == 8:
                info = self.__getRectInfo(pts)
                print(info)
                area = cv2.contourArea(pts)
                _, radius = cv2.minEnclosingCircle(pts)

                ratio = radius * radius * math.pi / area

                if int(ratio) == 1:
                    print(f"DETECT COLOR\t:    {color.upper()}")
                    self.__setLabel(frame, info, f'{color.upper()} Marker')
                    detect = True

        return detect, frame, info
    
    ''' Drone track shapes '''
    def track_shape(self, info, w, pError):
        speed = 24      # 20 ~ 28
        track = True

        x, y = info[2]
        area = info[3]
        fb = 0

        # REGULATE YAW : yaw ( Angle )
        error = x - w // 2
        yaw = self.PID[0] * error + self.PID[1] * (error - pError)
        yaw = int(np.clip(yaw, -100, 100))

        fb_range = self.MOVE['shape']
        # REGULATE FORWARD OR BACKWARD : fb ( Foward / Backward )
        if area > fb_range[0] and area < fb_range[1]:
            fb = 0
        elif area < fb_range[0] and area != 0:
            fb = speed
        elif area > fb_range[1]:
            fb = 0
            track = False

        if x == 0:
            yaw = 0
            error = 0

        self.send_rc_control(0, fb, 0, yaw)
        return error, track

    ''' Detect QR CODE '''
    def read_qr(self, frame):
        detect = False
        message = False

        try:
            # 바코드 정보 decoding
            qrs = decode(frame)

            # 바코드 정보가 여러 개 이기 때문에 하나씩 해석
            for qr in qrs:
                # 바코드 rect정보
                x, y, w, h = qr.rect
                # 바코드 데이터 디코딩
                message = qr.data.decode('utf-8')
                # 인식한 바코드 사각형 표시
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                # 인식한 바코드 사각형 위에 글자 삽입
                cv2.putText(frame, message, (x , y - 20), self.FONT, 0.5, (0, 0, 255), 1)
                detect = True
                print(f'QR CODE\t\t:    {message}')

            return detect, frame, message

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
    
    ''' Get info of rectangle  '''
    def __getRectInfo(self, points):
        # 입력받은 사각형의 정보 추출
        (x, y, w, h) = cv2.boundingRect(points)
        point1 = (x, y)
        point2 = (x + w, y + h)

        # 중심 찾기
        centroid_1= int((x + x + w) / 2)
        centroid_2 = int((y + y + h) / 2)
        centroid = (centroid_1, centroid_2)

        # 넓이 구하기
        area = w * h

        return (point1, point2, centroid, area)
    
    ''' Draw rectangle and text '''
    def __setLabel(self, frame, info, label):

        (point1, point2, centroid, area) = info
        
        # Bounding Box 그리기
        cv2.rectangle(frame, point1, point2, (0, 255, 0), 2)

        # 중심 원 그리기
        cv2.circle(frame, centroid, 5, (255,255,255), cv2.FILLED)
        # Labeling
        cv2.putText(frame, label, point1, self.FONT, 1, (0, 0, 255))

    ''' Initialization SHAPE '''
    def __initShapes(self):
        for shape in self.SHAPE:
            self.SHAPE[shape] = False
