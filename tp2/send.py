import socket
import json

UDP_IP = "127.0.1.1"
UDP_PORT = 55151
#MESSAGE = "Hello, World!"

MESSAGE = {}
MESSAGE['type'] = 'data'
MESSAGE['source'] = '127.0.1.1'
MESSAGE['destination'] = '127.0.1.1'
MESSAGE['payload'] = 'Hello World!'

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(json.dumps(MESSAGE), (UDP_IP, UDP_PORT))