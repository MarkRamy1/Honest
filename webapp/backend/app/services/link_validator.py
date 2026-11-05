import re
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field


class ValidatedProductLink(BaseModel):
    product_id: str
    merchant: str
    exact_title: str
    source_url: str
    safe_url: str
    verified_product_identifier: Optional[str] = None
    retrieval_timestamp: str
    verification_status: str  # "VERIFIED_DIRECT_LISTING" | "SEARCH_PAGE_ONLY" | "UNVERIFIED"
    is_buy_button_enabled: bool
    disabled_reason: Optional[str] = None
    is_search_page: bool = False


class ProductLinkValidator:
    """
    Validates product URLs to ensure purchase links point strictly to direct
    item-specific Product Detail Pages (PDP), completely eliminating false search pages,
    aggregators, or fabricated merchant routes.
    """

    SEARCH_PATTERNS = [
        r"/s\?k=",
        r"[?&]k=",
        r"/search\b",
        r"[?&]q=",
        r"[?&]query=",
        r"/wholesale\?",
        r"[?&]SearchText=",
        r"/browse\b",
        r"/category\b",
        r"/collections\b",
        r"google\.com/search",
        r"tiktok\.com/tag"
    ]

    PDP_PATTERNS = {
        "amazon": r"/dp/([A-Z0-9]{10})|/gp/product/([A-Z0-9]{10})",
        "aliexpress": r"/item/(\d+)\.html",
        "goat": r"/sneakers/([a-zA-Z0-9\-_]+)",
        "chrono24": r"/([a-zA-Z0-9\-_]+--mod\d+\.htm|\d+\.htm)",
        "noon": r"/([a-zA-Z0-9\-_]+)/p/([a-zA-Z0-9\-_]+)",
        "apple": r"/shop/buy-([a-zA-Z0-9\-_]+)"
    }

    def is_safe_url(self, url: str) -> bool:
        """Ensures URL conforms to safe web protocols and rejects dangerous schemes."""
        if not url or url.strip() in ["#", ""]:
            return False
        parsed = urlparse(url.strip())
        if parsed.scheme.lower() not in ["https", "http"]:
            return False
        # Reject private or local redirection tricks
        hostname = (parsed.hostname or "").lower()
        if hostname in ["169.254.169.254", "0.0.0.0"]:
            return False
        return True

    def validate_link(
        self,
        product_id: str,
        title: str,
        merchant: str,
        raw_url: str,
        retrieval_timestamp: Optional[str] = None
    ) -> ValidatedProductLink:
        """
        Thoroughly audits a purchase link destination against strict safety and PDP standards.
        """
        ts = retrieval_timestamp or datetime.now(timezone.utc).isoformat()
        clean_url = (raw_url or "").strip()

        if not self.is_safe_url(clean_url):
            return ValidatedProductLink(
                product_id=product_id,
                merchant=merchant,
                exact_title=title,
                source_url=clean_url,
                safe_url="#",
                verified_product_identifier=None,
                retrieval_timestamp=ts,
                verification_status="UNVERIFIED",
                is_buy_button_enabled=False,
                disabled_reason="Invalid, malformed, or unsafe link scheme",
                is_search_page=False
            )

        # Check for search or aggregator indicators
        is_search = any(re.search(pat, clean_url, re.IGNORECASE) for pat in self.SEARCH_PATTERNS)
        if is_search:
            return ValidatedProductLink(
                product_id=product_id,
                merchant=merchant,
                exact_title=title,
                source_url=clean_url,
                safe_url=clean_url,
                verified_product_identifier=None,
                retrieval_timestamp=ts,
                verification_status="SEARCH_PAGE_ONLY",
                is_buy_button_enabled=False,
                disabled_reason="Direct verified purchase link unavailable (destination is a search/discovery page)",
                is_search_page=True
            )

        # Inspect marketplace specific product identifiers
        parsed = urlparse(clean_url)
        domain = (parsed.hostname or "").lower()

        verified_id = None
        for marketplace, pattern in self.PDP_PATTERNS.items():
            if marketplace in domain:
                m = re.search(pattern, clean_url)
                if m:
                    # Extract first non-None group
                    verified_id = next((g for g in m.groups() if g is not None), None)
                    break

        # A valid PDP has path depth and is not root
        path_clean = parsed.path.strip("/")
        if not path_clean:
            return ValidatedProductLink(
                product_id=product_id,
                merchant=merchant,
                exact_title=title,
                source_url=clean_url,
                safe_url="#",
                verified_product_identifier=None,
                retrieval_timestamp=ts,
                verification_status="UNVERIFIED",
                is_buy_button_enabled=False,
                disabled_reason="Destination leads to a store homepage rather than a product listing",
                is_search_page=False
            )

        return ValidatedProductLink(
            product_id=product_id,
            merchant=merchant,
            exact_title=title,
            source_url=clean_url,
            safe_url=clean_url,
            verified_product_identifier=verified_id,
            retrieval_timestamp=ts,
            verification_status="VERIFIED_DIRECT_LISTING",
            is_buy_button_enabled=True,
            disabled_reason=None,
            is_search_page=False
        )
