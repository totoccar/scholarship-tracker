from base import BaseScraper

from models import ScholarshipPayload


class DemoScholarshipScraper(BaseScraper):
    def __init__(self, source_name: str = "Comunidad Tech", default_country: str = "Global") -> None:
        super().__init__(
            site_name="demo",
            source_url=None,
            source_name=source_name,
            default_country=default_country,
            request_timeout_seconds=0,
        )

    def extract_raw_items(self, html: str) -> list[dict]:
        return []

    def scrape(self) -> list[ScholarshipPayload]:
        return self.validate_scholarships(
            [
                {
                    "title": "Beca de Excelencia Python Cloud",
                    "description": "Beca para especialistas en automatizacion y desarrollo cloud.",
                    "provider": self.source_name,
                    "country": self.default_country,
                    "deadline": "2026-12-31",
                    "url": "https://python-cloud-example.com/beca-1",
                    "tags": ["Python", "Cloud", "Remote"],
                }
            ]
        )