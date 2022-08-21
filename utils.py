import cv2
import numpy as np
import pygame
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

def stop(drone):
    drone.left_x = 0.0
    drone.left_y = 0.0
    drone.right_x = 0.0
    drone.right_y = 0.0

def send_rc_control(drone, lr, fb, ud, yv):
    drone.right_x = lr
    drone.right_y = fb
    drone.left_x = yv
    drone.left_y = ud

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

def Label(frame, points, label):
    # 입력받은 사각형의 정보 추출
    (x, y, w, h) = cv2.boundingRect(points)
    point1 = (x, y)
    point2 = (x + w, y + h)

    # Bounding Box 그리기
    cv2.rectangle(frame, point1, point2, (255, 0, 0), 2)

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

def key_init():
    pygame.init()
    window = pygame.display.set_mode((400, 400))

def getKey(keyName):
    ans = False
    for eve in pygame.event.get():  pass
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))

    if keyInput[myKey]:
        ans = True
    
    pygame.display.update()

    return ans

def getKeyboardInput(drone):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50 / 100.0

    if getKey("LEFT"): lr = -speed
    elif getKey("RIGHT"): lr = speed

    if getKey("UP"): fb = speed
    elif getKey("DOWN"): fb = -speed

    if getKey("w"): ud = speed
    elif getKey("s"): ud = -speed

    if getKey("a"): yv = speed
    elif getKey("d"): yv = -speed

    if getKey("q"): drone.land()
    if getKey("e"): drone.land()


    return [lr, fb, ud, yv]


