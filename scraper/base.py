import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError

from models import ScholarshipPayload

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

TITLE_BLACKLIST = (
    "bases",
    "procedimiento",
    "ver mas",
    "ver más",
    "clic aqui",
    "clic aquí",
)

TAG_KEYWORDS = (
    ("inteligencia artificial", "IA"),
    ("artificial intelligence", "IA"),
    ("ia", "IA"),
    ("software", "Software"),
    ("cloud", "Cloud"),
    ("españa", "España"),
    ("espana", "España"),
    ("remoto", "Remoto"),
    ("remote", "Remoto"),
    ("python", "Python"),
    ("data science", "Data Science"),
    ("ciberseguridad", "Cybersecurity"),
    ("cybersecurity", "Cybersecurity"),
)


class BaseScraper(ABC):
    def __init__(
        self,
        site_name: str,
        source_url: str | None,
        source_name: str,
        default_country: str,
        request_timeout_seconds: int,
        link_base_url: str | None = None,
    ) -> None:
        self.site_name = site_name
        self.source_url = source_url.strip().rstrip("/") if source_url else None
        self.source_name = source_name
        self.default_country = default_country
        self.request_timeout_seconds = request_timeout_seconds
        self.link_base_url = link_base_url.strip().rstrip("/") if link_base_url else None

    def scrape(self) -> list[ScholarshipPayload]:
        html = self.fetch_html()
        raw_items = self.extract_raw_items(html)
        normalized_items = [self.normalize_raw_item(item) for item in raw_items]
        cleaned_items = [item for item in normalized_items if item is not None]
        return self.validate_scholarships(cleaned_items)

    def fetch_html(self) -> str:
        if not self.source_url:
            raise ValueError(f"{self.site_name} requires a source_url")

        return self.fetch_html_at_url(self.source_url)

    def fetch_html_at_url(self, target_url: str) -> str:
        if target_url.startswith("file://"):
            local_path = Path(target_url.replace("file://", "", 1)).expanduser()
            return local_path.read_text(encoding="utf-8")

        if target_url.startswith("/"):
            local_path = Path(target_url).expanduser()
            if local_path.exists():
                return local_path.read_text(encoding="utf-8")

        try:
            response = requests.get(target_url, timeout=self.request_timeout_seconds, headers=REQUEST_HEADERS)
        except requests.exceptions.SSLError:
            host = (urlparse(target_url).hostname or "").lower()
            if host.endswith("auip.org"):
                logger.warning("%s: SSL invalido en %s; reintentando con verify=False", self.site_name, host)
                response = requests.get(
                    target_url,
                    timeout=self.request_timeout_seconds,
                    verify=False,
                    headers=REQUEST_HEADERS,
                )
            else:
                raise

        response.raise_for_status()
        return response.text

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"\s+", " ", value).strip()

    def clean_title(self, title: str | None) -> str | None:
        normalized = self._normalize_text(title)
        lowered = normalized.lower()
        if len(normalized) < 10:
            return None
        if any(blocked in lowered for blocked in TITLE_BLACKLIST):
            return None
        return normalized

    def clean_tags(self, tags: list[str] | None, text: str = "") -> list[str]:
        normalized_tags: list[str] = []
        for tag in tags or []:
            cleaned = self._normalize_text(tag)
            if cleaned and cleaned not in normalized_tags and len(cleaned) <= 50:
                normalized_tags.append(cleaned)

        lowered = text.lower()
        for keyword, tag in TAG_KEYWORDS:
            if keyword in lowered and tag not in normalized_tags:
                normalized_tags.append(tag)

        return normalized_tags[:15]

    @staticmethod
    def extract_first_paragraph(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for paragraph in soup.select("main p, article p, .content p, .description p, p"):
            text = paragraph.get_text(" ", strip=True)
            lowered = text.lower()
            if len(text) < 40:
                continue
            if any(marker in lowered for marker in ("cookie", "newsletter", "síguenos", "follow us", "menú")):
                continue
            return re.sub(r"\s+", " ", text).strip()
        return ""

    def normalize_raw_item(self, item: dict) -> dict | None:
        normalized = dict(item)
        title = self.clean_title(normalized.get("title"))
        if not title:
            logger.debug("%s: titulo descartado por limpieza: %s", self.site_name, normalized.get("title"))
            return None

        normalized["title"] = title
        normalized["description"] = self._normalize_text(normalized.get("description"))
        normalized["tags"] = self.clean_tags(normalized.get("tags"), f"{normalized['title']} {normalized.get('description', '')}")
        return normalized

    @abstractmethod
    def extract_raw_items(self, html: str) -> list[dict]:
        raise NotImplementedError

    def validate_scholarships(self, raw_items: list[dict]) -> list[ScholarshipPayload]:
        validated: list[ScholarshipPayload] = []
        for item in raw_items:
            try:
                validated.append(ScholarshipPayload(**item))
            except ValidationError as exc:
                logger.warning("%s: item descartado por validacion: %s", self.site_name, exc.errors())
        return validated