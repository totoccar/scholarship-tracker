import json
import logging
import os
import sys
import time
from dataclasses import dataclass

import requests

from adapters import AlphaScholarshipScraper, BetaScholarshipScraper, DemoScholarshipScraper
from base import BaseScraper
from models import ScholarshipPayload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL")
SCRAPER_INTERVAL_SECONDS = int(os.getenv("SCRAPER_INTERVAL_SECONDS", "900"))
SCRAPER_SOURCE_URL = os.getenv("SCRAPER_SOURCE_URL", "")
SCRAPER_SOURCE_NAME = os.getenv("SCRAPER_SOURCE_NAME", "Fuente externa")
SCRAPER_DEFAULT_COUNTRY = os.getenv("SCRAPER_DEFAULT_COUNTRY", "Global")
SCRAPER_SITES_JSON = os.getenv("SCRAPER_SITES_JSON", "")
SCRAPER_LINK_BASE_URL = os.getenv("SCRAPER_LINK_BASE_URL", "")

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "40"))
BACKEND_WAIT_SECONDS = int(os.getenv("BACKEND_WAIT_SECONDS", "20"))
BACKEND_MAX_WAIT_SECONDS = int(os.getenv("BACKEND_MAX_WAIT_SECONDS", "300"))


@dataclass(frozen=True)
class ScraperSpec:
    kind: str
    name: str
    url: str | None = None
    source_name: str | None = None
    default_country: str = "Global"
    link_base_url: str | None = None


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


ADAPTER_REGISTRY: dict[str, type[BaseScraper]] = {
    "alpha": AlphaScholarshipScraper,
    "article": AlphaScholarshipScraper,
    "beta": BetaScholarshipScraper,
    "list": BetaScholarshipScraper,
    "demo": DemoScholarshipScraper,
}


def parse_site_specs() -> list[ScraperSpec]:
    if SCRAPER_SITES_JSON.strip():
        try:
            raw_specs = json.loads(SCRAPER_SITES_JSON)
        except json.JSONDecodeError as exc:
            raise ValueError("SCRAPER_SITES_JSON tiene un JSON invalido") from exc

        if not isinstance(raw_specs, list):
            raise ValueError("SCRAPER_SITES_JSON debe ser una lista de sitios")

        specs: list[ScraperSpec] = []
        for index, item in enumerate(raw_specs, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"SCRAPER_SITES_JSON[{index}] debe ser un objeto")

            kind = str(item.get("kind") or item.get("type") or "alpha").strip().lower()
            name = str(item.get("name") or item.get("site_name") or f"site-{index}").strip()
            url = item.get("url")
            source_name = item.get("source_name")
            default_country = str(item.get("default_country") or "Global").strip() or "Global"
            link_base_url = item.get("link_base_url")

            specs.append(
                ScraperSpec(
                    kind=kind,
                    name=name,
                    url=str(url).strip() if url else None,
                    source_name=str(source_name).strip() if source_name else None,
                    default_country=default_country,
                    link_base_url=str(link_base_url).strip() if link_base_url else None,
                )
            )

        return specs

    specs: list[ScraperSpec] = []
    if SCRAPER_SOURCE_URL:
        specs.append(
            ScraperSpec(
                kind="alpha",
                name=SCRAPER_SOURCE_NAME,
                url=SCRAPER_SOURCE_URL,
                source_name=SCRAPER_SOURCE_NAME,
                default_country=SCRAPER_DEFAULT_COUNTRY,
                link_base_url=SCRAPER_LINK_BASE_URL.strip() or None,
            )
        )

    if not specs:
        specs.append(ScraperSpec(kind="demo", name="demo"))

    return specs


def build_scrapers() -> list[BaseScraper]:
    scrapers: list[BaseScraper] = []
    for spec in parse_site_specs():
        adapter_cls = ADAPTER_REGISTRY.get(spec.kind)
        if adapter_cls is None:
            logger.warning("Adapter desconocido '%s' para sitio '%s'; se omite", spec.kind, spec.name)
            continue

        if adapter_cls is DemoScholarshipScraper:
            scrapers.append(DemoScholarshipScraper())
            continue

        if not spec.url:
            logger.warning("Sitio '%s' no tiene url configurada; se omite", spec.name)
            continue

        scrapers.append(
            adapter_cls(
                source_url=spec.url,
                source_name=spec.source_name or spec.name,
                default_country=spec.default_country,
                request_timeout_seconds=REQUEST_TIMEOUT_SECONDS,
                link_base_url=spec.link_base_url,
            )
        )

    return scrapers


def deduplicate_scholarships(scholarships: list[ScholarshipPayload]) -> list[ScholarshipPayload]:
    seen_urls: set[str] = set()
    unique_items: list[ScholarshipPayload] = []
    for scholarship in scholarships:
        url = str(scholarship.url)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        unique_items.append(scholarship)
    return unique_items


def send_to_backend(final_api_url: str, scholarship: ScholarshipPayload) -> tuple[bool, str]:
    payload = scholarship.model_dump(mode="json")
    response = requests.post(final_api_url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)

    if response.status_code in (200, 201):
        logger.info("Beca enviada: %s", payload["title"])
        return True, "inserted"
    elif response.status_code == 409:
        logger.debug("Duplicada (omitida): %s", payload["url"])
        return False, "duplicate"
    else:
        logger.error("Error enviando beca (%s): %s", response.status_code, response.text)
        return False, "error"


def run_scraper() -> None:
    final_api_url = resolve_api_url(API_URL)
    if not final_api_url:
        logger.error("La variable API_URL no esta configurada")
        sys.exit(1)

    logger.info("Iniciando scraping hacia API: %s", final_api_url)

    if not wait_for_backend(final_api_url):
        sys.exit(1)

    try:
        scrapers = build_scrapers()
    except ValueError as exc:
        logger.error("Configuracion invalida de scrapers: %s", exc)
        sys.exit(1)

    if not scrapers:
        logger.error("No hay scrapers configurados")
        sys.exit(1)

    scholarships: list[ScholarshipPayload] = []
    for scraper in scrapers:
        try:
            scraped = scraper.scrape()
            logger.info("%s: items validos extraidos: %s", scraper.site_name, len(scraped))
            scholarships.extend(scraped)
        except (requests.RequestException, ValueError) as exc:
            logger.error("%s: no se pudo ejecutar el scraper: %s", scraper.site_name, exc)

    scholarships = deduplicate_scholarships(scholarships)
    logger.info("Total de becas validas tras deduplicar: %s", len(scholarships))

    inserted_count = 0
    duplicate_count = 0
    for scholarship in scholarships:
        try:
            success, status = send_to_backend(final_api_url, scholarship)
            if status == "inserted":
                inserted_count += 1
            elif status == "duplicate":
                duplicate_count += 1
        except requests.RequestException as exc:
            logger.error("Error de red al enviar beca %s: %s", scholarship.url, exc)

    logger.info("Resultado: %d nuevas inscripciones detectadas, %d duplicadas omitidas", inserted_count, duplicate_count)
    if inserted_count > 0:
        logger.warning("*** SE ABRIERON INSCRIPCIONES: %d becas nuevas detectadas ***", inserted_count)


if __name__ == "__main__":
    interval = SCRAPER_INTERVAL_SECONDS
    logger.info("Scraper iniciado. Se ejecutará cada %d segundos", interval)
    while True:
        try:
            run_scraper()
        except KeyboardInterrupt:
            logger.info("Scraper detenido por usuario")
            sys.exit(0)
        except Exception as exc:
            logger.error("Error no capturado en run_scraper: %s", exc)
        
        logger.info("Esperando %d segundos hasta proxima ejecucion...", interval)
        time.sleep(interval)