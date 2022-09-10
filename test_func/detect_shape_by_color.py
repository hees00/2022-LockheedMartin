import cv2
from utils import *

width = 640
height = 480
FRAME = 60

PATH = {
  'images': './Resources/Images/',
  'videos': './Resources/Videos/',
  'result': './results/practice/',
  'log': './results/log/',
}

def detect_shape_by_color():
    select = int(input('Select Test (Image = 1 / Video = 2) : '))
    color = input('Enter a color to identify (red / green / blue) : ')
    shape = input('Enter a shape to identify (triangle / rectangle / circle) : ')
    

    cv2.namedWindow('DETECT CIRCLE BY COLOR')

    if select == 1:
        use_shape = input('Enter a shape to check (triangle / rectangle / circle) : ')
        src = input('Test file name : ')
        path = PATH['images'] + f'{use_shape}/' + src
        image = cv2.imread(path)

        if image is None:
            print('Image open failed!')
            return

        image = cv2.resize(image, (width, height))
        
        detect, image, info = identify_shapes(image, shapes = shape, color = color)
        print(f'DETECT : {detect}')
        cv2.imshow('DETECT CIRCLE BY COLOR', image)
        print(info)

        cv2.waitKey(0)

    elif select == 2:
        src = input('Test file name : ')
        path = PATH['videos'] + src
        video = cv2.VideoCapture(path)

        try:
            while video.isOpened():
                # 실행 내역 및 프레임 가져오기
                ret, frame = video.read()
                frame = cv2.resize(frame, (width, height))

                # 실행 내역이 true이면 프레임 출력
                if ret:
                    detect, frame, info = identify_shapes(frame, shapes = shape, color = color)

                    cv2.imshow('DETECT CIRCLE BY COLOR', frame)
                    print(info)

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

    else:
        print("Please enter valid values.")
        return