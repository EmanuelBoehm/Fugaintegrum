import socket
import sys
import threading
import select
from io import BytesIO
import time
class TcpServer():
    def __init__(self, tcpIP='127.0.0.1', port=9500, debug=False, buffer_size=2048):
        """
        Constructor
        :param TCP_IP: Must be string e.g. "127.0.0.1"
        :param port: integer number e.g. 9500.
        :param buffer_size: integer number most commonly used is 1024
        :param debug: boolean, when true print on connection changes to console
        """
     
        self.TCP_IP = tcpIP
        self.TCP_PORT = port
        self.BUFFER_SIZE = buffer_size
        self.debug = debug
        self.data = None
        self.isDataReceived = False
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        server.bind((self.TCP_IP,self.TCP_PORT))
        server.listen()
        self.server = server
        self.listen_thread = threading.Thread(target=self.ReceiveData,daemon=True)
        self.listen_thread.start()
        

    def __del__(self):
        if self.server != None:
            self.server.close()
        print("del")

    def ReceiveAll(self,socket,BUFFER):
        """
        TCP does not send everything in one package.
        If package is completly send, socket.recv() will return an empty bytestring.
        Depending on the frequency of sending the images there might be problems. 
        """
        temp = socket.recv(BUFFER)
        data = b''
        while len(temp) > BUFFER - 2:
            data += temp
            temp = socket.recv(BUFFER)
        data += temp
        return data



    def ReceiveData(self): #get's called by an external thread
        #self.isDataReceived = False
        server = self.server
        rxset = [server]
        txset = []
        
        while True:
            rxfds, _, _ = select.select(rxset, txset, rxset)
            for sock in rxfds:
                if sock is server:
                    conn, addr = self.server.accept()
                    conn.setblocking(0)
                    rxset.append(conn)
                    if self.debug:
                        print('Connection from address:', addr)
                else:
                    data = self.ReceiveAll(sock,self.BUFFER_SIZE)
                    if data == ";" :
                        print("Received all the data")
                        rxset.remove(sock)
                        sock.close()
                    else:
                        self.data = data
                        self.isDataReceived = True

    #may by external by user to get currrent buffer
    def ReadReceivedData(self):
        """
        This function should be used by the user.
        Return the data that has been received since last call. 
        None if nothing has been received
        :return:
        """
        data = None
        if self.isDataReceived:
            self.isDataReceived = False # reset
            data = self.data
            self.data = None #empty buffer
        return data
