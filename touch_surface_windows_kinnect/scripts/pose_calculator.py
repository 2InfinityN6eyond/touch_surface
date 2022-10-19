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




'''

from mimetypes import read_mime_types
import os
import sys
import cv2
import numpy as np
from multiprocessing import Process, Queue, Pipe, Value
from threading import Thread
from PyQt5 import QtWidgets, QtCore, QtGui
import mediapipe as mp

from scripts.calibration_window import CalibrationWindow
from scripts.utils import calc_landmark_list

import pyautogui

use_realsense = False

try :
    import pyrealsense2 as rs
    use_realsense =True
except :
    pass

class Posecalculator() : #Process) :
    def __init__(
        self,
        bluetooth_reciever_to_pose_calculator:Queue,
        frame_width = 1920,
        frame_height = 1080,
        fps         = 30
    ) :

        self.bluetooth_reciever_to_pose_calculator = bluetooth_reciever_to_pose_calculator

        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps         = fps        

        self.configs_n_vals = {
            "homography" : None,
            "checker_corner_shape" : (8, 5),

            "click_threshold" : 3900,
        

            "index_finger_idx" : 1,
            "midle_finger_idx" : 2,

            "index_finger_curr" : 0,
            "index_finger_prev" : 0,
            'midle_finger_curr' : 0,
            'midle_finger_prev' : 0
        }


        self.run()

    def run(self) :
        if use_realsense :
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            self.config.enable_stream(
                rs.stream.color,
                self.frame_width,
                self.frame_height,
                rs.format.bgr8,
                self.fps
            )
            self.pipeline.start(self.config)
        else :
            self.video_cap = cv2.VideoCapture(0)
            self.video_cap.set(
                cv2.CAP_PROP_FRAME_WIDTH, 
                self.frame_width
            )
            self.video_cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height
            )
            self.video_cap.set(
                cv2.CAP_PROP_FPS, self.fps
            )
            self.video_cap.set(
                cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")
            )

        self.readImage()


        self.calibrate()

        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence = 0.3,
            min_tracking_confidence  = 0.3,
        )

        while True :

            if not self.bluetooth_reciever_to_pose_calculator.empty() :
                self.bluetoothRecieverCb(self.bluetooth_reciever_to_pose_calculator.get())

            ret = self.readImage()
            if not ret :
                print("IMAGE READ FAILED")

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

                pyautogui.moveTo(*index_finger_coord)

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


    def bluetoothRecieverCb(self, data) :
        self.configs_n_vals["index_finger_prev"] = self.configs_n_vals["index_finger_curr"]
        self.configs_n_vals["index_finger_curr"] = 1 if data[self.configs_n_vals["index_finger_idx"]] > self.configs_n_vals["click_threshold"] else 0
        
        if self.configs_n_vals["index_finger_prev"] == 1 and self.configs_n_vals["index_finger_curr"] == 0:
            pyautogui.mouseUp()
        elif self.configs_n_vals["index_finger_prev"] == 1 and self.configs_n_vals["index_finger_curr"] == 0:
            pyautogui.mouseDown()

        self.configs_n_vals["midle_finger_prev"] = self.configs_n_vals["midle_finger_curr"]
        self.configs_n_vals["midle_finger_curr"] = 1 if data[self.configs_n_vals["midle_finger_idx"]] > self.configs_n_vals["midle_threshold"] else 0

        if self.configs_n_vals["middle_finger_prev"] == 1 and self.configs_n_vals["middle_finger_curr"] == 0:
            pyautogui.mouseUp()
        elif self.configs_n_vals["middle_finger_prev"] == 1 and self.configs_n_vals["middle_finger_curr"] == 0:
            pyautogui.mouseDown()

    

    def calibrate(self) :

        print("calibrate()")

        app = QtWidgets.QApplication(sys.argv)
        
        print("app object generated")


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
            self.calibrate_window = N
            
    def transformCoord(self, coord) :
        """
        coord : [x_coord, y_coord]
        """
        coord = np.array([coord[0], coord[1], 1]).reshape(3, 1)

        transformed = np.matmul(
            self.configs_n_vals["homography"],
            coord
        )
        
        print(transformed)
        
        transformed = transformed.reshape(3,)
        transformed /= transformed[2]

        print(transformed)

        print()

        return [transformed[0], transformed[1]]

'''