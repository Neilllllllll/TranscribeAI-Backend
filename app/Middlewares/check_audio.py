from flask import request
from functools import wraps
from app.Helpers.responses import error

"""
Décorateur qui vérifie l'authenticité d'un fichier audio : 
- Existance 
- Nom non vide
- Mimetype du binaire
"""

def check_audio(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'audioFile' not in request.files:
            return error("Aucun fichier audio fourni", 400)

        audio_file = request.files['audioFile']

        if audio_file.filename == '':
            return error("Le fichier audio est vide", 400)

        if not audio_file.mimetype.startswith("audio/"):
            return error(f"Fichier non audio reçu (MIME={audio_file.mimetype})", 400)

        return f(*args, **kwargs)

    return wrapper
