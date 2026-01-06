from app.Config import BaseConfig
import os 
# Configuration spécifique à l'API Flask
class APIConfig(BaseConfig.BaseConfig):
    API_PORT = int(os.getenv("API_PORT", "5000")) # Port d'écoute de l'API
    HOST = "0.0.0.0" # Écoute sur toutes les interfaces réseau

    # Formats audio autorisés
    raw_formats = os.getenv("FORMAT_AUDIO_ALLOWED", "wav,mp3,ogg,m4a")
    FORMAT_AUDIO_ALLOWED = {f.strip() for f in raw_formats.split(",")}

