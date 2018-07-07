import socket
import sys
import json
import select

MSG_SIZE = 500

class Client():

    def __init__(self, host, lPort, sPort):
        self.host = host
        self.localPort = int(lPort)
        self.serverPort = int(sPort)
        self.isRunning = True
        self.cmd = ">"

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            
            self.socket.bind(('', self.localPort))
            self.socket.connect((self.host, self.serverPort))   
            print("Connected to Server ", self.host)
        except socket.error:
            print ("Connection Failed.")
            sys.exit(1)
    
    def run(self):
        while self.isRunning:
            try:
                sys.stdout.write(self.cmd)
                sys.stdout.flush()

                _input, _output, _except = select.select([0, self.socket], [], [])

                for i in _input:
                    if i == 0:
                        data = sys.stdin.readline().strip()
                        if data:                           
                           if data[0] == '+':
                              self.subscribe(data[1:])
                           elif data[0] == '-':
                              self.unsubscribe(data[1:])
                           else:
                              self.send_message(data)
                        else:
                            print("")
                    elif i == self.socket:
                        data, source_addr = self.socket.recvfrom(MSG_SIZE)
                        if not data:
                            self.isRunning = False
                            break
                        else:
                            sys.stdout.write(data.decode() + "\n")
                            sys.stdout.flush()
                    else:
                        continue

            except KeyboardInterrupt:
                print ("...")
                self.socket.close()
                break                            
    
    def send_message(self, msg):
        message = {}
        message['type'] = 'message'
        message['content'] = msg                          
        # print("Sending message: ", json.dumps(message))
        self.socket.sendto(json.dumps(message).encode(), (self.host, self.serverPort))

    # Identificadores de tag são uma sequência de letras e números (sem pontuação).
    def subscribe(self, tag):
       
        if not tag.isalnum():
            print("A Tag must contain only alphanumeric characters.")
        else:
            message = {}
            message['type'] = 'subscribe'
            message['tag'] = tag 
            # print("Subscribing to #", tag)
            self.socket.sendto(json.dumps(message).encode(), (self.host, self.serverPort))

    def unsubscribe(self, tag):
        if not tag.isalnum():
            print("A Tag must contain only alphanumeric characters.")
        else:
            message = {}
            message['type'] = 'unsubscribe'
            message['tag'] = tag 
            # print("Unsubscribing to #", tag)
            self.socket.sendto(json.dumps(message).encode(), (self.host, self.serverPort))
    

if __name__ == "__main__":    
    localPort = sys.argv[1]
    serverIP = sys.argv[2]
    serverPort = sys.argv[3]
    client = Client(serverIP, localPort, serverPort)
    client.run()
