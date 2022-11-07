import os
import time
import pickle
from multiprocessing import Process, Queue, Pipe, Value
from threading import Thread

class DataWriterWorker(Thread) :
    def __init__(self, file_name, file_content) :
        super().__init__()
        self.file_name = file_name
        self.file_content = file_content
        
    def run(self) :
        with open(self.file_name, "wb") as fp :
            pickle.dump(self.file_content, fp)

class DataWriter(Process) :
    def __init__(
        self,
        root_path,
        data_queue:Queue
    ) :
        super().__init__()
        self.daemon = False
        self.runnint = Value('b', True)

        self.out_root_path = os.path.join(
            root_path,
            time.strftime("%Y_%m_%d__%H_%M_%S")
        )

        print(self.out_root_path)
        os.makedirs(self.out_root_path)

        self.data_queue = data_queue

    def run(self) :
        file_name_idx = 1
        while True :
            try :
                if not self.data_queue.empty() :
                    data = self.data_queue.get()
                    file_name = os.path.join(
                        self.out_root_path,
                        f"{file_name_idx:05d}.pkl"
                    )
                    data_writer_worker = DataWriterWorker(
                        file_name,
                        data
                    )
                    data_writer_worker.start()
                    file_name_idx += 1
            except :
                pass