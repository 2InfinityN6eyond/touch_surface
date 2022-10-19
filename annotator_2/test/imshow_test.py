import cv2
import time


frame_width  = [1920, 1280, 1280, 640][0]
frame_height = [1080, 1024,  720, 480][0]

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

while True :
    start_time = time.time()
    
    ret, frame = cap.read()

    fps = 1 / (time.time() - start_time)

    cv2.putText(
        frame,
        str(fps),
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX, 2.0,
        (0, 0, 0), 2
    )
    cv2.putText(
        frame,
        str(fps),
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX, 2.0,
        (255,255,255), 2
    )

    cv2.imshow("frame", frame)

    key = cv2.waitKey(10)
    if key in [27, ord("q"), ord("Q")]:  # ESC
        cv2.destroyAllWindows()
        break
