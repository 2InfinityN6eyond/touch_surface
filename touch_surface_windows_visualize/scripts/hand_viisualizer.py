import numpy as np
import cv2
from multiprocessing import Process, Queue
import os
import time

save_root_path = "C:/Users/hjp1n/Downloads"
save_image = True

class HandVisualizer(Process) :
    def __init__(
        self,
        data_queue
    ) :
        super(HandVisualizer, self).__init__()
        self.data_queue = data_queue

    def run(self) :
        cv2.namedWindow("hand_pose", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("hand_pose", 1920, 1080)
        
        raw_writer = None
        processed_writer = None
        while True :
            if not self.data_queue.empty() :
                data = self.data_queue.get()
                
                if data["type"] == "raw" :
                    data = data["data"]
                    cv2.imshow("hand_pose", data)
                    if cv2.waitKey(1) == ord('q') :
                        break

                    if save_image :
                        if not raw_writer :
                            raw_writer = cv2.VideoWriter(
                                os.path.join(
                                    save_root_path,
                                    str(int(time.time()))[-4:] + "raw.mp4"
                                ),
                                -1,
                                30,
                                (
                                    data.shape[1],
                                    data.shape[0]
                                )
                            )
                        raw_writer.write(data)
