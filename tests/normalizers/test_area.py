from decimal import Decimal

from packages.normalizers.area import parse_area_m2


def test_parse_area_m2_examples():
    assert parse_area_m2("45 m²") == Decimal("45")
    assert parse_area_m2("120m2") == Decimal("120")
    assert parse_area_m2("80,5 m²") == Decimal("80.5")
    assert parse_area_m2("") is None
    assert parse_area_m2(None) is None
