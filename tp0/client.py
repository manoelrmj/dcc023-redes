import socket
import sys
import struct

def caesarCipher(string, shift):
    return ''.join(map(lambda x:chr(((ord(x)+shift-97)%26)+97),string))

def main():
    # Endereco IP do Servidor
    HOST = sys.argv[1]
    # Porta
    PORT = sys.argv[2]
    # String a ser enviada
    STRING_MSG = sys.argv[3]
    # Tamanho da string
    CIPHER = int(sys.argv[4])

    # Cria o socket TCP
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.settimeout(15.0)
    dest = (HOST, int(PORT))
    tcp.connect(dest)

    # Envia o tamanho da string
    packed_int = struct.pack('>I', int(len(STRING_MSG.encode('utf-8'))))
    tcp.send(packed_int)

    # Envia a string
    tcp.send(caesarCipher(STRING_MSG, CIPHER).encode())

    # Envia a cifra
    packed_int = struct.pack('>I', CIPHER)
    tcp.send(packed_int)

    # Recebe mensagem decifrada
    msg = tcp.recv(len(STRING_MSG.encode('utf-8')))
    print (msg.decode())

    # Fecha a conexão
    tcp.close()

if __name__ == '__main__':
    main()
