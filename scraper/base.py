import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from pydantic import ValidationError

from models import ScholarshipPayload

logger = logging.getLogger(__name__)


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
        return self.validate_scholarships(raw_items)

    def fetch_html(self) -> str:
        if not self.source_url:
            raise ValueError(f"{self.site_name} requires a source_url")

        if self.source_url.startswith("file://"):
            local_path = Path(self.source_url.replace("file://", "", 1)).expanduser()
            return local_path.read_text(encoding="utf-8")

        if self.source_url.startswith("/"):
            local_path = Path(self.source_url).expanduser()
            if local_path.exists():
                return local_path.read_text(encoding="utf-8")

        response = requests.get(self.source_url, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.text

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