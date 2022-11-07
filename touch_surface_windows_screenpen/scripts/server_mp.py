import os
import socket
from multiprocessing import Process, Queue

class ScreenDrawInitializer(Process) :
    def __init__(
        self,
        HOST = "127.0.0.1",
        PORT = 65432
    ) : 
        super(ScreenDrawInitializer, self).__init__()
        self.HOST = HOST
        self.PORT = PORT
    
    def run(self) :
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"address:{addr}")
                print(f"calling screenpen")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        continue
                    print(data)

                    os.system("screenpen")
                    #conn.sendall(data)
                    #10.5.103.169


if __name__ == "__main__" :
    screen_draw_server = ScreenDrawInitializer()
    