import requests
from bs4 import BeautifulSoup
import logging
import os
import sys
import time

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "90"))
BACKEND_WAIT_SECONDS = int(os.getenv("BACKEND_WAIT_SECONDS", "20"))
BACKEND_MAX_WAIT_SECONDS = int(os.getenv("BACKEND_MAX_WAIT_SECONDS", "300"))


def resolve_api_url(raw_url):
    if not raw_url:
        return None

    normalized = raw_url.strip().rstrip("/")
    if normalized.endswith("/api/v1/scholarships"):
        return normalized

    # Permite configurar API_URL como dominio base en secrets.
    return f"{normalized}/api/v1/scholarships"


def resolve_health_url(final_api_url):
    return final_api_url.replace("/api/v1/scholarships", "/actuator/health")


def wait_for_backend(final_api_url):
    health_url = resolve_health_url(final_api_url)
    elapsed_seconds = 0

    while elapsed_seconds < BACKEND_MAX_WAIT_SECONDS:
        try:
            response = requests.get(health_url, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.ok:
                logger.info("Backend listo en %s", health_url)
                return True
            logger.info("Backend aún no listo (%s). Respuesta: %s", health_url, response.status_code)
        except requests.RequestException as exc:
            logger.info("Esperando backend en %s: %s", health_url, exc)

        time.sleep(BACKEND_WAIT_SECONDS)
        elapsed_seconds += BACKEND_WAIT_SECONDS

    logger.error("❌ El backend no respondió en %s segundos.", BACKEND_MAX_WAIT_SECONDS)
    return False

def run_scraper():
    final_api_url = resolve_api_url(API_URL)

    if not final_api_url:
        logger.error("La variable de entorno API_URL no está configurada.")
        sys.exit(1)

    logger.info(f"Iniciando ciclo de scraping hacia: {final_api_url}")

    if not wait_for_backend(final_api_url):
        sys.exit(1)
    
    # --- AGREGAR LÓGICA REAL DE BEAUTIFULSOUP ---
    # Ejemplo con tus mock_data
    mock_data = {
        "title": "Beca de Excelencia Python Cloud",
        "description": "Beca para especialistas en automatización.",
        "provider": "Comunidad Tech",
        "deadline": "2026-12-31",
        "url": "https://python-cloud-example.com/beca-1",
        "tags": ["Python", "Cloud", "Remote"]
    }

    try:
        response = requests.post(final_api_url, json=mock_data, timeout=REQUEST_TIMEOUT_SECONDS)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Beca enviada con éxito: {mock_data['title']}")
        elif response.status_code == 409: # Suponiendo que manejas duplicados
            logger.warning(f"⚠️ La beca ya existe en la base de datos.")
        elif response.status_code == 404:
            logger.error(
                "❌ Error 404. Verifica que API_URL apunte al backend correcto. URL usada: %s",
                final_api_url,
            )
        else:
            logger.error(f"❌ Error al enviar: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        logger.error("❌ Error: El backend tardó demasiado en despertar (Timeout).")
    except requests.RequestException as e:
        logger.error(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    run_scraper()