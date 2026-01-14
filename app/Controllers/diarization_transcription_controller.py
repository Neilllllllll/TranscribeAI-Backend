from flask import request
import app.Helpers as Helpers
from flask import current_app
from app.Schemas import TranscriptionDiarizationSchema

# Créer un job et retourne son uuid
def createDiarizationJob():

    # Validation des données reçues
    is_valid, result = TranscriptionDiarizationSchema.check_params(request.form)
    
    if not is_valid:
        return {"errors": result}, 400
    
    diarization_settings = result
    
    audio_manager = current_app.extensions['audio_manager']
    job_service = current_app.extensions['job_service']
    redis_queue_service = current_app.extensions['redis_diarization_queue_service']

    # Générer un identifiant unique pour le job
    job_uuid = Helpers.generate_token()

    # Enregistrer le fichier audio reçu dans un chemin temporaire
    audio_file = request.files['audioFile']
    audio_file.filename = job_uuid
    file_path = audio_manager.save_audio(audio_file)

    # Créer une entrée job dans la base de données avec le statut "en attente"
    job_service.create_job(job_uuid, file_path, "DIARIZATION", "PENDING", diarization_settings)

    # Enqueue le job dans redis
    redis_queue_service.enqueue_job(job_uuid)

    return Helpers.success({"job_uuid": job_uuid, "status" : "Votre demande de diarization est dans la file d'attente"}, 200)

# Récupérer la transcription par UUID
def getDiarizationByUuid():

    # Récupérer l'UUID du job depuis les paramètres de la requête
    job_uuid = request.args.get('job_uuid')
    if not job_uuid:
        return Helpers.error("Missing job_id parameter", 400)
    
    # Contacter le service de gestion des jobs pour obtenir le statut et la transcription
    job_service = current_app.extensions['job_service']
    job = job_service.get_job_by_uuid(job_uuid)

    if not job or job.type != "DIARIZATION":
        return Helpers.error("Votre demande de diarization n'existe pas", 404)
    elif job.status == "PENDING":
        redis_queue_service = current_app.extensions['redis_diarization_queue_service']
        position = redis_queue_service.get_queue_position(job.uuid)
        return Helpers.success({"job_id": job.uuid,"status": job.status, "position": position})
    elif job.status == "PROCESSING":
        return Helpers.success({"job_id": job.uuid,"status": job.status,})
    elif job.status == "FAILED":
        return Helpers.error("La diarization a échouée", 500)
    else:
        # Calcul du temps de la diarization en seconde 
        diarization_duration = 0
        if job.end_at and job.created_at:
            diarization_duration = (job.end_at - job.created_at).total_seconds()
        # Supprimer le job après récupération à voir comment gérer ça plus tard
        job_service.delete_job(job.uuid)
        return Helpers.success({
            "job_id": job.uuid,
            "status": job.status,
            "result": job.result,
            "diarization_time": diarization_duration
        }, 200)  
