import requests
from bs4 import BeautifulSoup
import logging
import os
import sys

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL") 
REQUEST_TIMEOUT_SECONDS = 30 # Aumentamos el timeout por si Render está despertando

def run_scraper():
    if not API_URL:
        logger.error("La variable de entorno API_URL no está configurada.")
        sys.exit(1)

    logger.info(f"Iniciando ciclo de scraping hacia: {API_URL}")
    
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
        # Si Render está dormido, esta petición tardará unos 20-30 segs en despertar el servicio.
        response = requests.post(API_URL, json=mock_data, timeout=REQUEST_TIMEOUT_SECONDS)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Beca enviada con éxito: {mock_data['title']}")
        elif response.status_code == 409: # Suponiendo que manejas duplicados
            logger.warning(f"⚠️ La beca ya existe en la base de datos.")
        else:
            logger.error(f"❌ Error al enviar: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        logger.error("❌ Error: El backend tardó demasiado en despertar (Timeout).")
    except requests.RequestException as e:
        logger.error(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    run_scraper()