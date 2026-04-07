import requests
from bs4 import BeautifulSoup
import time
import logging
import os

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL de la API de Spring Boot dentro de la red de Docker
API_URL = os.getenv("API_URL", "http://app:8080/api/v1/scholarships")
SCRAPER_INTERVAL_SECONDS = int(os.getenv("SCRAPER_INTERVAL_SECONDS", "900"))
BACKEND_WAIT_SECONDS = int(os.getenv("BACKEND_WAIT_SECONDS", "5"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))


def wait_for_backend():
    health_url = API_URL.replace("/api/v1/scholarships", "/actuator/health")
    while True:
        try:
            response = requests.get(health_url, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.ok:
                logger.info("Backend disponible: %s", health_url)
                return
        except requests.RequestException:
            pass

        logger.warning(
            "Backend aun no disponible. Reintentando en %s segundos...",
            BACKEND_WAIT_SECONDS,
        )
        time.sleep(BACKEND_WAIT_SECONDS)

def run_scraper():
    logger.info("Iniciando ciclo de scraping...")
    
    # Ejemplo: Simulamos que extraemos datos de una web
    # Aquí iría tu lógica de BeautifulSoup
    mock_data = {
        "title": "Beca de Excelencia Python Cloud",
        "description": "Beca para especialistas en automatización.",
        "provider": "Comunidad Tech",
        "deadline": "2026-12-31",
        "url": "https://python-cloud-example.com/beca-1",
        "tags": ["Python", "Cloud", "Remote"]
    }

    try:
        response = requests.post(API_URL, json=mock_data, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 201:
            logger.info(f"Beca enviada con éxito: {mock_data['title']}")
        else:
            logger.error(f"Error al enviar beca: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"No se pudo conectar con el backend: {e}")

if __name__ == "__main__":
    logger.info("Scraper listo. Intervalo: %s segundos", SCRAPER_INTERVAL_SECONDS)
    wait_for_backend()
    while True:
        run_scraper()
        time.sleep(SCRAPER_INTERVAL_SECONDS)