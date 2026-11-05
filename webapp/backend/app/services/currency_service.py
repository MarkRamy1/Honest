from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings
from app.core.logging import logger


class ExchangeRateRecord(BaseModel):
    from_currency: str = "USD"
    to_currency: str = "EGP"
    rate: Decimal
    source: str
    timestamp: str
    is_live: bool
    status: str = "VERIFIED_RATE"


class PriceRecord(BaseModel):
    listed_price: Optional[Decimal] = None
    currency: str = "USD"
    shipping_cost: Optional[Decimal] = None
    taxes_and_fees: Optional[Decimal] = None
    total_estimated_cost: Optional[Decimal] = None
    original_reference_price: Optional[Decimal] = None
    condition: str = "new"  # "new", "used", "refurbished", "unknown"
    source_name: str
    source_url: str
    retrieval_timestamp: str
    is_verified: bool
    exchange_rate_applied: Optional[ExchangeRateRecord] = None
    formatted_usd: str = ""
    formatted_egp: str = ""
    dual_currency_display: str = ""


class CurrencyService:
    """
    Precision monetary and currency conversion engine using exact Decimals,
    verifiable exchange rate sources with timestamps, and honest unverified labeling.
    """

    def __init__(self):
        self._cached_rate: Optional[ExchangeRateRecord] = None
        self._last_fetch_time: float = 0.0

    def get_usd_to_egp_rate(self) -> ExchangeRateRecord:
        """
        Retrieves the verifiable exchange rate from configured API source or
        the verified benchmark fallback with full provenance.
        """
        now_ts = datetime.now(timezone.utc).isoformat()

        # If a live API endpoint is configured, try fetching live rate
        if settings.EXCHANGE_RATE_API_URL:
            try:
                with httpx.Client(timeout=4.0) as client:
                    resp = client.get(settings.EXCHANGE_RATE_API_URL)
                    if resp.status_code == 200:
                        data = resp.json()
                        rate_val = data.get("rates", {}).get("EGP") or data.get("rate")
                        if rate_val:
                            decimal_rate = Decimal(str(rate_val)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                            record = ExchangeRateRecord(
                                from_currency="USD",
                                to_currency="EGP",
                                rate=decimal_rate,
                                source="Live Verified Forex Feed",
                                timestamp=now_ts,
                                is_live=True,
                                status="LIVE_VERIFIED"
                            )
                            self._cached_rate = record
                            return record
            except Exception as e:
                logger.warning(f"Failed to fetch live exchange rate: {e}. Falling back to configured benchmark.")

        # Fallback to configured rate with honest provenance
        fallback_decimal = Decimal(str(settings.USD_TO_EGP_FALLBACK)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return ExchangeRateRecord(
            from_currency="USD",
            to_currency="EGP",
            rate=fallback_decimal,
            source="Configured Central Bank / Market Reference Rate",
            timestamp=now_ts,
            is_live=False,
            status="CONFIGURED_BENCHMARK"
        )

    def build_price_record(
        self,
        listed_price: Optional[Union[float, int, str, Decimal]],
        currency: str = "USD",
        shipping_cost: Optional[Union[float, int, str, Decimal]] = None,
        taxes_and_fees: Optional[Union[float, int, str, Decimal]] = None,
        original_reference_price: Optional[Union[float, int, str, Decimal]] = None,
        condition: str = "new",
        source_name: str = "Unknown",
        source_url: str = "#",
        retrieval_timestamp: Optional[str] = None,
        is_verified: bool = True
    ) -> PriceRecord:
        """Constructs a strictly typed, decimal-based price record with full cost breakdown."""
        ts = retrieval_timestamp or datetime.now(timezone.utc).isoformat()
        curr_clean = currency.upper().strip() if currency else "USD"

        # Decimal conversions
        p_dec: Optional[Decimal] = None
        if listed_price is not None:
            try:
                p_dec = Decimal(str(listed_price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except Exception:
                p_dec = None

        ship_dec: Optional[Decimal] = None
        if shipping_cost is not None:
            try:
                ship_dec = Decimal(str(shipping_cost)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except Exception:
                ship_dec = None

        tax_dec: Optional[Decimal] = None
        if taxes_and_fees is not None:
            try:
                tax_dec = Decimal(str(taxes_and_fees)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except Exception:
                tax_dec = None

        ref_dec: Optional[Decimal] = None
        if original_reference_price is not None:
            try:
                ref_dec = Decimal(str(original_reference_price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except Exception:
                ref_dec = None

        # Compute total estimated cost
        total_dec: Optional[Decimal] = None
        if p_dec is not None:
            total_dec = p_dec + (ship_dec or Decimal("0.00")) + (tax_dec or Decimal("0.00"))

        rate_record = self.get_usd_to_egp_rate()

        # Build formatted display strings
        if p_dec is None or not is_verified:
            f_usd = "Price Unavailable / Unverified"
            f_egp = "غير متوفر / غير مدقق"
            dual = "Price Unavailable / Unverified"
        else:
            if curr_clean == "USD":
                f_usd = f"${p_dec:.2f}"
                egp_converted = (p_dec * rate_record.rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                f_egp = f"~{egp_converted:,} EGP"
                dual = f"${p_dec:.2f} (~{egp_converted:,} EGP)"
            elif curr_clean == "EGP":
                f_egp = f"{p_dec:,.2f} EGP"
                usd_converted = (p_dec / rate_record.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                f_usd = f"${usd_converted:.2f}"
                dual = f"${usd_converted:.2f} (~{p_dec:,.0f} EGP)"
            else:
                f_usd = f"{p_dec:.2f} {curr_clean}"
                f_egp = ""
                dual = f"{p_dec:.2f} {curr_clean}"

        # If condition is not new, append clear notice
        clean_condition = condition.lower().strip()
        if clean_condition in ["used", "refurbished"]:
            dual += f" [{clean_condition.capitalize()}]"

        return PriceRecord(
            listed_price=p_dec,
            currency=curr_clean,
            shipping_cost=ship_dec,
            taxes_and_fees=tax_dec,
            total_estimated_cost=total_dec,
            original_reference_price=ref_dec,
            condition=clean_condition,
            source_name=source_name,
            source_url=source_url,
            retrieval_timestamp=ts,
            is_verified=is_verified and (p_dec is not None),
            exchange_rate_applied=rate_record,
            formatted_usd=f_usd,
            formatted_egp=f_egp,
            dual_currency_display=dual
        )
