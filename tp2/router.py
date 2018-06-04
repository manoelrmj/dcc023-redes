#!/usr/bin/env python3

import struct
import socket
import sys
import argparse
import threading
import time
import json

class Router(object):

    """docstring for Router"""

    # Enlaces físicos
    links = {}

    # Tabela de roteamento
    routingTable = {}

    running = True
    UDP_PORT = 55151
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM, 0) # UDP

    def __init__(self, addr, period):
        super(Router, self).__init__()
        self.addr = addr
        self.period = period

    def start(self):
        # Start router threads
        
        # CLI Thread
        try:
            cliT = threading.Thread(target=self._cliThread, args=())
            cliT.start()
        except:
            print("Error: unable to start CLI thread")  

        # # Thread to receive messsages
        try:
            recT = threading.Thread(target=self._recThread, args=())
            recT.start()
        except:
            print("Error: unable to start REC thread")

        # Thread to send update messages
        try:
            updT = threading.Thread(target=self._updThread, args=())
            updT.start()
        except:
            print("Error: unable to start UPD thread")

    def addLink(self, destinationAddr, weight):
        self.links[destinationAddr] = weight

    def removeLink(self, destinationAddr):
        del self.links[destinationAddr]

    def _cliThread(self):
        # Command Line Interface
        inputString = ""
        while(inputString != "quit"):
            inputString = input('> ')
            inputParts = inputString.split(' ')
            
            if(inputParts[0] == "add"):
                self.addLink(inputParts[1], inputParts[2])
                #print(self.links)

            elif(inputParts[0] == "del"):
                self.removeLink(inputParts[1])
                #print(self.links)
            else:
                if(inputParts[0] != "quit"):
                    print("Invalid command. Please, try again.")
            #print(inputParts)

        self.running = False

        return

    def _recThread(self):
        #self.sock = socket.socket(socket.AF_INET, # Internet
        #             socket.SOCK_DGRAM, 0) # UDP
        self.sock.bind((self.addr, self.UDP_PORT))

        while self.running :
            data, source_addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            json_data = json.loads(data.decode())
            #print(json_data['type'])
            if(json_data['type'] == 'data'):
                print(json_data['payload'])
            elif(json_data['type'] == 'update'):
                #print(json_data)
                print("Update from ", source_addr)
                for key,value in json_data['distances'].items():
                    print (key,value)
                print(json_data)

    def _updThread(self):
        UDP_MESSAGE = {}
        UDP_MESSAGE['type'] = 'update'
        UDP_MESSAGE['source'] = self.addr
        
        while(self.running):
            
            for neighbour in self.links.keys():
                UDP_MESSAGE['distances'] = {}
                UDP_MESSAGE['destination'] = neighbour
                for key, value in self.links.items():
                    if(key != neighbour):
                        UDP_MESSAGE['distances'][key] = value
            
                self.sock.sendto(json.dumps(UDP_MESSAGE).encode(), (neighbour, self.UDP_PORT))

            time.sleep(int(self.period))

def main():
    
    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help="IPv4 address to listen on (usually inside 127.0.1.0/24)", required=True)
    parser.add_argument('--update-period', help="Period between updates [2.0]", required=True)
    parser.add_argument('--startup', help="File to read startup commands from")

    args = parser.parse_args()

    router = Router(args.addr, args.update_period)
    router.start()

    #print(args)    

if __name__ == '__main__':
    main()
