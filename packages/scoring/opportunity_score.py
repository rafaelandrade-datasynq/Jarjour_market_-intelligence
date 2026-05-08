from decimal import Decimal


def simple_opportunity_score(aluguel_m2: Decimal | None, market_average: Decimal | None) -> Decimal:
    if not aluguel_m2 or not market_average:
        return Decimal("0.00")
    discount = (market_average - aluguel_m2) / market_average
    return max(Decimal("0.00"), min(Decimal("100.00"), discount * Decimal("100")))
