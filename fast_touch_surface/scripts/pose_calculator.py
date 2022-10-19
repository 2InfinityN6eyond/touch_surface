from mimetypes import read_mime_types
import os
import sys
import cv2
import numpy as np
from multiprocessing import Process, Queue, Pipe, Value
from PyQt5 import QtWidgets, QtCore, QtGui
import mediapipe as mp

from scripts.calibration_window import CalibrationWindow
from scripts.utils import calc_landmark_list

from pprint import PrettyPrinter

use_realsense = False

from pynput.mouse import Button, Controller

mouse = Controller()




try :
    import pyrealsense2 as rs
    use_realsense =True
except :
    pass


class Posecalculator(Process) :
    def __init__(
        self,
        pose_calculator_to_data_bidge,
        pose_calculator_to_mouse_controller,
        image_width = 1920,
        image_hiegh = 1080,
        fps         = 30
    ) :        
        super(Posecalculator, self).__init__()

        self.image_width = image_width
        self.image_hiegh = image_hiegh
        self.fps         = fps        

        self.configs_n_vals = {
            "homography" : None,
            "checker_corner_shape" : (9, 6)
        }

        self.screen_height = pyautogui.size().height
        self.screen_width = pyautogui.size().width

        self.to_mouse_controller = pose_calculator_to_mouse_controller

    def run(self) :
    
        self.video_cap = cv2.VideoCapture(0)
        self.video_cap.set(
            cv2.CAP_PROP_FRAME_WIDTH, 
            self.image_width
        )
        self.video_cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT, self.image_hiegh
        )
        self.video_cap.set(
            cv2.CAP_PROP_FPS, self.fps
        )
        self.video_cap.set(
            cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")
        )

        self.calibrate()

        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence = 0.3,
            min_tracking_confidence  = 0.3,
        )

        while True :
            ret = self.readImage()
            if not ret :
                print("IMAGE READ FAILED")

            #image = cv2.flip(self.image, 1)
            image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            hand_keypoints_result = hands.process(image)
            image.flags.writeable = True
            

            if hand_keypoints_result.multi_hand_landmarks is not None :
                hand_landmarks = hand_keypoints_result.multi_hand_landmarks[0]
                landmark_list = calc_landmark_list(image, hand_landmarks)

                index_finger_coord_cam = landmark_list[8]
                middle_finger_coord_cam = landmark_list[12]

                index_finger_coord = self.transformCoord(
                    index_finger_coord_cam
                )
                middle_finger_coord = self.transformCoord(
                    middle_finger_coord_cam
                )

                #print(index_finger_coord, middle_finger_coord)
                #print(pyautogui.size())
                
                if index_finger_coord[0] < 0 :
                    #print("trimming low x")
                    index_finger_coord[0] = 1
                if index_finger_coord[0] >= self.screen_width :
                    #print("trimming hight x")
                    index_finger_coord[0] = self.screen_width - 1
                if index_finger_coord[1] < 0 :
                    #print("trimming low y")
                    index_finger_coord[1] = 1
                    #print("trimming")
                if index_finger_coord[1] >= self.screen_width :
                    index_finger_coord[1] = self.screen_height - 1

                print(index_finger_coord, middle_finger_coord)

                
                #self.to_mouse_controller.put(index_finger_coord)
                
                mouse.position = index_finger_coord

                #pyautogui.moveTo(*index_finger_coord)

            else : continue

    def readImage(self) :
        image = 10
        if use_realsense :
            frames = self.pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            image = np.asanyarray(color_frame.get_data())

            ret = True if image is not None else False

        else :
            ret, image = self.video_cap.read()

        self.image = image
        return ret

    def calibrate(self) :
        app = QtWidgets.QApplication(sys.argv)
        
        self.calibrate_window = CalibrationWindow(
            self.configs_n_vals["checker_corner_shape"],
            self
        )
        self.calibrate_window.show()

        image_read_timer = QtCore.QTimer()
        image_read_timer.setInterval(100)
        image_read_timer.timeout.connect(self.readImage)

        print("executing")
        app.exec_() 
        print("end execute")

    def verifyCalibrating(self) :
        #print("checking homography exists")
        if self.configs_n_vals["homography"] is not None :
            self.calibrate_window = None
            
    def transformCoord(self, coord) :
        """
        coord : [x_coord, y_coord]
        """
        coord = np.array([coord[0], coord[1], 1]).reshape(3, 1)

        transformed = np.matmul(
            self.configs_n_vals["homography"],
            coord
        )
        
        #print(transformed)
        
        transformed = transformed.reshape(3,)
        transformed /= transformed[2]

        #print(transformed)
        #print()

        return [transformed[0], transformed[1]]

