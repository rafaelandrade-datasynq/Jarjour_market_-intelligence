import re
from decimal import Decimal, InvalidOperation


def parse_brl_money(value: str | None) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    lowered = text.lower()
    if "sob consulta" in lowered or "consulte" in lowered:
        return None

    cleaned = re.sub(r"[^\d,.-]", "", text)
    if not cleaned:
        return None

    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(".", "")

    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None
