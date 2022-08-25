import cv2
import numpy as np
import math
from pyzbar.pyzbar import decode
from scipy.spatial import distance as dist

############################################
FONT = cv2.FONT_HERSHEY_SIMPLEX

COLOR = {
  'red': [[0, 0, 50], [50, 50, 255]],
  'blue': [[50, 0, 0], [255, 50, 50]],
  'green': [[0, 50, 0], [50, 255, 50]],
}

SHAPE = {
    'triangle': False,
    'rectangle': False,
    'circle': False,
}
############################################

def stop(drone):
    drone.left_x = 0.0
    drone.left_y = 0.0
    drone.right_x = 0.0
    drone.right_y = 0.0

def send_rc_control(drone, lr, fb, ud, yv):
    drone.right_x = lr / 100.0
    drone.right_y = fb / 100.0
    drone.left_x = yv / 100.0
    drone.left_y = ud / 100.0

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
Draw rectangle and text

@params   frame: numpy형식의 frames
@params   points: contour
@params   coolr: 식별할 color name

'''

def setLabel(frame, points, label):
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
    cv2.putText(frame, label, point1, FONT, 1, (0, 0, 255))

'''
Detect RECTANGLE AND COLOR

@params   frame: numpy형식의 frames
@params   color: 식별할 color name

return    Bounding box + color가 추가된 image

'''

def identify_shapes(frame, color, shapes = 'rectangle'):

    if type(shapes) is tuple:
        for shape in shapes:
            SHAPE[shape] = True
    elif type(shapes) is str:
        SHAPE[shapes] = True

    detect = False
    color = color.lower()
    lower_color = np.array(COLOR[color][0])
    upper_color = np.array(COLOR[color][1])

    mask = cv2.inRange(frame, lower_color, upper_color)
    mask = cv2.erode(mask, None)

    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for pts in contours:
        if cv2.contourArea(pts) < 400:
            continue
        approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)
        vtc = len(approx)
        if SHAPE['triangle'] and vtc == 3:
            print(f"DETECT COLOR\t:    {color.upper()}")
            setLabel(frame, pts, f'{color.upper()} Marker')
            detect = True

        elif SHAPE['rectangle'] and vtc == 4:
            print(f"DETECT COLOR\t:    {color.upper()}")
            setLabel(frame, pts, f'{color.upper()} Marker')
            detect = True
        
        elif SHAPE['circle'] and vtc > 4:
            area = cv2.contourArea(pts)
            _, radius = cv2.minEnclosingCircle(pts)

            ratio = radius * radius * math.pi / area

            if int(ratio) == 1:
                setLabel(frame, pts, f'{color.upper()} Marker')

    return detect, frame

def identify_b_g(frame):
    detect_blue, frame_blue = identify_shapes(frame, 'blue')
    detect_green, frame_green = identify_shapes(frame, 'green')

    if (detect_blue and detect_green) is False:
        return detect_blue, frame_blue

    elif detect_blue is True:
        return detect_blue, frame_blue

    elif detect_green is True:
        return detect_green, frame_green
