from dataclasses import dataclass
import logging
import re
from urllib.parse import urljoin
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from base import BaseScraper
from models import normalize_deadline

logger = logging.getLogger(__name__)


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


def merge_selector_overrides(base: CssSelectors, overrides: dict[str, str] | None) -> CssSelectors:
    if not overrides:
        return base

    allowed = {
        "item",
        "title",
        "description",
        "provider",
        "country",
        "deadline",
        "tags",
        "link",
    }
    sanitized = {key: value for key, value in overrides.items() if key in allowed and value}
    if not sanitized:
        return base

    return CssSelectors(**(base.__dict__ | sanitized))


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

    @staticmethod
    def _extract_benefits(text: str) -> str:
        patterns = [
            r"\b\d+[\.,]?\d*\s?(?:€|eur|euros?)\b",
            r"\b\d+[\.,]?\d*\s?(?:usd|d[oó]lares?|dollars?)\b",
            r"\b\d{1,3}\s?%\b",
            r"\b(full tuition|matr[ií]cula completa|dotaci[oó]n|stipend|allowance|ayuda econ[oó]mica|bolsa|grant|tuition waiver)\b",
        ]
        lowered = text.lower()
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, lowered, flags=re.IGNORECASE))
        if not matches:
            return ""
        normalized = []
        for match in matches:
            value = match if isinstance(match, str) else " ".join(match)
            value = value.strip()
            if value and value not in normalized:
                normalized.append(value)
        return ", ".join(normalized[:5])

    @staticmethod
    def _extract_deadline(card, selectors: CssSelectors) -> str:
        if selectors.deadline:
            deadline_node = card.select_one(selectors.deadline)
            if deadline_node is not None:
                datetime_value = deadline_node.get("datetime", "").strip()
                if datetime_value:
                    return datetime_value

                aria_label = deadline_node.get("aria-label", "").strip()
                if aria_label:
                    return aria_label

                deadline_text = deadline_node.get_text(" ", strip=True)
                if deadline_text:
                    return deadline_text

        card_text = card.get_text(" ", strip=True)
        text_patterns = [
            r"(?:cierre|deadline|hasta el|until|fecha limite|fecha límite)\s*[:\-]?\s*([A-Za-z0-9/\-\., ]{6,40})",
            r"(?:postula hasta|aplica hasta|inscripciones hasta)\s*[:\-]?\s*([A-Za-z0-9/\-\., ]{6,40})",
        ]
        for pattern in text_patterns:
            match = re.search(pattern, card_text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()

        time_node = card.select_one("time[datetime]") or card.select_one("time")
        if time_node is not None:
            return time_node.get("datetime", "").strip() or time_node.get_text(" ", strip=True)

        return ""

    @staticmethod
    def _infer_it_tags(text: str) -> list[str]:
        keyword_to_tag = {
            "python": "Python",
            "cloud": "Cloud",
            "devops": "DevOps",
            "machine learning": "Machine Learning",
            "inteligencia artificial": "AI",
            "artificial intelligence": "AI",
            "data science": "Data Science",
            "ciberseguridad": "Cybersecurity",
            "cybersecurity": "Cybersecurity",
            "hpc": "HPC",
            "computer vision": "Computer Vision",
            "ingenieria": "Engineering",
            "ingeniería": "Engineering",
            "informática": "Computer Science",
            "informatica": "Computer Science",
            "sistemas": "Systems",
            "masters": "Master",
            "master": "Master",
            "maestria": "Master",
            "maestría": "Master",
        }
        lowered = text.lower()
        tags = [tag for keyword, tag in keyword_to_tag.items() if keyword in lowered]
        unique: list[str] = []
        for tag in tags:
            if tag not in unique:
                unique.append(tag)
        return unique

    @staticmethod
    def _build_logo_url(target_url: str) -> str | None:
        host = (urlparse(target_url).hostname or "").strip().lower()
        if not host:
            return None
        if host.startswith("www."):
            host = host[4:]
        return f"https://logo.clearbit.com/{host}"

    def _deep_enrich_description(self, target_url: str, fallback_description: str) -> str:
        try:
            html = self.fetch_html_at_url(target_url)
        except Exception as exc:
            logger.debug("%s: no se pudo hacer deep scrape de %s: %s", self.site_name, target_url, exc)
            return fallback_description

        first_paragraph = self.extract_first_paragraph(html)
        return first_paragraph or fallback_description

    @staticmethod
    def _needs_deep_scrape(description: str) -> bool:
        normalized = description.strip().lower()
        if not normalized:
            return True
        if normalized.startswith("convocatoria detectada automaticamente"):
            return True
        if normalized.startswith("sin descripcion disponible"):
            return True
        return len(normalized) < 40

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

    @staticmethod
    def _is_relevant_link(text: str, href: str) -> bool:
        haystack = f"{text} {href}".lower()
        keywords = (
            "scholar",
            "scholarship",
            "fellowship",
            "grant",
            "funding",
            "financial",
            "aid",
            "beca",
            "convocatoria",
            "inscripcion",
            "postgrado",
            "posgrado",
            "master",
            "maestria",
            "movilidad",
        )
        return any(keyword in haystack for keyword in keywords)

    def _fallback_extract_from_links(self, soup: BeautifulSoup) -> list[dict]:
        raw_items: list[dict] = []
        seen_urls: set[str] = set()

        for link_node in soup.select("a[href]"):
            href = link_node.get("href", "").strip()
            text = link_node.get_text(strip=True)

            if not href or len(text) < 10:
                continue
            if not self._is_relevant_link(text, href):
                continue

            full_url = self._resolve_link(href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            raw_items.append(
                {
                    "title": text,
                    "description": f"Convocatoria detectada automaticamente en {self.source_name}.",
                    "provider": self.source_name,
                    "country": self.default_country,
                    "deadline": normalize_deadline(""),
                    "url": full_url,
                    "status": "PENDING",
                    "benefits": "",
                    "logoUrl": self._build_logo_url(full_url),
                    "tags": [self.site_name, "auto"],
                }
            )

            if len(raw_items) >= 25:
                break

        return raw_items

    def extract_raw_items(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        candidates = soup.select(self.selectors.item)

        if not candidates:
            return self._fallback_extract_from_links(soup)

        raw_items: list[dict] = []
        for card in candidates[:50]:
            link_node = card.select_one(self.selectors.link)
            href = link_node.get("href", "").strip() if link_node else ""
            if not href:
                continue

            raw_deadline = self._extract_deadline(card, self.selectors)

            tag_nodes = card.select(self.selectors.tags) if self.selectors.tags else []
            title = self._text(card.select_one(self.selectors.title), "Beca sin titulo")
            description = self._text(card.select_one(self.selectors.description), "Sin descripcion disponible")
            card_text = card.get_text(" ", strip=True)
            inferred_tags = self._infer_it_tags(f"{title} {description} {card_text}")
            explicit_tags = [node.get_text(strip=True) for node in tag_nodes]
            all_tags = [*explicit_tags, *inferred_tags]
            deduped_tags: list[str] = []
            for tag in all_tags:
                if tag and tag not in deduped_tags:
                    deduped_tags.append(tag)

            full_url = self._resolve_link(href)

            raw_items.append(
                {
                    "title": title,
                    "description": description,
                    "provider": self._text(card.select_one(self.selectors.provider), self.source_name),
                    "country": self._text(card.select_one(self.selectors.country), self.default_country),
                    "deadline": normalize_deadline(raw_deadline),
                    "url": full_url,
                    "status": "PENDING",
                    "benefits": self._extract_benefits(card_text),
                    "logoUrl": self._build_logo_url(full_url),
                    "tags": deduped_tags,
                }
            )

        if not raw_items:
            return self._fallback_extract_from_links(soup)

        return raw_items

    def normalize_raw_item(self, item: dict) -> dict | None:
        normalized = dict(item)
        url = str(normalized.get("url") or "").strip()
        fallback_description = str(normalized.get("description") or "").strip()
        if url and self._needs_deep_scrape(fallback_description):
            normalized["description"] = self._deep_enrich_description(url, fallback_description)

        normalized = super().normalize_raw_item(normalized)
        if normalized is None:
            return None

        normalized["tags"] = self.clean_tags(
            normalized.get("tags"),
            f"{normalized.get('title', '')} {normalized.get('description', '')}",
        )
        return normalized