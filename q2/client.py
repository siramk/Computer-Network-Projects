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
JOBS = [1,2]

FORMAT = "[%(levelname)s] {%(lineno)d} \n- %(message)s"
logging.basicConfig(format=FORMAT, level= logging.INFO)
logger = logging.Logger(__file__)

COMMANDS = [
    "list: gives list of connections online on server",
    "send client_id msg: will ask server to send 'msg' to cient with 'client_id'",
    "quit: to end the connection with server"
]

class Client:
    
    def __init__(self):
        self.serverHost = '192.168.0.106'
        self.serverPort = 7777
        self.socket = None
    
    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print('\nQuitting gracefully')
        if self.socket:
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                logger.error('Could not close connection %s' % str(e))
        sys.exit(0)
        return

    def create(self):
        try:
            self.socket = socket.socket()
        except socket.error as e:
            logger.error("Socket creation error" + str(e))
        return

    def connect(self):
        try:
            self.socket.connect((self.serverHost, self.serverPort))
        except socket.error as e:
            logger.error("Socket connection error: " + str(e))
            raise
        return

    def send_to_server(self):
        while True:
            command_str = input("COMM>")
            if len(command_str)==0:
                continue
            elif command_str.strip() == 'help':
                for cmd in COMMANDS:
                    print(cmd)
            elif command_str == "quit": break
            else:                
                command = str.encode(command_str) 
                try:
                    self.socket.send(command)
                except Exception as e:
                    logger.error(f"Unable to send message to server: {e} ")
                    break
        return 
        
    def recv_from_server(self):
        while True:
            try:
                data = self.socket.recv(20480)
            except Exception as ex:
                logger.error('Communication error: %s\n' %str(ex))
                break
            data_str = data.decode('utf-8')
            if data == b'': break
            elif data_str == " ":
                try:
                    self.socket.send(str.encode(" "))
                except Exception as ex:
                    logger.error(f"Unale to send msg to server: {ex}")
                    break
            elif data_str:
                print(data_str)
        return

def recv_work(client):
    client.recv_from_server()
    queue.task_done()
    queue.task_done()

def send_work(client):
    client.send_to_server()
    queue.task_done()
    queue.task_done()

def create_jobs():
    """ Each list item is a new job """
    for x in JOBS:
        queue.put(x)
    queue.join()
    return
def main():
    client = Client()
    client.register_signal_handler()
    client.create()
    while True:
        try:
            client.connect()
        except Exception as e:
            print("Error on socket connections: %s" %str(e))
            time.sleep(5)     
        else:
            break    
           
    t1 = threading.Thread(target= recv_work, args= (client,))
    t2 = threading.Thread(target= send_work, args= (client, ))
    t1.daemon =  True        
    t2.daemon =  True        
    t1.start()
    t2.start()
    create_jobs()
    client.socket.close()
    
if __name__ == "__main__":
    main()
    
    
  
