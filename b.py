import cv2
import numpy as np


MIN_PIX = 28

def process(img_input):

    gray = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)


    (thresh, img_binary) = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    h,w = img_binary.shape
  
    ratio = 100/h
    new_h = 100
    new_w = w * ratio

    img_empty = np.zeros((110,110), dtype=img_binary.dtype)
    img_binary = cv2.resize(img_binary, (int(new_w), int(new_h)), interpolation=cv2.INTER_AREA)
    img_empty[:img_binary.shape[0], :img_binary.shape[1]] = img_binary

    img_binary = img_empty


    cnts = cv2.findContours(img_binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # 컨투어의 무게중심 좌표를 구합니다. 
    M = cv2.moments(cnts[0][0])
    center_x = (M["m10"] / M["m00"])
    center_y = (M["m01"] / M["m00"])

    # 무게 중심이 이미지 중심으로 오도록 이동시킵니다. 
    height,width = img_binary.shape[:2]
    shiftx = width/2-center_x
    shifty = height/2-center_y

    Translation_Matrix = np.float32([[1, 0, shiftx],[0, 1, shifty]])
    img_binary = cv2.warpAffine(img_binary, Translation_Matrix, (width,height))


    img_binary = cv2.resize(img_binary, (28, 28), interpolation=cv2.INTER_AREA)
    flatten = img_binary.flatten() / 255.0

    return flatten


def detect_number(frame):
    """
    MIN_PIX
    """
    frame = cv2.resize(frame, (640, 580))
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret,img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_CLOSE, kernel)
    frame = img_binary
    digit = 0

    contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    max_bounding = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        area = w * h
        if area > max_area:
            max_area = area
            max_bounding = (x, y, w, h)

    x, y, w, h = max_bounding
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)

    length = max(w, h)
    img_digit = np.zeros((length, length, 1),np.uint8)

    new_x,new_y = x-(length - w)//2, y-(length - h)//2


    img_digit = img_binary[new_y:new_y+length, new_x:new_x+length]

    kernel = np.ones((5, 5), np.uint8)
    img_digit = cv2.morphologyEx(img_digit, cv2.MORPH_DILATE, kernel)

    cv2.imshow('digit', img_digit)
    cv2.waitKey(0)

    # if (w < MIN_PIX or h < MIN_PIX):
    #     return 0, 0

    # model = cv2.dnn.readNet('./models/mnist.onnx')

    # blob = cv2.dnn.blobFromImage(img_digit)
    # model.setInput(blob)
    # prob = model.forward() # 확률 값 출력, 확률의 최댓값이 인식한 클래스 의미

    # _, maxVal, _, maxLoc = cv2.minMaxLoc(prob)
    # digit = maxLoc[0] # [0]은 클래스, [1]은 확률
    # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

    # location = (x + int(w * 0.5), y - 10)
    # font = cv2.FONT_HERSHEY_COMPLEX
    # fontScale = 1.2
    # cv2.putText(frame, str(digit), location, font, fontScale, (0, 255, 0), 2)

    return frame, digit

frame = cv2.imread('five.jpg', cv2.IMREAD_COLOR)
frame, number = detect_number(frame)
print(number)
cv2.imshow('digit', frame)
cv2.waitKey(0)