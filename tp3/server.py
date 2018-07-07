import sys
import socket
import json

def main():
    UDP_PORT = sys.argv[1]

    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM, 0) # UDP
    
    sock.bind(('127.0.0.1', int(UDP_PORT)))

    subscriptions = {}
    
    while(True):
	    data, source_addr = sock.recvfrom(500) # buffer size is 500 bytes
	    message = json.loads(data.decode())
	    
	    messageType = message['type']

	    #print("Received: ", message, " from ", source_addr[0], " - Type: ", messageType)   

	    if(messageType == "subscribe"):
	    	if((source_addr[0] + ":" + str(source_addr[1])) in subscriptions):
	    		subscriptions[source_addr[0] + ":" + str(source_addr[1])]['tags'].append(message['tag'])
	    		sock.sendto(("Inscrito na tag #" + message['tag']).encode(), (source_addr[0], source_addr[1]))
	    	else:
	    		subscriptions[source_addr[0] + ":" + str(source_addr[1])] = {}
	    		subscriptions[source_addr[0] + ":" + str(source_addr[1])]['tags'] = []
	    		subscriptions[source_addr[0] + ":" + str(source_addr[1])]['tags'].append(message['tag'])
	    		sock.sendto(("Inscrito na tag #" + message['tag']).encode(), (source_addr[0], source_addr[1]))
	    elif(messageType == "unsubscribe"):
	    	if(message['tag'] in subscriptions[source_addr[0] + ":" + str(source_addr[1])]['tags']):
	    		subscriptions[source_addr[0] + ":" + str(source_addr[1])]['tags'].remove(message['tag'])
	    		sock.sendto(("Removido da tag #" + message['tag']).encode(), (source_addr[0], source_addr[1]))
	    elif(messageType == "message"):
	    	for client in subscriptions:
	    		for tag in subscriptions[client]['tags']:
	    			if tag in message['content']: # Recebeu mensagem de interesse desse cliente
	    				#print("Enviando msg para ", client.split(':')[0], ":", client.split(':')[1])
	    				sock.sendto(message['content'].encode(), (client.split(':')[0], int(client.split(':')[1])))
	    				
	    #print(subscriptions)

if __name__ == '__main__':
    main()