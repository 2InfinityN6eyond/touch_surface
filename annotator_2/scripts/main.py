#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import copy
import cv2 as cv
import cv2
import numpy as np
import mediapipe as mp
import pickle

from utils import (
    calc_bounding_rect,
    calc_landmark_list,
    draw_bounding_rect,
    draw_landmarks
)

def main(data_root_path, scenrio):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence = 0.3,
        min_tracking_confidence  = 0.3,
    )

    frame_width  = [1920, 1280, 1280, 640][0]
    frame_height = [1080, 1024,  720, 480][0]

    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, frame_height)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    record_flag = -1

    video_writer = None

    while True:
        start_time = time.time()

        ret, image = cap.read()
        if not ret:
            break

        image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        crop_failed_flag = False
        if results.multi_hand_landmarks is not None:
            
            hand_landmarks = results.multi_hand_landmarks[0]
            #for hand_landmarks in results.multi_hand_landmarks :
            
            # Bounding box calculation
            brect = calc_bounding_rect(debug_image, hand_landmarks)

            left, top, right, bottom = brect

            width, height = right - left, bottom - top                

            center_x = int((left + right) / 2)
            center_y = int((top + bottom) / 2)

            crop_top = max(center_y - height, 0)
            crop_bottom = min(center_y + height, debug_image.shape[0])
            crop_left = max(center_x - width,  0)
            crop_right = min(center_x + width,  debug_image.shape[1])
            
            save_image = copy.deepcopy(debug_image[
                crop_top:crop_bottom,
                crop_left:crop_right,
                :
            ])

            hand_image = np.zeros(
                (
                    max(crop_bottom - crop_top, crop_right - crop_left),
                    max(crop_bottom - crop_top, crop_right - crop_left),
                    3
                ),
                dtype=np.uint8
            )

            hand_image[:crop_bottom - crop_top, :crop_right - crop_left, :] = debug_image[
                crop_top:crop_bottom,
                crop_left:crop_right,
                :
            ]

            landmark_list = calc_landmark_list(debug_image, hand_landmarks)
            debug_image = draw_bounding_rect(True, debug_image, brect)
            debug_image = draw_landmarks(
                debug_image,
                landmark_list
            )        

            landmark_transformed = (
                np.array(landmark_list) - np.array([
                    crop_left, crop_top
                ])
            ).tolist()

            if crop_failed_flag :
                print("crop failed!!")
                continue

            fps = 1 / (time.time() - start_time)
            cv.putText(
                debug_image,
                f"{scenario} {fps:3f}fps. {'recording..' if record_flag == 1 else ''}",
                (10, 60),
                cv.FONT_HERSHEY_SIMPLEX, 2.0,
                (0, 0, 0), 2
            )
            cv.putText(
                debug_image,
                f"{scenrio} {fps:3f}fps. {'recording..' if record_flag == 1 else ''}",
                (10, 60),
                cv.FONT_HERSHEY_SIMPLEX, 2.0,
                (255,255,255), 2
            )
        
            hand_image = draw_landmarks(
                hand_image,
                landmark_transformed
            )      

            hand_image = cv2.resize(
                hand_image,
                (debug_image.shape[0], debug_image.shape[0]),
                cv2.INTER_AREA
            )
            vis_image = np.hstack((debug_image, hand_image))

            cv.imshow(
                'Hand Gesture Recognition',
                cv2.resize(
                    vis_image, 
                    (vis_image.shape[1] // 3, vis_image.shape[0] // 3),
                    cv2.INTER_AREA        
                )
            )
            
            if record_flag == 1 :
                if video_writer is None :
                    save_file_idx = 1
                    
                    data_root_path = os.path.join(
                        data_root_path,
                        time.strftime("%Y_%m_%d__%H_%M_%S")
                    )
                    os.makedirs(data_root_path, exist_ok=True)

                    video_writer = cv2.VideoWriter(
                        os.path.join(data_root_path, 'vide.mp4'),
                        cv2.VideoWriter_fourcc(*"MP4V"),
                        30,
                        (
                            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        )
                    )   
                video_writer.write(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                with open(
                    os.path.join(data_root_path, f'{save_file_idx:06d}.pkl'),
                    "wb"
                ) as fp :
                    pickle.dump(
                        {
                            "image" : save_image,
                            "landmark_list" : landmark_transformed
                        },
                        fp
                    )
                save_file_idx += 1

        key = cv.waitKey(10)
        if key in [27, ord("q"), ord("Q")]:  # ESC
            cv.destroyAllWindows()
            break

        if key in [ord(' '), ord('s')] :
            record_flag *= -1

    cap.release()

    if video_writer is not None :
        video_writer.release()

if __name__ == '__main__':
    scenarios = [
        "f1",
        "f2",
        "f3",
        "f2_f3",
        "pen",
        "pen_hover",
        "eraser",
        "none"
    ]

    scenario = sys.argv[1]
    print(scenario)

    if scenario not in scenarios :
        print("invalid scenario")
        exit()

    resource_root_path = "/".join(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        ).split("/")[:-1]
    ) + "/"

    data_root_path = os.path.join(resource_root_path, "data", scenario)
    main(data_root_path, scenario)