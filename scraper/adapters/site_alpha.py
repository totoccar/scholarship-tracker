from .css import CssScholarshipScraper, CssSelectors


class AlphaScholarshipScraper(CssScholarshipScraper):
    def __init__(
        self,
        source_url: str,
        source_name: str,
        default_country: str,
        request_timeout_seconds: int,
        link_base_url: str | None = None,
    ) -> None:
        super().__init__(
            site_name="alpha",
            source_url=source_url,
            source_name=source_name,
            default_country=default_country,
            request_timeout_seconds=request_timeout_seconds,
            link_base_url=link_base_url,
            selectors=CssSelectors(
                item="article, .scholarship-card, .scholarship-item, .opportunity",
                title="h2, h3, .title",
                description="p, .description, .summary",
                provider=".provider, .organization, .institution",
                country=".country, .location",
                deadline="time, .deadline, .closing-date",
                tags=".tag, .tags span, .badge",
            ),
        )