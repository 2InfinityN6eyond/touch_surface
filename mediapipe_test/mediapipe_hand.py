import cv2
import mediapipe as mp
import time

from utils import *


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

i = 0

with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3,
) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
    
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        ___start_process = time.time()
        results = hands.process(image)
        ___end_process = time.time()

        print(___end_process - ___start_process)
    
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            pass
            #bbox = calc_bounding_rect()


            """
            for hand_landmarks in results.multi_hand_landmarks:
              mp_drawing.draw_landmarks(
                  image,
                  hand_landmarks,
                  mp_hands.HAND_CONNECTIONS,
                  mp_drawing_styles.get_default_hand_landmarks_style(),
                  mp_drawing_styles.get_default_hand_connections_style())
            """

        """
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
        """
    cap.release()