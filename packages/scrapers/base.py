from abc import ABC, abstractmethod

from packages.scrapers.contracts import ScraperResult


class BaseScraper(ABC):
    source_name = "base"

    @abstractmethod
    def collect_from_html(self, html: str, evidence_path: str = "") -> ScraperResult:
        """Parse stored HTML evidence without opening a browser or requesting a portal."""
