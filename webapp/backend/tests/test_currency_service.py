import pytest
from decimal import Decimal
from app.services.currency_service import CurrencyService


def test_currency_service_decimal_precision():
    service = CurrencyService()
    rec = service.build_price_record(
        listed_price="129.99",
        shipping_cost="15.50",
        taxes_and_fees="5.25",
        currency="USD",
        source_name="Direct Partner",
        is_verified=True
    )
    assert isinstance(rec.listed_price, Decimal)
    assert rec.listed_price == Decimal("129.99")
    assert rec.shipping_cost == Decimal("15.50")
    assert rec.total_estimated_cost == Decimal("150.74")
    assert rec.formatted_usd == "$129.99"


def test_currency_service_exchange_rate_provenance():
    service = CurrencyService()
    rate = service.get_usd_to_egp_rate()
    assert rate.from_currency == "USD"
    assert rate.to_currency == "EGP"
    assert isinstance(rate.rate, Decimal)
    assert rate.rate > 0
    assert rate.source is not None
    assert rate.timestamp is not None


def test_currency_service_used_condition_flag():
    service = CurrencyService()
    rec = service.build_price_record(
        listed_price="250.00",
        condition="used",
        source_name="Refurb Hub",
        is_verified=True
    )
    assert rec.condition == "used"
    assert "[Used]" in rec.dual_currency_display


def test_currency_service_unverified_price_handling():
    service = CurrencyService()
    rec = service.build_price_record(
        listed_price=None,
        is_verified=False
    )
    assert rec.is_verified is False
    assert rec.listed_price is None
    assert "Unavailable" in rec.dual_currency_display
