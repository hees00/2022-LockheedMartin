import cv2
import math
import numpy as np
import time
from djitellopy import tello
from pyzbar.pyzbar import decode

class ArmingDrone(tello.Tello):

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    # Values of HSV Color [0] : Lower / [1] : Upper
    COLOR = {
      'all': [[0, 0, 0], [255, 255, 255]],
      'red': [[0, 232, 55], [179, 255, 255]],
      'blue': [[95, 111, 0], [125, 255, 255]],
      'green': [[37, 19, 15], [95, 255, 255]],
    }

    # Detecting of Shapes
    SHAPE = {
        'triangle': False,
        'rectangle': False,
        'circle': False,
    }

    MOVE = {
        'shape': [26000, 27000],
        'kau': [],
        'f22': [],
    }

    PID = [0.2, 0.2, 0]

    ''' Drone stop ( Hovering ) '''
    def hover(self):
        print('Drone Stop')
        self.send_rc_control(0, 0, 0, 0)

    ''' Drone moves for sec '''
    def move_sec(self, rc_control, sec):
        try:
            lr = rc_control[0]
            fb = rc_control[1]
            ud = rc_control[2]
            yv = rc_control[3]

            start = time.time()

            while True:
                end = time.time()
                duration = end - start

                self.send_rc_control(lr, fb, ud, yv)

                if duration > sec:
                    break   

        except Exception as e:
            print(e)

    def detect_handwrititing(self):
        pass
        
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
            if cv2.contourArea(pts) < 1000:
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
                area = cv2.contourArea(pts)
                _, radius = cv2.minEnclosingCircle(pts)

                ratio = radius * radius * math.pi / area

                if int(ratio) == 1:
                    print(f"DETECT COLOR\t:    {color.upper()}")
                    self.__setLabel(frame, info, f'{color.upper()} Marker')
                    detect = True

        return detect, frame, info

    ''' Drone track shapes '''
    def track_shape(self, info, w, pError, speed = 20):
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
            track = False
        elif area < fb_range[0] and area != 0:
            fb = speed
        elif area > fb_range[1]:
            fb = 0
            track = False

        if x == 0:
            yaw = 0
            error = 0

        print(f'Area : {area}')
        print(f'yaw : {yaw}')

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

    def display_info(self, frame, label):
        pass

    ''' Start Mission 01 ~ 05 '''
    def start_mission(self, mission_number):

        # Twice to the right 10 10 Twice to the left 10 10 [cm]
        if mission_number == 1:
            self.move_sec([10, 0, 0, 0], 1)
            self.move_sec([10, 0, 0, 0], 1)
            self.move_sec([-10, 0, 0, 0], 1)
            self.move_sec([-10, 0, 0, 0], 1)

        # Left and right 30 [cm]
        elif mission_number == 2:
            pass

        # 360 degree rotation
        elif mission_number == 3:
            pass

        # Draw a rectangle right > up > left > down
        elif mission_number == 4:
            pass

        # Adjust the angle to draw a triangle
        elif mission_number == 5:
            pass

        # Draw a rectangle in the left > bottom > right > top
        elif mission_number == 6:
            pass
        
        # flip left
        elif mission_number == 7:
            self.flip_left()

        # Up and down 30 [cm]
        elif mission_number == 8:
            pass

        # Left 30cm> 180 degrees rotation > Right 30cm > 180 degrees rotation
        elif mission_number == 9:
            pass

    ''' Get info of rectangle  '''
    def __getRectInfo(self, points):
        # 입력받은 사각형의 정보 추출
        (x, y, w, h) = cv2.boundingRect(points)
        point1 = (x - 10, y - 10)
        point2 = (x + w + 10, y + h + 10)

        # 중심 찾기
        centroid_1= int((x + x + w) / 2)
        centroid_2 = int((y + y + h) / 2)
        centroid = (centroid_1, centroid_2)

        # 넓이 구하기
        area = w * h

        return (point1, point2, centroid, area)
    
    ''' Draw rectangle and text '''
    def __setLabel(self, frame, info, label, shape = 'rectangle'):

        (point1, point2, centroid, area) = info
        
        if shape == 'rectangle':
            # Bounding Box 그리기
            cv2.rectangle(frame, point1, point2, (0, 255, 0), 2)
        # elif shape =='circle':
        #     radius = abs(point1 - point2)
        #     cv2.circle(frame, centroid, radius,(0, 255, 0), 2) 

        # 중심 원 그리기
        cv2.circle(frame, centroid, 5, (255,255,255), cv2.FILLED)
        # Labeling
        cv2.putText(frame, label, point1, self.FONT, 1, (0, 0, 255))

