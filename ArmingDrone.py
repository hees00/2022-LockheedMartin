import cv2
import math
import numpy as np
import time
from djitellopy import tello
from pyzbar.pyzbar import decode

from yolo.YOLO import YOLO

class ArmingDrone(tello.Tello):

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    # Values of HSV Color [0] : Lower / [1] : Upper
    COLOR = {
      'all': [[0, 0, 0], [255, 255, 255]],
      'red': [[0, 232, 55], [179, 255, 255]],
      'blue': [[95, 111, 0], [125, 255, 255]],
      'green': [[37, 19, 15], [95, 255, 255]],
      'black': [[0, 0, 0], [179, 255, 20]],
    }

    # Detecting of Shapes
    SHAPE = {
        'triangle': False,
        'rectangle': False,
        'circle': False,
    }

    AREA = {
        'shape': [26000, 27000],
        'kau': [26000, 27000],
        'f22': [26000, 27000],
    }

    PID = [0.2, 0.2, 0]

    YOLO_CONFIG = {
        'model_name': 'yolov5n.onnx',
        'conf_thres': 0.7,
        'iou_thres': 0.3,
    }

    MIN_PIX = 28

    TIME = 0
    TIME_LIMIT = 30

    # Create YOLO DETECTOR MODEL
    model_path = f'./models/{YOLO_CONFIG["model_name"]}'
    yolo_detector = YOLO(model_path, conf_thres = YOLO_CONFIG['conf_thres'], iou_thres = YOLO_CONFIG['iou_thres'])

    def hover(self):
        ''' Drone stop ( Hovering ) '''

        self.send_rc_control(0, 0, 0, 0)

    def hover_sec(self, sec):
        ''' Drone stop ( Hovering ) '''

        start = time.time()
        while True:
            end = time.time()
            duration = end - start

            self.hover()

            if duration > sec:
                break   

    def move_sec(self, rc_control, sec):
        ''' Drone moves for sec '''

        try:
            lr, fb, ud, yv = rc_control
            start = time.time()

            while True:
                end = time.time()
                duration = end - start

                self.send_rc_control(lr, fb, ud, yv)

                if duration > sec:
                    break   

        except Exception as e:
            print(e)


    def identify_shapes(self, frame, shapes = 'all', color = 'all'):
        ''' Detect Shapes by color '''

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

    def detect_object(self, frame, objects = 'all'):
        ''' 
        Detect Objects : A380 / Apache / F22 / KAU / KT-1 

            @ Param <Numpy> frame           : Image frame\n
            @ Param <list>  objects         : Set object to detect [Default : all]\n
        
        '''

        boxes, scores, class_ids = self.yolo_detector(frame)
        detect = {}
        rectInfo = {}

        if objects != 'all':
            classes = self.yolo_detector.get_classes_list()
            id_list = []

            for obj in objects:
                obj = obj.upper()
                id_num = classes.index(obj)
                id_list.append(id_num)
                detect[obj] = False

            objects_info = list(zip(boxes, scores, class_ids))
            filter_boxes = []
            filter_scores = []
            filter_class_ids = []

            # Filtering classes
            for object_info in objects_info:
                if object_info[2] in id_list:
                    box = object_info[0]
                    score = object_info[1]
                    class_id = object_info[2]

                    # Save Bounding Box Info
                    xywh = self.__xyxy2xywh(box)
                    ppca = self.__xywh2ppca(xywh)
                    rectInfo[classes[class_id]] = ppca

                    detect[classes[class_id]] = True

                    filter_boxes.append(box)
                    filter_scores.append(score)
                    filter_class_ids.append(class_id)

            # Draw Bounding Box
            filter_object_info = (filter_boxes, filter_scores, filter_class_ids)
            draw_frame = self.yolo_detector.draw_detections(frame, draw_info = filter_object_info)                

        elif objects == 'all':
            draw_frame = self.yolo_detector.draw_detections(frame)


        return detect, draw_frame, rectInfo

    def detect_number(self, frame):
        frame = cv2.resize(frame, (480, 480))
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, img_binary = cv2.threshold(img_gray, 20, 255, cv2.THRESH_BINARY_INV)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_bounding = None
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            area = w * h
            if area > max_area:
                max_area = area
                max_bounding = (x, y, w, h)

        x, y, w, h = max_bounding

        if (w < self.MIN_PIX or h < self.MIN_PIX):
            return 0, 0

        length = max(w, h) + 60
        img_digit = np.zeros((length, length, 1), np.uint8)
        img_digit = img_binary[ y:y + length, x:x + length ]

        model = cv2.dnn.readNet('./models/mnist.onnx')

        blob = cv2.dnn.blobFromImage(self.__norm_digit(img_digit), 1/255.0, (28, 28))
        model.setInput(blob)
        prob = model.forward() # 확률 값 출력, 확률의 최댓값이 인식한 클래스 의미

        _, maxVal, _, maxLoc = cv2.minMaxLoc(prob)
        digit = maxLoc[0] # [0]은 클래스, [1]은 확률
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        location = (x + int(w * 0.5), y - 10)
        font = cv2.FONT_HERSHEY_COMPLEX
        fontScale = 1.2
        cv2.putText(frame, str(digit), location, font, fontScale, (0, 255, 0), 2)

        return frame, digit

    def track_object(self, info, w, pError, objects = 'shape' ,speed = 20):
        ''' Drone track object '''

        track = True

        x, y = info[2]
        area = info[3]
        fb = 0

        # REGULATE YAW : yaw ( Angle )
        error = x - w // 2
        yaw = self.PID[0] * error + self.PID[1] * (error - pError)
        yaw = int(np.clip(yaw, -100, 100))

        fb_range = self.AREA[objects.lower()]
        # REGULATE FORWARD OR BACKWARD : fb ( Foward / Backward )
        if area > fb_range[0] and area < fb_range[1]:
            fb = 0
            self.TIME += 1

        elif area < fb_range[0] and area != 0:
            fb = speed
            self.__initTime()

        elif area > fb_range[1]:
            fb = 0
            self.TIME += 1


        if self.TIME == self.TIME_LIMIT:
            track = False

        if x == 0:
            yaw = 0
            error = 0

        print(f'Area : {area}')
        print(f'yaw : {yaw}')
        print(f'TIME : {self.TIME}')

        self.send_rc_control(0, fb, 0, yaw)
        return error, track

    def read_qr(self, frame):
        ''' Detect QR CODE '''

        detect = False
        message = False

        try:
            # Decode barcode information
            qrs = decode(frame)

            # Interpret one by one because there are multiple barcode information
            for qr in qrs:
                # Barcode rectangle Information
                x, y, w, h = qr.rect
                # Decode Barcode Data
                message = qr.data.decode('utf-8')
                # Display recognized barcode squares
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                # Insert letter over recognized barcode square
                cv2.putText(frame, message, (x , y - 20), self.FONT, 0.5, (0, 0, 255), 1)
                detect = True
                print(f'QR CODE\t\t:    {message}')

            return detect, frame, message

        except Exception as e:
            print(e)

    def start_mission(self, mission_number):
        ''' Start Mission 01 ~ 09 '''

        # After Back 30, Forward 30 [cm]
        if mission_number == 1:
            self.move_sec([0, -30, 0, 0], 1)
            self.hover_sec(1)
            self.move_sec([0, 30, 0, 0], 1)
            self.hover_sec(1)

        # Left and right 30 [cm]
        elif mission_number == 2:
            self.move_sec([30, 0, 0, 0], 1)
            self.hover_sec(1)
            self.move_sec([-30, 0, 0, 0], 1)
            self.hover_sec(1)

        # 360 degree rotation
        elif mission_number == 3:
            self.rotate_clockwise(360)

        # Draw a rectangle right > up > left > down
        elif mission_number == 4:
            self.move_sec([-30, 0, 0, 0], 1)
            self.hover_sec(1)
            self.move_sec([0, 0, 30, 0], 1)
            self.hover_sec(1)
            self.move_sec([30, 0, 0, 0], 1)
            self.hover_sec(1)
            self.move_sec([0, 0, -30, 0], 1)
            self.hover_sec(1)

        # Flip Backward
        elif mission_number == 5:
            self.flip_back()

        # Draw a rectangle in the left > bottom > right > top
        elif mission_number == 6:
            self.move_sec([0, 0, 60, 0], 0.5)
            self.flip_back()
            self.move_sec([0, 0, -60, 0], 0.5)
        
        # flip left
        elif mission_number == 7:
            self.flip_left()

        # Up and down 30 [cm]
        elif mission_number == 8:
            self.move_sec([0, 0, 60, 0], 0.5)
            self.move_sec([0, 0, -60, 0], 0.5)

        # Left 30cm> 180 degrees rotation > Right 30cm > 180 degrees rotation
        elif mission_number == 9:
            pass

    # Setter
    def setYoloModel(self, model_name):
        self.YOLO_CONFIG['model_name'] = model_name

    def setConf(self, conf_thres):
        self.YOLO_CONFIG['conf_thres'] = conf_thres

    def setIou(self, iou_thres):
        self.YOLO_CONFIG['iou_thres'] = iou_thres

    def __getRectInfo(self, points):
        ''' Get info of rectangle  '''

        (x, y, w, h) = cv2.boundingRect(points)
 
        return self.__xywh2ppca((x, y, w, h))

    
    def __setLabel(self, frame, info, label, shape = 'rectangle'):
        ''' Draw rectangle and text '''

        (point1, point2, centroid, area) = info
        
        if shape == 'rectangle':
            # Draw Bounding Bow
            cv2.rectangle(frame, point1, point2, (0, 255, 0), 2)

        # Draw a center circle
        cv2.circle(frame, centroid, 5, (255,255,255), cv2.FILLED)
        # Labeling
        cv2.putText(frame, label, point1, self.FONT, 1, (0, 0, 255))

    def __xyxy2xywh(self, coords):
        ''' Convert bounding box (x1, y1, x2, y2) to bounding box (x, y, w, h) '''

        x, y = coords[:2]
        w = x - coords[2]
        h = y - coords[3]

        return (x, y, w, h)

    def __xywh2ppca(self, coords):
        ''' Convert bounding box (x, y, w, h) to bounding box (p1, p2, center, area) '''
        (x, y, w, h) = coords

        point1 = (x - 10, y - 10)
        point2 = (x + w + 10, y + h + 10)

        # Finding Center
        centroid_1= int((x + x + w) / 2)
        centroid_2 = int((y + y + h) / 2)
        centroid = (centroid_1, centroid_2)

        # Finding the area
        area = int(w * h)

        return (point1, point2, centroid, area)

    # 영상의 위치 정규화
    def __norm_digit(img):
        # 무게 중심 좌표 추출
        m = cv2.moments(img)
        cx = m['m10'] / m['m00']
        cy = m['m01'] / m['m00']
        h, w = img.shape[:2]
        
        # affine 행렬 생성
        aff = np.array([[1, 0, w/2 - cx], [0, 1, h/2 - cy]], dtype=np.float32)
        
        # warpAffine을 이용해 기하학 변환
        dst = cv2.warpAffine(img, aff, (0, 0))
        return dst

    def __initTime(self):
        self.TIME = 0
    