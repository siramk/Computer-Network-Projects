import socket

HOSTNAME = input("ENTER HOSTNAME OR IP_ADDR> ")   
PORT = int(input("ENTER PORT NUMBER> "))     

addr_info = socket.getaddrinfo(HOSTNAME, PORT)
family = addr_info[0][0]
type = addr_info[0][1]
HOST = addr_info[0][4][0]

with socket.socket(family= family, type= type) as s:
    print("ENTER 'quit' to exit!")
    s.connect((HOST, PORT))
    while True:
        in_data = input("DATA> ")
        if in_data == "quit":
            break
        s.send(str.encode(in_data))
        out_data = s.recv(20480)
        print(out_data.decode('utf-8'))
    s.close()
    