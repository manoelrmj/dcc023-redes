import socket
import sys
import _thread

# Por meio do map, aplica a função de transformação a todos os elementos da
# string, gerando uma nova string decifrada.
def decipher(string, cipher):
    return ''.join(map(lambda x:chr(((ord(x)-cipher-97)%26)+97),string))

def handleRequest(con):
    con.settimeout(15.0)
    # Recebe inteiro de 4 bytes (tamanho da string)
    msg = con.recv(4)
    string_size = int.from_bytes(msg, byteorder='big')

    # Recebe a string
    msg = con.recv(string_size)
    string = msg.decode()

    # Recebe a chave
    msg = con.recv(4)
    key = int.from_bytes(msg, byteorder='big')

    # Decifra
    decipheredString = decipher(string, key)
    print(decipheredString)

    # Envia mensagem decifrada
    con.send (decipheredString.encode())

    # Finaliza a conexao
    con.close()

def main():
    # Endereco IP do Servidor
    HOST = ''
    # Porta
    PORT = int(sys.argv[1])

    # Cria o socket
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    orig = (HOST, PORT)
    tcp.bind(orig)
    tcp.listen(10)

    # Aguarda conexões
    while True:
        con, client = tcp.accept()
        # Inicia uma nova thread para atender a requisição
        try:
           _thread.start_new_thread(handleRequest, (con, ) )
        except:
           print ("Erro ao criar thread")

if __name__ == '__main__':
    main()
