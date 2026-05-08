import re
from decimal import Decimal, InvalidOperation


def parse_area_m2(value: str | None) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not match:
        return None

    try:
        parsed = Decimal(match.group(0).replace(",", "."))
    except (InvalidOperation, ValueError):
        return None
    return parsed.quantize(Decimal("0.01")).normalize()
