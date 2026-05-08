from datetime import UTC, datetime
from html.parser import HTMLParser

from packages.scrapers.base import BaseScraper
from packages.scrapers.contracts import ScrapedListing, ScraperResult


class _DFImoveisHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._current: dict | None = None
        self._field: str | None = None
        self.listings: list[dict] = []

    def handle_starttag(self, tag: str, attrs):
        attr = dict(attrs)
        if tag == "article" and attr.get("data-listing") == "dfimoveis":
            self._current = {"source_url": attr.get("data-url", "")}
        if self._current is not None and "data-field" in attr:
            self._field = attr["data-field"]

    def handle_data(self, data: str):
        if self._current is None or self._field is None:
            return
        value = data.strip()
        if not value:
            return
        current = self._current.get(self._field, "")
        self._current[self._field] = f"{current} {value}".strip()

    def handle_endtag(self, tag: str):
        if tag == "article" and self._current is not None:
            self.listings.append(self._current)
            self._current = None
        if self._field is not None:
            self._field = None


class DFImoveisOfflineScraper(BaseScraper):
    source_name = "dfimoveis"

    def collect_from_html(self, html: str, evidence_path: str = "") -> ScraperResult:
        parser = _DFImoveisHTMLParser()
        parser.feed(html)
        captured_at = datetime.now(UTC).isoformat()
        listings = [
            ScrapedListing(
                source_name=self.source_name,
                title=item.get("title", ""),
                description=item.get("description", ""),
                address=item.get("address", ""),
                price=item.get("price", ""),
                area=item.get("area", ""),
                condominium=item.get("condominium", ""),
                contact=item.get("contact", ""),
                phone=item.get("phone", ""),
                source_url=item.get("source_url", ""),
                captured_at=captured_at,
                payload={
                    **item,
                    "offline_fixture": True,
                    "evidence_path": evidence_path,
                    "captured_at": captured_at,
                },
            )
            for item in parser.listings
        ]
        return ScraperResult(
            source_name=self.source_name,
            listings=listings,
            evidence_path=evidence_path,
        )
