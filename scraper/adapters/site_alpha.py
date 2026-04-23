from .css import CssScholarshipScraper, CssSelectors, merge_selector_overrides


class AlphaScholarshipScraper(CssScholarshipScraper):
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
            item="article, .scholarship-card, .scholarship-item, .opportunity",
            title="h2, h3, .title",
            description="p, .description, .summary",
            provider=".provider, .organization, .institution",
            country=".country, .location",
            deadline="time, .deadline, .closing-date",
            tags=".tag, .tags span, .badge",
        )
        super().__init__(
            site_name="alpha",
            source_url=source_url,
            source_name=source_name,
            default_country=default_country,
            request_timeout_seconds=request_timeout_seconds,
            link_base_url=link_base_url,
            selectors=merge_selector_overrides(base_selectors, selector_overrides),
        )