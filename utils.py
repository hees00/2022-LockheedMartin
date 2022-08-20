from threading import Thread
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from scipy.spatial import distance as dist

############################################
FONT = cv2.FONT_HERSHEY_SIMPLEX
COLOR = {
  'red': [[0, 0, 50], [60, 60, 255]],
  'blue': [[50, 0, 0], [255, 50, 50]],
  'green': [[0, 50, 0], [50, 255, 50]],
}
############################################

class Drone():
    def __init__(self):
        self.r_val = 0
        self.l_val = 0
        self.up_val = 0
        self.down_val = 0
        self.f_val = 0
        self.b_val = 0
        self.c_wise = 0
        self.cc_wise = 0

    def takeoff(self):
        print('Drone take off.')

    def land(self):
        print('Drone land.')

    def stop(self, val):
        for i in range(val):
            print(f'Drone Stop now.')

    def up(self, val):
        self.up_val = val
        for i in range(val):
            print(f'Drone Up {i + 1}\t|\tUP : {self.up_val} ')

    def down(self, val):
        self.down_val = val
        for i in range(val):
            print(f'Drone down {i + 1}\t|\tDOWN : {self.up_val} ')

    def clockwise(self, val):
        self.c_wise = val
        for i in range(val):
            print(f'Clockwise {i + 1}\t|\tc_wise : {self.down_val}')

    def counter_clockwise(self, val):
        self.c_wise = val
        for i in range(val):
            print(f'Clockwise {i + 1}\t|\tc_wise : {self.down_val}')


'''
DETECT QR CODE

@params   frame: numpy형식의 frames

return    Bounding box + QR data가 추가된 image

'''
def read_QR(frame):
    # QR CODE를 식별했는지 확인
    detect = False

    try:
        # 바코드 정보 decoding
        qrs = decode(frame)
        detect = False

        # 바코드 정보가 여러 개 이기 때문에 하나씩 해석
        for qr in qrs:
            # 바코드 rect정보
            x, y, w, h = qr.rect
            # 바코드 데이터 디코딩
            qr_info = qr.data.decode('utf-8')
            # 인식한 바코드 사각형 표시
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
            # 인식한 바코드 사각형 위에 글자 삽입
            cv2.putText(frame, qr_info, (x , y - 20), FONT, 0.5, (0, 0, 255), 1)
            detect = True
            print(f'QR CODE\t\t:    {qr_info}')

        return detect, frame
    except Exception as e:
        print(e)

'''
Detect RECTANGLE AND COLOR

@params   frame: numpy형식의 frames
@params   coolr: 식별할 color name

return    Bounding box + color가 추가된 image

'''

def Label(frame, points, label):
    # 입력받은 사각형의 정보 추출
    (x, y, w, h) = cv2.boundingRect(points)
    point1 = (x, y)
    point2 = (x + w, y + h)

    # Bounding Box 그리기
    cv2.rectangle(frame, point1, point2, (255, 0, 0), 3)

    # 중심 찾기
    centroid_1= int((x + x + w) / 2)
    centroid_2 = int((y + y + h) / 2)
    centroid = (centroid_1, centroid_2)

    # 중심 원 그리기
    cv2.circle(frame, centroid, 5, (255,255,255), 2)
    # Labeling
    cv2.putText(frame, label, point1, FONT, 1, (0, 0, 255))

'''
Detect RECTANGLE AND COLOR

@params   frame: numpy형식의 frames
@params   color: 식별할 color name

return    Bounding box + color가 추가된 image

'''

def identify_color(frame, color):
    detect = False
    color = color.lower()
    lower_red = np.array(COLOR[color][0])
    upper_red = np.array(COLOR[color][1])

    mask = cv2.inRange(frame, lower_red, upper_red)
    mask = cv2.erode(mask, None)

    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for pts in contours:
        if cv2.contourArea(pts) < 400:
            continue
        approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)
        vtc = len(approx)
        if vtc == 4:
            print(f"DETECT COLOR\t:    {color.upper()}")
            Label(frame, pts, f'{color.upper()} Marker')
            detect = True

    return detect, frame
