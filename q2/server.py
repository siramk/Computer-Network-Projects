import os
import socket
import subprocess
import time
import signal
import sys
import logging
import threading
from queue import Queue

queue = Queue()
JOBS = [1]



FORMAT = "[%(levelname)s] {%(lineno)d} \n- %(message)s"
logging.basicConfig(format=FORMAT, level= logging.INFO)
logger = logging.Logger(__file__)

class Server:
    
    def __init__(self):
        self.host = ''
        self.port = 7777
        self.socket = None
        self.connections = []
        self.addresses = []
        self.threads = []
        
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

    def create(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            logger.error(f"Connection Error: {e}")
            sys.exit(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return
    
    def bind(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error as ex:
            logger.error(f"scoket binfing error: {ex}")
            time.sleep(5)
            self.bind()
            
    
    def accept_conn(self):    
        while True:
            try:
                conn, addr = self.socket.accept()
                conn.setblocking(1) # waits on socket.recv and socket.send
                self.connections.append(conn)
                self.addresses.append(addr)
                t = threading.Thread(target= server.talk_to_clients, 
                                     args=(len(self.connections)-1, 
                                           self.connections[-1], 
                                           self.addresses[-1]))
                t.daemon = True
                self.threads.append(t)
                t.start()
            except Exception as e:
                logger.error('Error accepting connections: %s' % str(e))
            print('\nConnection has been established with: {0}'.format(addr))
        return
    
    def talk_to_clients(self, client_id, conn, addr):
        while True:
            command = conn.recv(20480)
            command_str = (command.decode('utf-8')).strip()
            if command == b'': break
            if command_str == "list": output_str = self.list()
            elif command_str == "quit": break
            elif command_str[:4] == "send":
                to_id = int(command_str[5])
                msg = command_str[7:]
                msg = f"FROM {addr}: " + msg 
                to_conn = self.connections[to_id]
                to_addr = self.addresses[to_id]
                try:
                    to_conn.send(str.encode(msg))
                except Exception as ex:
                    logger.error("Cannot send message to {} from {}: {}".format(to_addr, addr,ex))
                    continue
                output_str = "MESSAGE sent succefully to {}".format(to_addr)
            else:
                output_str = "Please enter correct command!"
            try:
                conn.send(str.encode(output_str))
            except Exception as ex:
                logger.error("Cannot send status message to client: {} from server:= {}".format(addr,ex))
                
        return
    
    def list(self):
        clients = "-----------CLIENTS-------------\n"
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
            clients += f"{i}: {self.addresses[i]}\n"
        return clients
    
def work(server):
    server.accept_conn()
    queue.task_done()

def create_jobs():
    """ Each list item is a new job """
    for x in JOBS:
        queue.put(x)
    queue.join()
    return
    
if __name__ == "__main__":
    server = Server()
    server.register_signal_handler()
    server.create()
    server.bind()
    t = threading.Thread(target= work, args= (server,))
    t.daemon = True
    t.start()
    create_jobs()
