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
        response = requests.post(API_URL, json=mock_data)
        if response.status_code == 201:
            logger.info(f"Beca enviada con éxito: {mock_data['title']}")
        else:
            logger.error(f"Error al enviar beca: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"No se pudo conectar con el backend: {e}")

if __name__ == "__main__":
    logger.info("Scraper listo. Intervalo: %s segundos", SCRAPER_INTERVAL_SECONDS)
    while True:
        run_scraper()
        time.sleep(SCRAPER_INTERVAL_SECONDS)