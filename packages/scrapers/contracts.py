from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScrapedListing:
    source_name: str
    title: str
    description: str = ""
    address: str = ""
    price: str = ""
    area: str = ""
    condominium: str = ""
    contact: str = ""
    phone: str = ""
    source_url: str = ""
    captured_at: str = ""
    payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ScraperResult:
    source_name: str
    listings: list[ScrapedListing]
    evidence_path: str = ""

    @property
    def raw_count(self) -> int:
        return len(self.listings)
