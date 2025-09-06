#from dotenv import load_dotenv
from threading import Thread
import logging
import time
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from decimal import Decimal, getcontext, ROUND_DOWN
from functools import wraps
from datetime import datetime
#######################################################################################################################
import sqlite3
import hashlib
#######################################################################################################################
import os
from collections import defaultdict
#=========================================
import re
from collections import Counter
#######################################################################################################################
# Set up logging
logging.basicConfig(level=logging.INFO)
################################

####################################################################################################################################################
# Initialisation de Flask-SocketIO
app = Flask(__name__)
Profit_cumul = 0
log_data = ""  # Global log data
log_data1 = ""  # Global log data
###################################
timeframe_du_footprint = ""
ancien_timeframe_du_footprint = ""
donnees_du_footprint = ""
ancien_donnees_du_footprint = ""
dictionnaire_des_bougies = {}

donees_de_derniere_bougie = ""
ancien_donees_de_derniere_bougie = "ancienne données"
donees_de_avant_derniere_bougie = "" 
ancien_donees_de_avant_derniere_bougie = "ancienne données"

signal_pr_indicateur = 0
###################################
app.secret_key = 'your_secret_key'  # Set a secret key for sessions
####################################################################################################################################################
bot_running = True
logs =""""""
ajust_logs =""""""
transactions_logs = """"""
Solde_USDT = "None"
#####################################################################################################
#FONCTIONS DEDIES AUX LOGS
from datetime import datetime
def log_message(message):
    global logs
    timestamped_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
    
    logs +=f"\n{ timestamped_message}"  # concatène le nouveau message à la chaîne logs
    logging.info(timestamped_message)

def log_ajust_message(message):
    global ajust_logs
    timestamped_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
    #ajust_logs=nettoyer_logs(ajust_logs)
    ajust_logs += f"\n{ timestamped_message}"  # concatène le nouveau message à la chaîne logs
    logging.info(timestamped_message)

def log_transactions(message):
    global transactions_logs
    timestamped_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
    #transactions_logs=nettoyer_logs(transactions_logs)
    transactions_logs += f"\n{ timestamped_message}"  # concatène le nouveau message à la chaîne logs
    logging.info(timestamped_message)

def save_logs_to_file(log_message):
    timestamped_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {log_message}"
    file_path = os.path.join(os.getcwd(), 'logs.txt')
    with open(file_path, 'a', encoding='utf-8', errors='replace') as file:
        file.write(timestamped_message + '\n')

def nettoyer_logs(texte, nb_lignes_max=100):
    # Découpe la chaîne en lignes
    lignes = texte.strip().split('\n')
    
    # Si plus de 20 lignes, on garde les 20 dernières
    if len(lignes) > nb_lignes_max:
        lignes = lignes[-nb_lignes_max:]
    # Reconstruit la chaîne avec les lignes conservées
    return '\n'.join(lignes)
#FONCTIONS DEDIES AUX LOGS
#####################################################################################################

#ANALYSE DU FOOTprint####################################################################################################################
def volumes_trading_bot():
    global bot_running, donnees_du_footprint, ancien_donnees_du_footprint, timeframe_du_footprint, ancien_timeframe_du_footprint, donees_de_derniere_bougie
    bot_running = True
    save_logs_to_file(":::: 1_Fonction de detection de volume::::::::::::::::::::::::::::")
    #log_message(":::: 1_Fonction de detection de volume::::::::::::::::::::::::::::")
    #while bot_running:  # S'assurer que les processus en cours sont terminés
    try:
        save_logs_to_file(":::: 2_Fonction de detection de volume::::::::::::::::::::::::::::")
            #log_message(":::: 2_Fonction de detection de volume::::::::::::::::::::::::::::")
        if donnees_du_footprint != ancien_donnees_du_footprint and donnees_du_footprint != "":
            setup_volume_detection(donees_de_derniere_bougie, donees_de_avant_derniere_bougie)
            save_logs_to_file(f"\nAffichons les données des volumes\n{donnees_du_footprint}\n==============================\n")
            ancien_donnees_du_footprint = donnees_du_footprint
            ancien_timeframe_du_footprint = timeframe_du_footprint
        else :
            save_logs_to_file("\n=== Aucune Nouvelle Donnée Détectée ===")
            #time.sleep(10)
    except Exception as e:
        save_logs_to_file(f"[Erreur boucle principale] {e}")
        log_message(f"[Erreur boucle principale] {e}")
        #time.sleep(10)
    #save_logs_to_file("Arrêt du bot Démandé.")
    #log_message("Arrêt du bot Démandé.")
#######################################################################################################################
def enregistrer_donnees_dns_dictionnaire(data_text):#paa besoin d'y toucher
    global dictionnaire_des_bougies
    print("Enregistrement dans un dictionnaire...")
    save_logs_to_file("Enregistrement dans un dictionnaire...")
    print("data_text = ", data_text)
    save_logs_to_file(f"data_text = {data_text} ")
    # Initialisation du dictionnaire
    parsed_data = defaultdict(dict)
    # Lecture ligne par ligne
    for line in data_text.splitlines():
        if not line.strip():
            continue  # sauter les lignes vides
        # Séparer les parties principales
        parts = line.strip().split('@')
        # Extraire date (ou ID) et le reste
        #3003@115160,0x/3/Baissière;
        bougie_id = parts[0]  # Ex: "3003"
        values = parts[1:]  # Ex: ["115160,0x/3/"] ou ["115160,0x/3/Baissière"]
        save_logs_to_file(f"values = {values}")
        print(f"values = {values}")

        save_logs_to_file(f"ID = {bougie_id}")
        print(f"ID = {bougie_id}")
        # Extraire les sous-valeurs
        #val_parts = values[0].split('/')
        val_parts = [p for p in values[0].split("/") if p]
        try:
            value0 = int(val_parts[0])#volume
            save_logs_to_file(f"value0 = {value0}")
            print(f"value0 = {value0}")

            value1 = int(val_parts[1])#7/4 valeur
            save_logs_to_file(f"value1 = {value1}")
            print(f"value1 = {value1}")

            value2 = val_parts[2]#bid
            save_logs_to_file(f"value2 = {value2}")
            print(f"value2 = {value2}")

            value4 = val_parts[4]#ask
            save_logs_to_file(f"value4 = {value4}")
            print(f"value4 = {value4}")
            # x
            value5 = val_parts[5]#ask
            save_logs_to_file(f"value5 = {value5}")
            print(f"value5 = {value5}")

        except (IndexError, ValueError):
            continue  # en cas de format invalide
        # Vérifier présence d’un label (Bullish/Bearish)
        label = val_parts[5] if len(val_parts) > 5 and val_parts[5] else None
        # Stockage dans le dict
        parsed_data[bougie_id] = {
            "value0": value0,
            "value1": value1,
            "value2": value2,
            "value4": value4,
            #"value5": value5
            }
        if label:
            parsed_data[bougie_id]["label"] = label
    # Exemple d'accès
    dictionnaire_des_bougies = parsed_data
    print("Enregistré dans le dictionnaire...")
    save_logs_to_file("Enregistré dans le dictionnaire...")

    print("parsed data = ",parsed_data)
    save_logs_to_file(f"parsed data = {parsed_data}")

    print("dictionnaire des bougies = ", dictionnaire_des_bougies)
    save_logs_to_file(f"dictionnaire des bougies = {dictionnaire_des_bougies}")
    # -> {'value1': 0, 'value2': 7, 'value3': 5, 'label': 'Bullish'}
#####################################################################################
def verif_nature_derniere_bougie(parsed_data):
    bougie_ids = sorted(parsed_data.keys(), key=int)  # trier les bougie_id numériquement
    save_logs_to_file(f"bougie_ids → {bougie_ids}")
    print(f"bougie_ids → {bougie_ids}")
    if bougie_ids:
        last_bougie = bougie_ids[-1]
        # Récupérer le label directement
        last_label = parsed_data[last_bougie].get("label", None)
        save_logs_to_file(f"Dernière bougie {last_bougie} → label: {last_label}")
        log_message(f"Dernière bougie → {last_label}")
        return last_label
    else:
        save_logs_to_file("Les données de la dernière bougie n'ont pas été reçues.")
        log_message("Les données de la dernière bougie n'ont pas été reçues.")
        return None


def verif_nature_avant_derniere_bougie(parsed_data):
    # Suppose que `parsed_data` est ton dictionnaire déjà rempli
    bougie_ids = sorted(parsed_data.keys(), key=int)  # trier les bougie_id numériquement
    if len(bougie_ids) > 1:
        second_last_bougie = bougie_ids[-2]
        # Récupérer le time_id max pour chaque bougie
        second_last_time_id = max(parsed_data[second_last_bougie].keys(), key=int)
        # Récupérer les labels s'ils existent
        second_last_label = parsed_data[second_last_bougie][second_last_time_id].get("label", None)
        save_logs_to_file(f"Avant-dernière bougie {second_last_bougie}/{second_last_time_id} → label: {second_last_label}")
        log_message(f"Avant-dernière bougie → {second_last_label}")
        return second_last_label
    else:
        save_logs_to_file("Les données de l'avant dernière bougie n'ont pas été recues.")
        log_message("Les données de l'avant dernière bougie n'ont pas été recues.")
        return None

def verif_nature_deux_fois_avant_derniere_bougie(parsed_data):
    # Suppose que `parsed_data` est ton dictionnaire déjà rempli
    bougie_ids = sorted(parsed_data.keys(), key=int)  # trier les bougie_id numériquement
    if len(bougie_ids) > 2:
        third_last_bougie = bougie_ids[-3]
        # Récupérer le time_id max pour chaque bougie
        third_last_time_id = max(parsed_data[third_last_bougie].keys(), key=int)
        # Récupérer les labels s'ils existent
        third_last_label = parsed_data[third_last_bougie][third_last_time_id].get("label", None)
        save_logs_to_file(f"2 fois Avant-dernière bougie {third_last_bougie}/{third_last_time_id} → label: {third_last_label}")
        log_message(f"2 fois Avant-dernière bougie → {third_last_label}")
        return third_last_label
    else:
        save_logs_to_file("Les données de la bougie 2 fois avant dernière n'ont pas été recues.")
        log_message("Les données de la bougie 2 fois avant dernière n'ont pas été recues.")
        return None
#####################################################################################
def derniere_bougie(post_data):
    global donees_de_derniere_bougie, ancien_donees_de_derniere_bougie
    #save_logs_to_file("\n")
    if ancien_donees_de_derniere_bougie != donees_de_derniere_bougie:
        save_logs_to_file(f"\ndonnee de toute les bougies dispo :: {post_data}")
        # Séparer les lignes
        lignes = post_data.strip().splitlines()
        # Vérifie qu'il y a bien au moins une ligne
        if lignes:
            # 1️⃣ Dernière ligne
            derniere_ligne = lignes[-1]
            # 2️⃣ Extraire la première valeur (avant le "/")
            prefix = derniere_ligne.split("@")[0]
            # 3️⃣ Trouver toutes les lignes qui commencent par ce prefix
            lignes_associees = [ligne for ligne in lignes if ligne.startswith(prefix)]
            # 4️⃣ Joindre dans une nouvelle chaîne
            donees_de_derniere_bougie = "\n".join(lignes_associees)
            # 5️⃣ Afficher le résultat final
            save_logs_to_file(f"\ntoute les donnees associees a la dernière bougie sont :: {donees_de_derniere_bougie}")
            save_logs_to_file(f"Première valeur de la dernière ligne : {prefix}")
            save_logs_to_file(f"Lignes correspondantes : {derniere_ligne}")
            #save_logs_to_file(donees_de_derniere_bougie)
        else:
            save_logs_to_file("Aucune ligne dans post_data.")
    else : 
        save_logs_to_file("les données n'on pas changés.")
        save_logs_to_file(donees_de_derniere_bougie)

def avant_derniere_bougie(post_data):
    global donees_de_avant_derniere_bougie, ancien_donees_de_avant_derniere_bougie
    #save_logs_to_file("\n")
    if ancien_donees_de_avant_derniere_bougie != donees_de_avant_derniere_bougie:
        save_logs_to_file(f"\ndonnee de toute les bougies dispo :: {post_data}")
        # Séparer les lignes
        lignes = post_data.strip().splitlines()
        # Vérifie qu'il y a bien au moins une ligne
        if lignes:
            # 1️⃣ Dernière ligne
            avant_derniere_ligne = lignes[-1]
            # 2️⃣ Extraire la première valeur (avant le "@")
            #prefix = derniere_ligne.split("@")[0]-1
            prefix = int(avant_derniere_ligne.split("@")[0]) - 1  # calcul en entier
            prefix_str = str(prefix)                          # reconversion en chaîne
            # 3️⃣ Trouver toutes les lignes qui commencent par ce prefix
            lignes_associees = [ligne for ligne in lignes if ligne.startswith(prefix_str)]
            # 4️⃣ Joindre dans une nouvelle chaîne
            donees_de_avant_derniere_bougie = "\n".join(lignes_associees)
            # 5️⃣ Afficher le résultat final
            save_logs_to_file(f"\ntoute les donnees associees a l avant dernière bougie sont :: {donees_de_avant_derniere_bougie}")
            save_logs_to_file(f"Première valeur de l avant dernière ligne : {prefix_str}")
            save_logs_to_file(f"Lignes correspondantes : {avant_derniere_ligne}")
            #save_logs_to_file(donees_de_avant_derniere_bougie)
        else:
            save_logs_to_file("Aucune ligne dans post_data.")
    else : 
        save_logs_to_file("les données n'on pas changés.")
        save_logs_to_file(donees_de_avant_derniere_bougie)
#####################################################################################
def recuperer_volume_der_bougie(texte):
    cible = "00"
    if cible in texte:
        # On découpe la chaine sur les "/"
        morceaux = texte.split("/")
        # Parcourir chaque morceau pour trouver celui qui contient "0000"
        for morceau in morceaux:
            if cible in morceau:
                print("Sous-chaîne trouvée :", morceau)
                return morceau  # On retourne la sous-chaine trouvée
    return 0  # Rien trouvé

def recuperer_volume_avnt_der_bougie(texte):
    # Découper la chaîne en morceaux séparés par "/"
    morceaux = texte.split("/")
    
    # Parcourir chaque morceau
    for morceau in morceaux:
        # Vérifier si la longueur est exactement de 6 caractères
        if len(morceau) == 6:
            print("Sous-chaîne trouvée :", morceau)
            save_logs_to_file(f"recuperer_volume_avnt_der_bougie Sous-chaîne trouvée : {morceau}")
            return morceau  # Retourner le premier morceau trouvé
    
    return 0  # Rien trouvé
#####################################################################################
def detect_repetitions_volume(texte: str) -> bool:# dans la meme bougie
#ECRIT TON CODE ICI IL DOIT RETOURNER TRUE SI 3 DONNEE PAREIL SONT DETECTE DANS L"ASK ET FALSE SI C EST LE CONTRAIRE
    if True:
        print("setup vente :: un meme ASK a ete détecté au moins trois fois dans la derniere bougie")

        return True
    else:
        print("Aucun volume répétée")
        return False
#####################################################################################
def extraire_valeurs_utiles_pr_cprer_elements_rpt_dns_deux_bougies(texte):# dans la meme bougie
    valeurs = set()
    for ligne in texte.splitlines():
        if "@" in ligne:
            partie = ligne.split("@", 1)[1]
            morceaux = [m for m in partie.split("/") if m]  # supprimer vides
            if len(morceaux) < 6:
                # prendre le dernier élément numérique si dispo
                if morceaux[-1].isdigit():
                    valeurs.add(f"/{morceaux[-1]}/")
    return valeurs
##################################################################################################################################################
##c'est surtout ici que tu dois travailler #######################################################################################################
def setup_volume_detection(derniere_bougie, avant_derniere_bougie):
    global dictionnaire_des_bougies,signal_pr_indicateur, SYMBOL
    save_logs_to_file("\n")
    save_logs_to_file(":::: Vérifions si SETUP est détecté ::::::::::::::::::::::")
    log_message(":::: Vérifions si SETUP est détecté ::::::::::::::::::::::")
    # Découpe en lignes et garde seulement celles avec du contenu réel
    lignes_utiles_dans_derniere_bougie = [ligne for ligne in derniere_bougie.strip().split('\n') if ligne.strip()]
    nb_lignes_utiles_dans_derniere_bougie = len(lignes_utiles_dans_derniere_bougie)
    save_logs_to_file(f"Nombre de lignes utiles dans derniere bougie : {nb_lignes_utiles_dans_derniere_bougie}")

    lignes_utiles_dans_avant_derniere_bougie = [ligne for ligne in avant_derniere_bougie.strip().split('\n') if ligne.strip()]
    nb_lignes_utiles_dans_avant_derniere_bougie = len(lignes_utiles_dans_avant_derniere_bougie)
    save_logs_to_file(f"Nombre de lignes utiles dans avant-derniere bougie : {nb_lignes_utiles_dans_avant_derniere_bougie}")

    if nb_lignes_utiles_dans_derniere_bougie>1 and nb_lignes_utiles_dans_avant_derniere_bougie>1 :
        # Séparer en lignes
        lignes_dans_derniere_bougie = derniere_bougie.strip().split('\n')
        lignes_dans_avant_derniere_bougie = avant_derniere_bougie.strip().split('\n')
        nature_derniere_bougie = verif_nature_derniere_bougie(dictionnaire_des_bougies) # verifier le type de la bougie analysee
        save_logs_to_file(f"setup achat :: nature_derniere_bougie = {nature_derniere_bougie}")
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::SIGNAL ACHAT
        if nature_derniere_bougie == "Baissière": # verifier le type de la bougie analysee
            derniere_ligne_dans_derniere_bougie = lignes_dans_derniere_bougie[-1] #recuperer la 1ERE ligne de la derniere bougie.
            avant_derniere_ligne_dans_derniere_bougie = lignes_dans_derniere_bougie[-2] #recuperer la 2EME ligne de la derniere bougie.
            deux_fois_avant_derniere_ligne_dans_derniere_bougie = lignes_dans_derniere_bougie[-3] #recuperer la 3EME ligne de la derniere bougie.
            trois_fois_avant_derniere_ligne_dans_derniere_bougie = lignes_dans_derniere_bougie[-4] #recuperer la 4EME ligne de la derniere bougie.

            derniere_ligne_dans_avant_derniere_bougie = lignes_dans_avant_derniere_bougie[-1] #recuperer la premiere ligne de l'avant derniere bougie.
            save_logs_to_file(f"setup achat :: derniere_ligne_dans_avant_derniere_bougie {derniere_ligne_dans_avant_derniere_bougie}")#test
            """DETECTONS LE DOUBLE ZERO"""
            if "00/" in derniere_ligne_dans_derniere_bougie or "00/" in  avant_derniere_ligne_dans_derniere_bougie or "00/" in  deux_fois_avant_derniere_ligne_dans_derniere_bougie or "00/" in trois_fois_avant_derniere_ligne_dans_derniere_bougie:
                save_logs_to_file("setup achat :: Double zero detecte")
                log_message("setup achat :: une config détectée")
                
                """verifier si la bougie precedente n'est pas trop eloignee du double zero pour VENTE"""
                #recuperons la valeur du volume Double zero detecte
                if "00/" in derniere_ligne_dans_derniere_bougie :
                    volume_double_zero = int(recuperer_volume_der_bougie(derniere_ligne_dans_derniere_bougie))
                    volume_bougie_precedente = int(recuperer_volume_der_bougie(derniere_ligne_dans_avant_derniere_bougie))
                elif "00/" in  avant_derniere_ligne_dans_derniere_bougie :
                    volume_double_zero = int(recuperer_volume_der_bougie(avant_derniere_ligne_dans_derniere_bougie))
                    volume_bougie_precedente = int(recuperer_volume_der_bougie(derniere_ligne_dans_avant_derniere_bougie))
                elif "00/" in  deux_fois_avant_derniere_ligne_dans_derniere_bougie :
                    volume_double_zero = int(recuperer_volume_der_bougie(deux_fois_avant_derniere_ligne_dans_derniere_bougie))
                    volume_bougie_precedente = int(recuperer_volume_avnt_der_bougie(derniere_ligne_dans_avant_derniere_bougie))
                elif "00/" in trois_fois_avant_derniere_ligne_dans_derniere_bougie :
                    volume_double_zero = int(recuperer_volume_der_bougie(trois_fois_avant_derniere_ligne_dans_derniere_bougie))
                    volume_bougie_precedente = int(recuperer_volume_avnt_der_bougie(derniere_ligne_dans_avant_derniere_bougie))


                print(f"setup achat :: volume de la bougie double zero = {volume_double_zero}, volume de la bougie precedente = {volume_bougie_precedente}")
                save_logs_to_file(f"setup achat :: volume de la bougie double zero = {volume_double_zero}, volume de la bougie precedente = {volume_bougie_precedente}")
                
                """verifier si bougie precedente est dans la meme zone que le double zero"""
                #verifions si le volume de la bougie precedente n'est pas superieur a celui du double zero et aussi si il est a un bon ecart
                if volume_double_zero <= volume_bougie_precedente and volume_double_zero + 45 > volume_bougie_precedente :
                    save_logs_to_file("setup achat :: bougie precedente est dans la meme zone que le double zero")
                    log_message("setup achat :: bougie precedente est dans la meme zone que le double zero")


                    """DETECTONS LE DOUBLE VOLUME"""
                    triple_volume_dns_dern_bougie = detect_repetitions_volume(derniere_bougie)# verifions si le meme volume se retrouve 3 fois dans la meme bougie
                    if triple_volume_dns_dern_bougie : # verifier si triple volume ou detecte dans les deux bougie sont detecte
                        save_logs_to_file("setup achat :: un meme volume a ete détecté au moins trois fois dans la meme bougie")
                        save_logs_to_file("setup achat :: SIGNAL ACHAT DETECTE")
                        log_message("setup achat :: SIGNAL ACHAT DETECTE")
                        signal_pr_indicateur = 2
                    else :
                        save_logs_to_file("setup achat ::  SIGNAL ACHAT -NON- DETECTE")
                        log_message("setup achat :: SIGNAL ACHAT ANNULE ><ni double volume ni triple volume n'ont ete detecte><")
                        if signal_pr_indicateur != 1 :
                            signal_pr_indicateur = -2
                else : 
                    save_logs_to_file("setup achat :: la bougie precedente est trop eloignee du double zero")
                    log_message("setup achat :: SIGNAL ACHAT ANNULE ><bougie precedente est trop eloignee du double zero><")
                    if signal_pr_indicateur != 1 :
                        signal_pr_indicateur = -2
            else :
                save_logs_to_file("setup achat :: double zero -NON- DETECTE ")
                log_message("setup achat :: double zero -NON- DETECTE ")
                if signal_pr_indicateur != 1 :
                    signal_pr_indicateur = -2
        else:
            save_logs_to_file("setup achat :: la bougie analysee n'est pas Haussiere")
            log_message("setup achat :: SIGNAL ACHAT -NON- DETECTE")
            if signal_pr_indicateur != 1 :
                signal_pr_indicateur = -2
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::SIGNAL ACHAT
##c'est surtout ici que tu dois travailler ##################################################################################################################################################
##################################################################################################################################################
def est_2359():
    maintenant = datetime.now()
    return maintenant.hour == 23 and maintenant.minute == 59
def supperviseur():
    global bot_running,logs,ajust_logs,transactions_logs,SYMBOL,symbol, timeframe_du_footprint, ancien_timeframe_du_footprint, donnees_du_footprint, ancien_donnees_du_footprint
    while True:
        try:
            #funct_montant_minimum()
            #log_message("Superviseur actif...")
            if est_2359():
                log_message("Il est 23h59 Vidons la mémoire ram!")
                timeframe_du_footprint = ""
                ancien_timeframe_du_footprint = ""
                donnees_du_footprint = ""
                ancien_donnees_du_footprint = ""
                logs =""""""
                ajust_logs =""""""
                transactions_logs = """"""
            #else:
                #log_message("Ce n'est pas encore 23h59.")
            time.sleep(3)
        except Exception as e:
            log_message(f"[Erreur boucle principale] {e}")
            time.sleep(3)
bot_thread = Thread(target=supperviseur)
bot_thread.daemon = True
bot_thread.start()
#############################################################################################################################################################

#FROM ATAS ##################################################################################################################################################
@app.route("/envoie_des_donnees_test", methods=["POST"])
def envoie_des_donnees_volumes():
    global donnees_du_footprint, bot_running, dictionnaire_des_bougies, signal_pr_indicateur
    post_data1 = request.get_data(as_text=True)
    print(f"donnees brut du test ::\n {post_data1}")
    save_logs_to_file(f"donnees brut des volumes ::\n {post_data1}")
    print(f"remplacons toute les virgules par des points")
    save_logs_to_file(f"remplacons toute les virgules par des points")
    post_data = post_data1.replace(",0", "")
    print(f"> ::\n {post_data}")
    save_logs_to_file(f"> ::\n {post_data}")

    if bot_running:
        log_message("::: Donnees Des Volumes Recus Traitons Les")
    else :
        log_message("::: Donnees Des Volumes Recus Mais Le Robot Est A L'arret")
    # Traitement
    lignes_nettoyees = []
    for ligne in post_data.splitlines():
        if '/' in ligne:
            debut = ligne.find('/') + 1  # pour enlever le slash initial
            fin = ligne.find(';') if ';' in ligne else len(ligne)
            cleaned = ligne[debut:fin].strip()
            lignes_nettoyees.append(cleaned)
            save_logs_to_file(f"traitement ligne: {cleaned}")
    # Création d'une nouvelle chaîne
    nouvelle_chaine = '\n'.join(lignes_nettoyees)
    #############################################
    # Étape 1 : Séparer les lignes
    lignes = donnees_du_footprint.splitlines()
    # Étape 2 : Regrouper les lignes par identifiant
    groupes = defaultdict(list)
    ordre_identifiants = []  # Pour garder l'ordre d'apparition
    for ligne in lignes:
        identifiant = ligne.split("@")[0] + "@"
        if identifiant not in groupes:
            ordre_identifiants.append(identifiant)
        groupes[identifiant].append(ligne)
    # Étape 3 : Garder les 5 derniers identifiants
    derniers_identifiants = ordre_identifiants[-5:]
    # Étape 4 : Réassembler les lignes
    lignes_filtrees = []
    for identifiant in derniers_identifiants:
        lignes_filtrees.extend(groupes[identifiant])
    # Étape 5 : Réécrire la variable
    donnees_du_footprint = "\n".join(lignes_filtrees)
    #############################################
    donnees_du_footprint += f"\n{nouvelle_chaine}"
    save_logs_to_file(f"donnees traitees des volumes ::\n {donnees_du_footprint}")
    save_logs_to_file("")
    print(f"donnees traitees des volumes ::\n {donnees_du_footprint}")
    derniere_bougie(donnees_du_footprint)
    avant_derniere_bougie(donnees_du_footprint)
    enregistrer_donnees_dns_dictionnaire(donnees_du_footprint)
    volumes_trading_bot()
    valeur = signal_pr_indicateur
    signal_pr_indicateur = 0  # remise à zéro
    save_logs_to_file("::: /mon_endpoint")
    print("::: /mon_endpoint")
    return jsonify(message="Reçu", valeur=valeur)
#############################################################################################################################################################
@app.route("/envoie_du_timeframe_du_footprint", methods=["POST"])
def envoie_du_timeframe_du_footprint():
    global timeframe_du_footprint, ancien_timeframe_du_footprint,donnees_du_footprint, ancien_donnees_du_footprint, bot_running
    post_data = request.get_data(as_text=True).strip()
    if not post_data:
        return "Aucune donnée reçue", 400
    if bot_running:
        log_message(f"Timeframe du footprint :: {post_data}")
        save_logs_to_file(f"Timeframe du footprint :: {post_data}")
        timeframe_du_footprint = post_data
        if timeframe_du_footprint != ancien_timeframe_du_footprint and timeframe_du_footprint != "":
            save_logs_to_file("\n::: Nouvelle Timeframe détectée, vidons ancien_donnees_du_footprint et donnees_du_footprint")
            log_message("::: Nouvelle Timeframe détectée, vidons ancien_donnees_du_footprint et donnees_du_footprint")
            donnees_du_footprint = ""
            ancien_donnees_du_footprint = ""
        elif timeframe_du_footprint == ancien_timeframe_du_footprint:
            save_logs_to_file("\n::: Toujours le même Timeframe")
    else :
        save_logs_to_file("\n::: Donnée Timeframe recu mais le robot est à l'arret")
        log_message("::: Donnée Timeframe Recu Mais Le Robot Est A L'arret")
    return "ok", 200, {"Content-Type": "text/plain"}
#FROM ATAS ##################################################################################################################################################
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")