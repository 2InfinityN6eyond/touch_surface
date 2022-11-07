import socket
import random
import time

host_addr = '127.0.0.1'
host_port = 50050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host_addr, host_port))
server_socket.listen()

conn, client_addr = server_socket.accept()

with conn :
    print(f"connected to {client_addr}")

    while True :
        message = "{} {} {}".format(
            random.randint(1, 4000),
            random.randint(1, 4000),
            random.randint(1, 4000)
        )

        conn.send(
            message.encode('utf-8')
        )

        time.sleep(0.05)