
import socket

HOST = input("ENTER HOST ADDRESS> ").strip()  
PORT = int(input("ENTER PORT NUMBER> "))
TYPE = input("ENTER TRANSPORT PROTO> ")

if ':' in HOST:
    family = socket.AF_INET6
else:
    family = socket.AF_INET

if TYPE == "TCP":
    type = socket.SOCK_STREAM
else:
    type = socket.SOCK_DGRAM

with socket.socket(family=family, type= type) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connection established to: ', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data)