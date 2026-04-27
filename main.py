import requests
from bs4 import BeautifulSoup
import time
import os

# Fonction pour vérifier la disponibilité des logements
def check_housing():
    # Note : Ton URL pointe vers "tools/41", mais le code HTML fourni indique "tools/42" (année 2025-2026). 
    # N'hésite pas à ajuster le 41 en 42 dans l'URL si nécessaire.
    url = 'https://trouverunlogement.lescrous.fr/tools/42/search?bounds=2.2235574_49.9505487_2.3457767_49.846837&locationName=Amiens+%2880000%29'
    
    # Ajout d'un User-Agent classique pour éviter les blocages antibot du CROUS
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Lève une erreur si le code HTTP n'est pas 200
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # On cible précisément les titres des résidences dans les annonces
        titres_residences = soup.find_all('h3', class_='fr-card__title')
        
        for titre in titres_residences:
            nom_residence = titre.text.lower()
            # On vérifie si "saint leu" ou "saint-leu" est présent dans le titre de l'annonce
            if 'saint leu' in nom_residence or 'saint-leu' in nom_residence:
                return True
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de la page : {e}")
        return False

# Fonction pour envoyer la notification
def send_notification():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # Message personnalisé
    message = '🚨 Bonne nouvelle ! Un logement est disponible à la Résidence Saint-Leu !'
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print('✅ Notification sent successfully.')
        else:
            print(f'❌ Failed to send notification. Status code: {response.status_code}')
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")

# Boucle principale du bot
def main():
    print("🚀 Bot started... Surveillance exclusive de la résidence Saint-Leu en cours.")
    already_notified = False
    
    while True:
        try:
            if check_housing():
                if not already_notified:
                    send_notification()
                    already_notified = True
            else:
                # Si plus aucune annonce Saint Leu n'est là, on réinitialise pour la prochaine fois
                already_notified = False
                
            time.sleep(60)
            
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
