from .css import CssScholarshipScraper, CssSelectors


class BetaScholarshipScraper(CssScholarshipScraper):
    def __init__(
        self,
        source_url: str,
        source_name: str,
        default_country: str,
        request_timeout_seconds: int,
        link_base_url: str | None = None,
    ) -> None:
        super().__init__(
            site_name="beta",
            source_url=source_url,
            source_name=source_name,
            default_country=default_country,
            request_timeout_seconds=request_timeout_seconds,
            link_base_url=link_base_url,
            selectors=CssSelectors(
                item="li.scholarship-item, .result-card, .listing-item, .card",
                title="header h2, h3, .card-title, .listing-title",
                description=".content p, .excerpt, .summary, .card-description",
                provider=".issuer, .organization, .card-provider",
                country=".region, .country, .location",
                deadline="time, .ends-at, .deadline, .card-deadline",
                tags=".chips span, .labels .tag, .category, .card-tags .tag",
            ),
        )