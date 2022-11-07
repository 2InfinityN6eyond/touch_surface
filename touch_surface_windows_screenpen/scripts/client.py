import socket

HOST = "10.5.106.134"  # The server's hostname or IP address
HOST = "127.0.0.1"
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
