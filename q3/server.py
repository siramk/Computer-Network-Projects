
import socket

HOST = ""
PORT = int(input("ENTER PORT NUMBER> "))


with socket.socket(family=socket.AF_INET6, type= socket.SOCK_STREAM) as s:
    s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connection established to: ', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.send(data)
    