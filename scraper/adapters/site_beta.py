from .css import CssScholarshipScraper, CssSelectors, merge_selector_overrides


class BetaScholarshipScraper(CssScholarshipScraper):
    def __init__(
        self,
        source_url: str,
        source_name: str,
        default_country: str,
        request_timeout_seconds: int,
        link_base_url: str | None = None,
        selector_overrides: dict[str, str] | None = None,
    ) -> None:
        base_selectors = CssSelectors(
            item="li.scholarship-item, .result-card, .listing-item, .card",
            title="header h2, h3, .card-title, .listing-title",
            description=".content p, .excerpt, .summary, .card-description",
            provider=".issuer, .organization, .card-provider",
            country=".region, .country, .location",
            deadline="time, .ends-at, .deadline, .card-deadline",
            tags=".chips span, .labels .tag, .category, .card-tags .tag",
        )
        super().__init__(
            site_name="beta",
            source_url=source_url,
            source_name=source_name,
            default_country=default_country,
            request_timeout_seconds=request_timeout_seconds,
            link_base_url=link_base_url,
            selectors=merge_selector_overrides(base_selectors, selector_overrides),
        )