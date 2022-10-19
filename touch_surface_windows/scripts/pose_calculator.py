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

from pynput.mouse import Button, Controller

mouse = Controller()

#sys.path.append()

ROOT_PATH = os.path.dirname((os.path.abspath(__file__)))
sys.path.insert(0, ROOT_PATH)
print(sys.path)

from pykinect_azure.k4abt.body2d import Body2d
import pykinect_azure as pykinect
from pykinect_azure.k4a import _k4a



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


        self.screen_height = pyautogui.size().height
        self.screen_width = pyautogui.size().width

        self.run()


    def run(self) :
        """
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
        """


        # Initialize the library, if the library is not found, add the library path as argument
        pykinect.initialize_libraries(track_body=True)

        # Modify camera configuration
        device_config = pykinect.default_configuration
        device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1440P
        #device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_UNBINNED
        device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
        #print(device_config)

        self.device = pykinect.start_device(config=device_config)
        self.bodyTracker = pykinect.start_body_tracker()

        calibration = self.device.get_calibration(
            pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED,
            pykinect.K4A_COLOR_RESOLUTION_1440P
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
    
        capture = self.device.update()
        #body_frame = self.bodyTracker.update()

        ret, color_image = capture.get_color_image()

        self.image = color_image

        #ret, depth_color_image = capture.get_colored_depth_image()
        #ret, body_image_color = body_frame.get_segmentation_image()

        #print(depth_color_image.shape, body_image_color.shape)

        return ret
 
        #combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)
        #combined_image = body_frame.draw_bodies(combined_image)
        
        body_joints = None
        try :
            if body_frame.get_num_bodies() > 0 :
                body_joints = body_frame.get_body2d()
                body_handle = body_frame.get_body().handle()
                
                body_joints = Body2d.create(
                    body_handle=body_handle,
                    calibration=calibration,
                    bodyIdx=0,
                    dest_camera= pykinect.K4A_CALIBRATION_TYPE_COLOR
                )
            self.body_joints = body_joints
        except Exception as e : 
            self.body_joints = None
            return 

        try :            
            left_hand_left_end = min(
                body_joints.joints[7].get_coordinates()[0],
                body_joints.joints[9].get_coordinates()[0]
            )
            left_hand_right_end = max(
                body_joints.joints[7].get_coordinates()[0],
                body_joints.joints[9].get_coordinates()[0]
            )
            left_hand_top_end = min(
                body_joints.joints[7].get_coordinates()[1],
                body_joints.joints[9].get_coordinates()[1]
            )
            left_hand_bottom_end = max(
                body_joints.joints[7].get_coordinates()[1],
                body_joints.joints[9].get_coordinates()[1]
            )

            bbox_shape = max(left_hand_right_end - left_hand_left_end, left_hand_bottom_end - left_hand_top_end)

            left_hand_center_x = int((left_hand_right_end + left_hand_left_end) / 2)
            left_hand_center_y = int((left_hand_top_end + left_hand_bottom_end) / 2)

            left_hand_left_end   = max(left_hand_center_x - bbox_shape, 0)
            left_hand_right_end  = min(left_hand_center_x + bbox_shape, color_image.shape[1])
            left_hand_top_end    = max(left_hand_center_y - bbox_shape, 0)
            left_hand_bottom_end = min(left_hand_center_y + bbox_shape, color_image.shape[0])
            

            hand_cropped_image = color_image[left_hand_top_end:left_hand_bottom_end, left_hand_left_end:left_hand_right_end].copy()
            """
            cv2.line(
                color_image,
                body_joints.joints[7].get_coordinates(),
                body_joints.joints[9].get_coordinates(),
                (255,255),
                10,
                cv2.LINE_8
            )

            cv2.rectangle(
                color_image,
                (left_hand_left_end, left_hand_top_end),
                (left_hand_right_end, left_hand_bottom_end),
                (255,255,255),
                3,
                cv2.LINE_8
            )        
            """

            """
            image = cv2.cvtColor(hand_cropped_image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
            """

        except Exception as e :
            print(e)


        """
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
        """


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

