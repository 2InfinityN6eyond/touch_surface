import cv2
from multiprocessing import Process, Queue


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
        
        while True :
            if not self.data_queue.empty() :
                data = self.data_queue.get()

                cv2.imshow("hand_pose", data)
                if cv2.waitKey(1) == ord('q') :
                    break