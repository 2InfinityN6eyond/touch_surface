import socket
from multiprocessing import Process, Queue, Pipe, Value

class BluetoothReciever_(Process) :
    def __init__(
        self,
        to_data_bridge:Queue = None
    ) -> None:
        super(BluetoothReciever, self).__init__()
        self.to_data_bridge = to_data_bridge


    def run(self) :
        device_mac_addr = "08:3A:F2:52:14:DA"
        device_port = 1

        sock = socket.socket(
            socket.AF_BLUETOOTH,
            socket.SOCK_STREAM,
            socket.BTPROTO_RFCOMM
        )
        sock.connect((device_mac_addr, device_port))

        while True :
            buf = sock.recv(1024)
            decoded = buf.decode("utf-8").split("|")[0]
            if len(decoded) < 4 :
                continue
            data = list(filter(len, decoded.split(" ")))
            if len(data) != 3 :
                continue
            data = list(map(int, data))

            if self.to_data_bridge is not None :
                self.to_data_bridge.put(data)
            else :
                print(data)

class BluetoothReciever(Process) :
    def __init__(
        self,
        to_data_bridge:Queue
    ) -> None:
        super(BluetoothReciever, self).__init__()
        self.to_data_bridge = to_data_bridge

    def run(self) :
        server_ip = '127.0.0.1'
        server_port = 50050

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        sock.connect((server_ip, server_port))

        while True :
            buf = sock.recv(1024)
            data = buf.decode('utf-8').split(" ")

            self.to_data_bridge.put(list(map(int, data)))

if __name__ == "__main__" :
    bluetooth_reciever = BluetoothReciever(None)
    bluetooth_reciever.start()
