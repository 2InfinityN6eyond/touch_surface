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

def calc_landmark_list(image_width, image_height, landmarks):
    #image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


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

      print(i)
      i+=1 
      """
      hand_landmark = results.multi_hand_landmarks[0]
      landmark_list = calc_landmark_list(image.shape[1], image.shape[0], hand_landmark)

      

      index_finger_coord_cam = landmark_list[8]
      middle_finger_coord_cam = landmark_list[12]

      index_finger_coord = transformCoord(index_finger_coord_cam, homography)
      middle_finger_coord = transformCoord(middle_finger_coord_cam, homography)
      """
      
      index_finger_coord = [100, 100]
      middle_finger_coord = [100, 100]


      if index_finger_coord[0] < 0 :
        
        index_finger_coord[0] = 1
      if index_finger_coord[0] >= screen_width :
        
        index_finger_coord[0] = screen_width - 1
      if index_finger_coord[1] < 0 :
        
        index_finger_coord[1] = 1
        
      if index_finger_coord[1] >= screen_width :
        index_finger_coord[1] = screen_height - 1

      
      

      #pyautogui.moveTo(*index_finger_coord)




cap.release()