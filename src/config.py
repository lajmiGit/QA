import os

# --- Configuration des Modèles ---

# Le "Cerveau" : Raisonnement complexe, Agents et Synthèse
MODEL_PRO = "gemini-3-pro-preview"

# Le "Capteur" : Vision, Vidéo et Lectures rapides
MODEL_FLASH = "gemini-3-flash-preview"

# --- Quotas Réels (Confirmés via Screenshots) ---
# Gemini 3 Pro : 25 RPM, 1M TPM, 250 RPD
MAX_RPM_PRO = 25 

# Gemini 3 Flash : 1000 RPM, 1M TPM, 10K RPD
MAX_RPM_FLASH = 1000

# --- Paramètres de Résilience ---
MAX_RETRIES = 10
TIMEOUT = 600
