import socket

IP_PROTO = int(input("SELECT IP PROTOCOL TO BE USED:\n 1.) IPV4 \n 2.) IPV6 \n ENTER THE OPTION NUMBER> "))
HOSTNAME = input("ENTER HOSTNAME OR IP_ADDR> ")   
PORT = int(input("ENTER PORT NUMBER> "))     

if IP_PROTO == 1:
    family = socket.AF_INET
else:
    family = socket.AF_INET6

addr_info = socket.getaddrinfo(HOSTNAME, PORT, family= family)
for i in range(len(addr_info)):
    try:
        HOST = addr_info[i][4][0]
        temp = socket.socket(family=family, type=addr_info[i][1])
        temp.connect((HOST,PORT))
        temp.close()
        break
    except Exception as e:
        temp.close()
        continue
        
family = addr_info[i][0]
type = addr_info[i][1]
HOST = addr_info[i][4][0]

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
    