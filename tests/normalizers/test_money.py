from decimal import Decimal

from packages.normalizers.money import parse_brl_money


def test_parse_brl_money_examples():
    assert parse_brl_money("R$ 3.500,00") == Decimal("3500.00")
    assert parse_brl_money("R$ 12.000") == Decimal("12000.00")
    assert parse_brl_money("3.200") == Decimal("3200.00")
    assert parse_brl_money("Sob consulta") is None
    assert parse_brl_money("") is None
    assert parse_brl_money(None) is None
