import pytest
from app.services.identity_matcher import ProductIdentityMatcher
from app.services.link_validator import ProductLinkValidator
from app.services.currency_service import CurrencyService
from app.services.intent_parser import IntentParserService
from app.agents.orchestrator import ShoppingAgentOrchestrator
from app.services.product_search import ProductSearchService


def test_redmi13_intent_parsing():
    parser = IntentParserService()
    parsed = parser.parse("I want to buy a phone (Redmi 13)")
    assert parsed["category"] == "smartphones"
    assert "Redmi 13" in parsed["target_query"] or "redmi 13" in parsed["raw_query"].lower()


def test_redmi13_exact_identity_matching():
    matcher = ProductIdentityMatcher()
    target_query = "Redmi 13"

    # 1. Exact match test
    exact_title = "Xiaomi Redmi 13 (6GB RAM, 128GB Storage, 108MP Camera, Midnight Black)"
    res_exact = matcher.evaluate_match(target_query, exact_title, candidate_brand="Xiaomi")
    assert res_exact.is_exact_match is True
    assert res_exact.confidence_score >= 0.75
    assert res_exact.rejection_reason is None

    # 2. Incompatible model test: Redmi Note 13 (different model with AMOLED)
    note_title = "Xiaomi Redmi Note 13 4G (8GB RAM, 256GB Storage, 108MP AMOLED)"
    res_note = matcher.evaluate_match(target_query, note_title, candidate_brand="Xiaomi")
    assert res_note.is_exact_match is False
    assert "modifier(s) 'note'" in res_note.rejection_reason.lower()

    # 3. Incompatible model test: Redmi 13C (different budget tier)
    c_title = "Xiaomi Redmi 13C Dual SIM 128GB 4GB RAM"
    res_c = matcher.evaluate_match(target_query, c_title, candidate_brand="Xiaomi")
    assert res_c.is_exact_match is False
    assert "modifier(s) 'c'" in res_c.rejection_reason.lower()

    # 4. Accessory rejection: Phone case
    case_title = "Shockproof Silicone Case for Xiaomi Redmi 13 with Camera Protection"
    res_case = matcher.evaluate_match(target_query, case_title, candidate_brand="Xiaomi")
    assert res_case.is_exact_match is False
    assert res_case.is_accessory is True
    assert "accessory" in res_case.rejection_reason.lower()

    # 5. Accessory rejection: Tempered glass screen protector
    glass_title = "Tempered Glass Screen Protector for Redmi 13 (Pack of 3)"
    res_glass = matcher.evaluate_match(target_query, glass_title, candidate_brand="Xiaomi")
    assert res_glass.is_exact_match is False
    assert res_glass.is_accessory is True

    # 6. Accessory rejection: Replacement LCD screen
    screen_title = "Replacement LCD Display Touch Screen Digitizer for Redmi 13"
    res_screen = matcher.evaluate_match(target_query, screen_title, candidate_brand="Xiaomi")
    assert res_screen.is_exact_match is False
    assert res_screen.is_accessory is True


def test_redmi13_buy_button_validation():
    validator = ProductLinkValidator()

    # Direct verified Product Detail Page (PDP)
    valid_pdp = "https://www.amazon.com/dp/B0D5D8N5T9"
    res_pdp = validator.validate_link("p1", "Xiaomi Redmi 13", "Amazon Prime", valid_pdp)
    assert res_pdp.is_buy_button_enabled is True
    assert res_pdp.verification_status == "VERIFIED_DIRECT_LISTING"
    assert res_pdp.verified_product_identifier == "B0D5D8N5T9"

    # Search URL disguised as buy link must be rejected from direct buy
    search_url = "https://www.amazon.com/s?k=Redmi+13+phone"
    res_search = validator.validate_link("p2", "Xiaomi Redmi 13", "Amazon Prime", search_url)
    assert res_search.is_buy_button_enabled is False
    assert res_search.verification_status == "SEARCH_PAGE_ONLY"
    assert "search/discovery page" in res_search.disabled_reason

    # Google search URL must be rejected from buy button
    google_search = "https://www.google.com/search?q=Xiaomi+Redmi+13+price"
    res_google = validator.validate_link("p3", "Xiaomi Redmi 13", "Google", google_search)
    assert res_google.is_buy_button_enabled is False
    assert res_google.is_search_page is True

    # Unsafe javascript: scheme must be blocked
    unsafe_url = "javascript:alert('malicious')"
    res_unsafe = validator.validate_link("p4", "Xiaomi Redmi 13", "Malicious", unsafe_url)
    assert res_unsafe.is_buy_button_enabled is False
    assert res_unsafe.safe_url == "#"


def test_redmi13_price_and_currency_provenance():
    curr_service = CurrencyService()

    # Verified price with full provenance
    price_rec = curr_service.build_price_record(
        listed_price="139.99",
        currency="USD",
        source_name="Amazon Prime (Xiaomi Official)",
        source_url="https://www.amazon.com/dp/B0D5D8N5T9",
        is_verified=True
    )
    assert price_rec.is_verified is True
    assert price_rec.listed_price is not None
    assert price_rec.formatted_usd == "$139.99"
    assert "EGP" in price_rec.formatted_egp
    assert price_rec.exchange_rate_applied is not None
    assert price_rec.exchange_rate_applied.rate > 0
    assert price_rec.retrieval_timestamp is not None

    # Unverified price must not present fabricated numbers
    unverified_rec = curr_service.build_price_record(
        listed_price=None,
        currency="USD",
        is_verified=False
    )
    assert unverified_rec.is_verified is False
    assert unverified_rec.listed_price is None
    assert "Unavailable" in unverified_rec.formatted_usd


def test_redmi13_no_match_honest_reporting():
    search_service = ProductSearchService()

    # Querying for a completely fictional model must return an honest no-match result
    # rather than manufacturing fake $169 products or search URLs
    result = search_service.find_best_value_products(
        query="Xiaomi SuperPhone 99999 Impossible Model That Does Not Exist",
        category="smartphones"
    )
    assert result["has_verified_match"] is False
    assert result["top_pick"] is None
    assert len(result["all_contenders"]) == 0
    assert "No sufficiently verified exact product matches found" in result["message"]


def test_redmi13_full_orchestration_workflow(client):
    res = client.post("/api/agent/research", json={
        "query": "I want to buy a phone (Redmi 13)",
        "destination_country": "US",
        "ai_provider": "mock"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["category"] == "smartphones"

    top = data["recommendation"]["top_value_pick"]
    assert top is not None
    assert "Redmi 13" in top["name"]
    # Must NOT be an accessory
    assert "case" not in top["name"].lower()
    assert "glass" not in top["name"].lower()
    # Must have a verified PDP link
    assert top["validated_link"]["is_buy_button_enabled"] is True
    assert "/dp/" in top["validated_link"]["safe_url"]
    # Must have explicit currency and price
    assert top["verified_price_usd"] == 139.99
    assert "$" in top["price_dual"]
