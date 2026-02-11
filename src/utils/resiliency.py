import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions

def retry_gemini_api(func):
    @retry(
        retry=retry_if_exception_type((
            google.api_core.exceptions.ResourceExhausted,
            google.api_core.exceptions.InternalServerError,
            google.api_core.exceptions.ServiceUnavailable
        )),
        wait=wait_exponential(multiplier=2, min=4, max=70),
        stop=stop_after_attempt(10),
        before_sleep=lambda retry_state: print(f"⚠️ Quotas API atteints ou Erreur Serveur. Attente du prochain cycle... (Tentative {retry_state.attempt_number})")
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
