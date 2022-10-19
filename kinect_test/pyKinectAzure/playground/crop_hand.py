import sys
import cv2
import time

import os
from hamcrest import less_than

from torch import col_indices_copy

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_PATH)

import pykinect_azure as pykinect

if __name__ == "__main__":

    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries(track_body=True)

    # Modify camera configuration
    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_2160P
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1440P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
    #print(device_config)

    # Start device 
    device = pykinect.start_device(config=device_config)

    # Start body tracker
    bodyTracker = pykinect.start_body_tracker()

    cv2.namedWindow('Color image with skeleton',cv2.WINDOW_NORMAL)

    prev_time = time.time()
    while True:
        
        # Get capture
        capture = device.update()

        # Get body tracker frame
        body_frame = bodyTracker.update()

        # Get the color image
        ret, color_image = capture.get_color_image()
        if not ret:
            continue

        ret, depth_image = capture.get_colored_depth_image()


        ret, transformed_colored_depth_image = capture.get_transformed_colored_depth_image()
        print(transformed_colored_depth_image.shape)

        # Draw the skeletons into the color image
        #color_skeleton = body_frame.draw_bodies(color_image, pykinect.K4A_CALIBRATION_TYPE_COLOR)
        color_skeleton = body_frame.draw_bodies(depth_image)
        


        body_joints = None
        try :
            body_joints = body_frame.get_body2d()
        except Exception as e : 
            print(e)
            print('-------')
            continue

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


        left_hand_center_x = int((left_hand_right_end + left_hand_left_end) / 2)
        left_hand_center_y = int((left_hand_top_end + left_hand_bottom_end) / 2)

        left_hand_left_end   = max(left_hand_center_x - (left_hand_right_end - left_hand_left_end), 0)
        left_hand_right_end  = min(left_hand_center_x + (left_hand_right_end - left_hand_left_end), color_image.shape[1])
        left_hand_top_end    = max(left_hand_center_y - (left_hand_bottom_end - left_hand_top_end), 0)
        left_hand_bottom_end = min(left_hand_center_y + (left_hand_bottom_end - left_hand_top_end), color_image.shape[0])

        curr_time = time.time()
        interval = curr_time - prev_time
        prev_time = curr_time


        
        cv2.line(
            color_skeleton,
            body_joints.joints[7].get_coordinates(),
            body_joints.joints[9].get_coordinates(),
            #(int(body_joints[9][1]), int(body_joints[9][0])),
            #(int(body_joints[7][1]), int(body_joints[7][0])),
            (255,255),
            10,
            cv2.LINE_8
        )

        cv2.rectangle(
            color_skeleton,
            (left_hand_left_end, left_hand_top_end),
            (left_hand_right_end, left_hand_bottom_end),
            (255,255,255),
            3,
            cv2.LINE_8
        )        

        cv2.putText(
            color_skeleton,
            str(1 / interval),
            (0, 40),
            cv2.FONT_ITALIC,
            1,
            (255,255,255),
            2
        )

        # Overlay body segmentation on depth image
        cv2.imshow('Color image with skeleton',color_skeleton)	


        # Press q key to stop
        if cv2.waitKey(1) == ord('q'):  
            break