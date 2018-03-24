import socket
HOST = '127.0.0.1'
# Endereco IP do Servidor
PORT = 5000
# Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)
con, cliente = tcp.accept()
print ('Conectado por', cliente)
while True:
    msg = con.recv(1024).decode()
    if not msg: break
    msg = '>' + msg + '<'
    print (cliente, msg)
    con.send(msg.encode())
print ('Finalizando conexao do cliente', cliente)
con.close()
