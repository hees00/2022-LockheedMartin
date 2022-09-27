from ast import expr_context
import cv2
import math
import numpy as np
import time
from djitellopy import tello
from pyzbar.pyzbar import decode
from yolo.YOLO import YOLO

class ArmingDrone(tello.Tello):

    FONT = cv2.FONT_HERSHEY_SIMPLEX
    BOX_COLOR = (1, 41, 95)
    FONT_COLOR = (67, 127, 151)

    WIDTH = 840
    HEIGHT = 720

    '''
    Red hsv list 

    1. (0, 141, 72), (179, 255, 255) < best >
    
    '''
    # Values of HSV Color [0] : Lower / [1] : Upper
    COLOR = {
      'all': [[0, 0, 0], [179, 255, 255]],
      'red': [[0, 141, 72], [179, 255, 255]],
      'blue': [[95, 111, 35], [127, 255, 255]],
      'green': [[37, 19, 15], [95, 255, 255]],
      'black': [[0, 0, 0], [179, 255, 35]],
    }

    # Detecting of Shapes
    SHAPE = {
        'triangle': False,
        'rectangle': False,
        'circle': False,
    }

    AREA = {
        'shape': [26000, 27000],
        'kau': [27000, 28000],
        'f22': [80000,81000],
    }

    PID = [0.15, 0.15, 0]

    YOLO_CONFIG = {
        'model_name': 'yolov5n.onnx',
        'conf_thres': 0.77,
        'iou_thres': 0.3,
    }

    NUMBER_CONFIG = {
        'model_name': 'MnistCNN.onnx',
        'minArea': 300,
        'max_val': 10,
    }

    MIN_PIX = 28

    TIME = 0
    TIME_LIMIT = 20

    # Create YOLO DETECTOR MODEL
    yolo_model_path = f'./models/{YOLO_CONFIG["model_name"]}'
    yolo_detector = YOLO(yolo_model_path, conf_thres = YOLO_CONFIG['conf_thres'], iou_thres = YOLO_CONFIG['iou_thres'])

    # Create NUMBER DETECTOR MODEL
    number_model_path = f'./models/{NUMBER_CONFIG["model_name"]}'
    number_detector = cv2.dnn.readNet('./models/MnistCNN.onnx')

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

        cv2.imshow('mask', mask)
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

    def detect_number(self, frame, circleInfo):
        ''' 
        Detect number : 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 9

            @ Param <Numpy> frame           : Image frame\n
            @ Param <tuple> circleInfo      : Circle Info (point1, point2, center, area)\n
        
        '''
        model = self.number_detector
        detect = False
        number = 0

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)

            start_x = circleInfo[0][0]
            end_x = circleInfo[1][0] + 1
            start_y = circleInfo[1][1] + 10

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = binary[start_y:, start_x: end_x]

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            max_area = 0
            max_bounding = None
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w*h

                if area < self.NUMBER_CONFIG['minArea']:
                    continue

                if area >= max_area:
                    max_area = area
                    max_bounding = (x, y, w, h)

            x, y, w, h = max_bounding
            length = max(w, h) + 10
            new_x, new_y = x + w// 2, y + h // 2
            number_box = np.zeros((length, length,1), np.uint8)
            number_box = binary[new_y - length//2 : new_y + length//2, new_x - length//2 :new_x + length//2]

            blob = cv2.dnn.blobFromImage(number_box, 1 / 255., (28, 28))
            model.setInput(blob)
            prob = model.forward()
            # maxVal : Probability / maxLoc[0] : Class
            _, maxVal, _, maxLoc = cv2.minMaxLoc(prob)
            if maxVal > self.NUMBER_CONFIG['max_val']:
                number = maxLoc[0]

            if number != 0:
                x = x + start_x
                y = y + start_y

                # Draw Bounding Box
                cv2.rectangle(frame, (x, y), (x + w, y + h), self.BOX_COLOR, 2)
                
                # Put Text
                location = (x + int(w * 0.5), y - 10)
                cv2.putText(frame, str(number), location, self.FONT, 1, self.FONT_COLOR, 2)
                detect = True
 
        except Exception as e:
            pass

        return detect, frame, number

    def track_object(self, info, pError, objects = 'shape' ,speed = 20):
        ''' Drone track object '''

        track = True
        deceleration = 2
        standard_yaw = 40

        x, y = info[2]
        area = info[3]
        fb = 0

        # REGULATE YAW : yaw ( Angle )
        error = x - self.WIDTH // 2
        yaw = self.PID[0] * error + self.PID[1] * (error - pError)
        yaw = int(np.clip(yaw, -100, 100))

        # REGULATE UP & DOWN : ud ( Up / Down )

        fb_range = self.AREA[objects.lower()]
        # REGULATE FORWARD OR BACKWARD : fb ( Foward / Backward )
        if area > fb_range[0] and area < fb_range[1]:
            fb = 0

            if objects == 'shape' or objects == 'F22':
                track = False
            else:
                self.TIME += 1

        elif area < fb_range[0] and area != 0:
            fb = speed
            self.__initTime()

        elif area > fb_range[1]:
            fb = 0

            if objects == 'shape' or objects == 'F22':
                track = False
            else:
                self.TIME += 1

        if self.TIME == self.TIME_LIMIT:
            track = False

        if x == 0:
            yaw = 0
            error = 0

        print(f'Area : {area}')
        print(f'yaw : {yaw}')
        print(f'TIME : {self.TIME}')
        
        # In a curve, deceleration
        # if objects != 'shape' and (yaw > standard_yaw or yaw < -standard_yaw):
        #     fb = fb // deceleration

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
            print('MISSION : 1 - After Back 30, Forward 30 [cm]')
            self.move_sec([0, -30, 0, 0], 1)
            self.hover_sec(0.5)
            self.move_sec([0, 30, 0, 0], 1)
            self.hover_sec(0.5)

        # Left and right 30 [cm]
        elif mission_number == 2:
            print('MISSION : 2 - Left and right 30 [cm]')
            self.move_sec([30, 0, 0, 0], 1)
            self.hover_sec(0.5)
            self.move_sec([-30, 0, 0, 0], 1)
            self.hover_sec(0.5)

        # 360 degree rotation
        elif mission_number == 3:
            print('MISSION : 3 - 360 degree rotation')
            self.rotate_clockwise(360)

        # Draw a rectangle right > up > left > down
        elif mission_number == 4:
            print('MISSION : 4 - Draw a rectangle : right > up > left > down')
            self.move_sec([-30, 0, 0, 0], 1)
            self.hover_sec(0.5)
            self.move_sec([0, 0, 30, 0], 1)
            self.hover_sec(0.5)
            self.move_sec([30, 0, 0, 0], 1)
            self.hover_sec(0.5)
            self.move_sec([0, 0, -30, 0], 1)
            self.hover_sec(0.5)

        # Flip Backward
        elif mission_number == 5:
            print('MISSION : 5 - Flip Backward')
            self.move_sec([0, 45, 0, 0], 1)
            self.hover_sec(0.5)
            self.flip_back()

        # Up 30 > Flip Backward > Down 30 [cm]
        elif mission_number == 6:
            print('MISSION : 6 - Up 30 > Flip Backward > Down 30 [cm]')
            self.move_sec([0, 0, 30, 0], 1)
            self.hover_sec(0.5)
            self.flip_back()
            self.hover_sec(0.5)
            self.move_sec([0, 0, -30, 0], 1)
            self.hover_sec(0.5)
        
        # flip left
        elif mission_number == 7:
            print('MISSION : 7 - Flip left')
            self.move_sec([60, 0, 0, 0], 1)
            self.hover_sec(0.5)
            self.flip_left()

        # Up and down 30 [cm]
        elif mission_number == 8:
            print('MISSION : 8 - Up and down 30 [cm]')
            self.move_sec([0, 0, 30, 0], 1)
            self.hover_sec(1)
            self.move_sec([0, 0, -30, 0], 1)

        # Capture number
        elif mission_number == 9:
            print('MISSION : 9 - Capture number 9')
            pass

    # Setter
    def setWindows(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height

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
            cv2.rectangle(frame, point1, point2, self.BOX_COLOR, 2)

        # Draw a center circle
        cv2.circle(frame, centroid, 5, (0, 255, 0), cv2.FILLED)
        # Labeling
        cv2.putText(frame, label, point1, self.FONT, 1, self.FONT_COLOR, cv2.LINE_4)

    def __xyxy2xywh(self, coords):
        ''' Convert bounding box (x1, y1, x2, y2) to bounding box (x, y, w, h) '''
        x, y = coords[:2]
        w = abs(x - coords[2])
        h = abs(y - coords[3])

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

    def __initTime(self):
        self.TIME = 0
    