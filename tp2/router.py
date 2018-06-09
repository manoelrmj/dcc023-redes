#!/usr/bin/env python3

import struct
import socket
import sys
import argparse
import threading
import time
import json
import math

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

    def __init__(self, addr, period, startup):
        super(Router, self).__init__()
        self.addr = addr
        self.period = period
        self.startup = startup

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
        self.routingTable[destinationAddr] = (int(weight), destinationAddr)

    def removeLink(self, destinationAddr):
        del self.links[destinationAddr]
        # Verifica se o link removido era o de menor custo
        if self.routingTable.get(destinationAddr)[1] == destinationAddr:
            del self.routingTable[destinationAddr]

    def _processInput(self, inputString):
        inputParts = inputString.split(' ')
        if(inputParts[0] == "add"):
            self.addLink(inputParts[1], inputParts[2])
            #print(self.links)

        elif(inputParts[0] == "del"):
            self.removeLink(inputParts[1])
            #print(self.links)
        elif(inputParts[0] == "trace"):
            print("TRACE")
        else:
            if(inputParts[0] != "quit"):
                print("Invalid command. Please, try again.")
        #print(inputParts)

    def _cliThread(self):
        # Command Line Interface

        # Le arquivo se especificado
        if(self.startup != None):
            file = open(self.startup, 'r')
            for line in file:
                print("> ", line)
                self._processInput(line)

        inputString = ""
        while(inputString != "quit"):
            inputString = input('> ')
            self._processInput(inputString)
            

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
                # for key,value in json_data['distances'].items():
                #     print (key,value)
                # Atualizar tabela de roteamento
                for key,value in json_data['distances'].items():
                    if(key in self.routingTable):
                        if(value + int(self.links[source_addr[0]]) < self.routingTable[key][0]):
                            self.routingTable[key] = (int(value) + int(self.links[source_addr[0]]), source_addr[0])                            
                    else: 
                        self.routingTable[key] = (int(value) + int(self.links[source_addr[0]]), source_addr[0])
                print("routingTable:")
                print(self.routingTable)

            elif(json_data['type'] == 'trace'):
                print("Trace")

    def _updThread(self):
        UDP_MESSAGE = {}
        UDP_MESSAGE['type'] = 'update'
        UDP_MESSAGE['source'] = self.addr

        
        while(self.running):            
            
            # for neighbour in self.links.keys():
            #     UDP_MESSAGE['distances'] = {}
            #     UDP_MESSAGE['destination'] = neighbour
            #     for key, value in self.links.items():
            #         if(key != neighbour):
            #             UDP_MESSAGE['distances'][key] = value

            for neighbour in self.links.keys():
                UDP_MESSAGE['distances'] = {}
                UDP_MESSAGE['destination'] = neighbour
                for key, value in self.routingTable.items():
                    if(key != neighbour): # Split horizon
                        UDP_MESSAGE['distances'][key] = value[0]
            
                self.sock.sendto(json.dumps(UDP_MESSAGE).encode(), (neighbour, self.UDP_PORT))

            time.sleep(int(self.period))

def main():
    
    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help="IPv4 address to listen on (usually inside 127.0.1.0/24)", required=True)
    parser.add_argument('--update-period', help="Period between updates [2.0]", required=True)
    parser.add_argument('--startup', help="File to read startup commands from")

    args = parser.parse_args()

    router = Router(args.addr, args.update_period, args.startup)
    router.start()

    #print(args)    

if __name__ == '__main__':
    main()
