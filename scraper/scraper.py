import logging
import os
import sys
import time
from datetime import date

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL")
SCRAPER_SOURCE_URL = os.getenv("SCRAPER_SOURCE_URL", "")
SCRAPER_SOURCE_NAME = os.getenv("SCRAPER_SOURCE_NAME", "Fuente externa")
SCRAPER_DEFAULT_COUNTRY = os.getenv("SCRAPER_DEFAULT_COUNTRY", "Global")

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "40"))
BACKEND_WAIT_SECONDS = int(os.getenv("BACKEND_WAIT_SECONDS", "20"))
BACKEND_MAX_WAIT_SECONDS = int(os.getenv("BACKEND_MAX_WAIT_SECONDS", "300"))


class ScholarshipPayload(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=5000)
    provider: str = Field(min_length=2, max_length=150)
    country: str = Field(default="Global", max_length=100)
    deadline: str
    url: HttpUrl
    tags: list[str] = Field(default_factory=list)

    @field_validator("deadline")
    @classmethod
    def validate_deadline_iso(cls, value: str) -> str:
        parsed = date_parser.parse(value).date()
        return parsed.isoformat()

    @field_validator("tags")
    @classmethod
    def sanitize_tags(cls, tags: list[str]) -> list[str]:
        cleaned = []
        for tag in tags:
            normalized = tag.strip()
            if normalized and len(normalized) <= 50:
                cleaned.append(normalized)
        return cleaned[:15]


def resolve_api_url(raw_url: str | None) -> str | None:
    if not raw_url:
        return None
    normalized = raw_url.strip().rstrip("/")
    if normalized.endswith("/api/v1/scholarships"):
        return normalized
    return f"{normalized}/api/v1/scholarships"


def resolve_health_url(final_api_url: str) -> str:
    return final_api_url.replace("/api/v1/scholarships", "/actuator/health")


def wait_for_backend(final_api_url: str) -> bool:
    health_url = resolve_health_url(final_api_url)
    elapsed_seconds = 0

    while elapsed_seconds < BACKEND_MAX_WAIT_SECONDS:
        try:
            response = requests.get(health_url, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.ok:
                logger.info("Backend listo en %s", health_url)
                return True
            logger.debug("Backend aun no listo (%s). Status: %s", health_url, response.status_code)
        except requests.RequestException as exc:
            logger.debug("Esperando backend en %s: %s", health_url, exc)

        time.sleep(BACKEND_WAIT_SECONDS)
        elapsed_seconds += BACKEND_WAIT_SECONDS

    logger.error("El backend no respondio en %s segundos", BACKEND_MAX_WAIT_SECONDS)
    return False


def text_or_default(node, default: str) -> str:
    if node is None:
        return default
    return node.get_text(strip=True) or default


def normalize_deadline(raw_deadline: str) -> str:
    if not raw_deadline:
        return (date.today().replace(year=date.today().year + 1)).isoformat()
    return date_parser.parse(raw_deadline).date().isoformat()


def extract_scholarships_static(source_url: str) -> list[dict]:
    response = requests.get(source_url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    candidates = soup.select("article, .scholarship-card, .scholarship-item, .opportunity")

    raw_items: list[dict] = []
    for card in candidates[:25]:
        link = card.select_one("a[href]")
        title_node = card.select_one("h2, h3, .title")
        desc_node = card.select_one("p, .description, .summary")
        provider_node = card.select_one(".provider, .organization, .institution")
        country_node = card.select_one(".country, .location")
        deadline_node = card.select_one("time, .deadline, .closing-date")
        tag_nodes = card.select(".tag, .tags span, .badge")

        href = link.get("href", "").strip() if link else ""
        if not href:
            continue
        if href.startswith("/"):
            href = source_url.rstrip("/") + href

        raw_deadline = ""
        if deadline_node is not None:
            raw_deadline = deadline_node.get("datetime", "").strip() or deadline_node.get_text(strip=True)

        raw_items.append(
            {
                "title": text_or_default(title_node, "Beca sin titulo"),
                "description": text_or_default(desc_node, "Sin descripcion disponible"),
                "provider": text_or_default(provider_node, SCRAPER_SOURCE_NAME),
                "country": text_or_default(country_node, SCRAPER_DEFAULT_COUNTRY),
                "deadline": normalize_deadline(raw_deadline),
                "url": href,
                "tags": [n.get_text(strip=True) for n in tag_nodes],
            }
        )

    return raw_items


def get_raw_scholarships() -> list[dict]:
    if SCRAPER_SOURCE_URL:
        logger.info("Extrayendo becas desde fuente estatica: %s", SCRAPER_SOURCE_URL)
        return extract_scholarships_static(SCRAPER_SOURCE_URL)

    logger.warning("SCRAPER_SOURCE_URL no configurada; usando dataset minimo de ejemplo")
    return [
        {
            "title": "Beca de Excelencia Python Cloud",
            "description": "Beca para especialistas en automatizacion y desarrollo cloud.",
            "provider": "Comunidad Tech",
            "country": "Global",
            "deadline": "2026-12-31",
            "url": "https://python-cloud-example.com/beca-1",
            "tags": ["Python", "Cloud", "Remote"],
        }
    ]


def validate_scholarships(raw_items: list[dict]) -> list[ScholarshipPayload]:
    validated: list[ScholarshipPayload] = []
    for item in raw_items:
        try:
            validated.append(ScholarshipPayload(**item))
        except ValidationError as exc:
            logger.warning("Item descartado por validacion: %s", exc.errors())
    return validated


def send_to_backend(final_api_url: str, scholarship: ScholarshipPayload) -> None:
    payload = scholarship.model_dump(mode="json")
    response = requests.post(final_api_url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)

    if response.status_code in (200, 201):
        logger.info("Beca enviada: %s", payload["title"])
    elif response.status_code == 409:
        logger.info("Duplicada (omitida): %s", payload["url"])
    else:
        logger.error("Error enviando beca (%s): %s", response.status_code, response.text)


def run_scraper() -> None:
    final_api_url = resolve_api_url(API_URL)
    if not final_api_url:
        logger.error("La variable API_URL no esta configurada")
        sys.exit(1)

    logger.info("Iniciando scraping hacia API: %s", final_api_url)

    if not wait_for_backend(final_api_url):
        sys.exit(1)

    try:
        raw_items = get_raw_scholarships()
    except requests.RequestException as exc:
        logger.error("No se pudo descargar fuente de scraping: %s", exc)
        sys.exit(1)

    scholarships = validate_scholarships(raw_items)
    logger.info("Items extraidos: %s | validos: %s", len(raw_items), len(scholarships))

    for scholarship in scholarships:
        try:
            send_to_backend(final_api_url, scholarship)
        except requests.RequestException as exc:
            logger.error("Error de red al enviar beca %s: %s", scholarship.url, exc)


if __name__ == "__main__":
    run_scraper()