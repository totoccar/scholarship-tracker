from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from base import BaseScraper
from models import normalize_deadline


@dataclass(frozen=True)
class CssSelectors:
    item: str
    title: str
    description: str
    provider: str | None = None
    country: str | None = None
    deadline: str | None = None
    tags: str | None = None
    link: str = "a[href]"


class CssScholarshipScraper(BaseScraper):
    def __init__(
        self,
        site_name: str,
        source_url: str,
        source_name: str,
        default_country: str,
        request_timeout_seconds: int,
        link_base_url: str | None,
        selectors: CssSelectors,
    ) -> None:
        super().__init__(
            site_name,
            source_url,
            source_name,
            default_country,
            request_timeout_seconds,
            link_base_url=link_base_url,
        )
        self.selectors = selectors

    def _resolve_link(self, href: str) -> str:
        if href.startswith("http://") or href.startswith("https://"):
            return href
        if self.link_base_url:
            return urljoin(f"{self.link_base_url}/", href)
        return urljoin(f"{self.source_url}/", href)

    @staticmethod
    def _text(node, default: str) -> str:
        if node is None:
            return default
        return node.get_text(strip=True) or default

    def extract_raw_items(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        candidates = soup.select(self.selectors.item)

        raw_items: list[dict] = []
        for card in candidates[:50]:
            link_node = card.select_one(self.selectors.link)
            href = link_node.get("href", "").strip() if link_node else ""
            if not href:
                continue

            raw_deadline = ""
            if self.selectors.deadline:
                deadline_node = card.select_one(self.selectors.deadline)
                if deadline_node is not None:
                    raw_deadline = deadline_node.get("datetime", "").strip() or deadline_node.get_text(strip=True)

            tag_nodes = card.select(self.selectors.tags) if self.selectors.tags else []

            raw_items.append(
                {
                    "title": self._text(card.select_one(self.selectors.title), "Beca sin titulo"),
                    "description": self._text(card.select_one(self.selectors.description), "Sin descripcion disponible"),
                    "provider": self._text(card.select_one(self.selectors.provider), self.source_name),
                    "country": self._text(card.select_one(self.selectors.country), self.default_country),
                    "deadline": normalize_deadline(raw_deadline),
                    "url": self._resolve_link(href),
                    "tags": [node.get_text(strip=True) for node in tag_nodes],
                }
            )

        return raw_items