from app.Schemas.base_schema import BaseSchema

class TranscriptionDiarizationSchema(BaseSchema):
    @staticmethod
    def check_params(data):
        # Liste des paramètres autorisés
        allowed = ["min_speakers", "max_speakers"]
        # Liste des paramètres obligatoires
        required = [] 

        # 1. Validation des paramètres (autorisation + obligation)
        is_valid, errors = BaseSchema.validate(data, required, allowed)

        if not is_valid:
            return False, errors

        # 2. Vérification de logique métier
        try:
            # Vérifie le type 
            min_spk = int(data.get('min_speakers', 1))
            max_spk = data.get('max_speakers')
            if max_spk:
                max_spk = int(data.get('max_speakers'))

            # Vérifie la logique

            if max_spk and min_spk > max_spk:
                return False, ["min_speakers ne peut pas être supérieur à max_speakers"]
            
            # Retourne les données typées en int pour le controller
            return True, {
                "min_speakers": min_spk,
                "max_speakers": max_spk
            }
        except (ValueError, TypeError):
            return False, ["Les paramètres de locuteurs doivent être des nombres entiers."]
