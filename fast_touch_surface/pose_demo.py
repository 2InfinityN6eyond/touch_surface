import numpy as np
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


# For webcam input:
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


import pyautogui

pyautogui.FAILSAFE = False

screen_width = pyautogui.size().width
screen_height = pyautogui.size().height

from scripts.utils import *

homography = np.array([
  [ 1.83304447e+00,  3.52612380e-01, -2.10274617e+02],
  [-1.15953686e-01,  2.52047339e+00, -4.16752444e+02],
  [-1.58343699e-04,  3.44102646e-04,  1.00000000e+00]
])


def transformCoord(coord, homography) :
  """
  coord : [x_coord, y_coord]
  """
  coord = np.array([coord[0], coord[1], 1]).reshape(3, 1)

  transformed = np.matmul(
      homography,
      coord
  )
  
  #print(transformed)
  
  transformed = transformed.reshape(3,)
  transformed /= transformed[2]

  #print(transformed)
  #print()

  return [transformed[0], transformed[1]]

i = 0

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      hand_landmark = results.multi_hand_landmarks[0]
      
      landmark_list = calc_landmark_list(
        image, landmarks=hand_landmark
      )
      bounding_box = calc_bounding_rect(
        image, landmarks=hand_landmark
      )


      image = draw_bounding_rect(True, image, bounding_box)
      image = draw_landmarks(image, landmark_list)

      cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
      if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()