from decimal import Decimal


def test_weighted_gpa_formula() -> None:
    weighted = Decimal("18") * 3 + Decimal("16") * 2
    assert (weighted / 5).quantize(Decimal("0.01")) == Decimal("17.20")
