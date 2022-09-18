import cv2
from YOLO  import YOLO

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize YOLO object detector
model_path = "../models/yolov5n.onnx"
yolo_detector = YOLO(model_path, conf_thres=0.7, iou_thres=0.3)

cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
while cap.isOpened():

    # Read frame from the video
    ret, frame = cap.read()

    if not ret:
        break

    # Update object localizer
    boxes, scores, class_ids = yolo_detector(frame)

    combined_img = yolo_detector.draw_detections(frame)
    cv2.imshow("Detected Objects", combined_img)

    # Press key q to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
