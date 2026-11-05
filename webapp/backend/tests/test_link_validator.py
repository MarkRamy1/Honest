import pytest
from app.services.link_validator import ProductLinkValidator


def test_link_validator_marketplace_pdps():
    validator = ProductLinkValidator()

    # Amazon PDP
    amazon_res = validator.validate_link(
        product_id="prod_amz",
        title="Sony Headphones",
        merchant="Amazon",
        raw_url="https://www.amazon.com/dp/B09XS7JWHH"
    )
    assert amazon_res.is_buy_button_enabled is True
    assert amazon_res.verification_status == "VERIFIED_DIRECT_LISTING"
    assert amazon_res.verified_product_identifier == "B09XS7JWHH"

    # AliExpress PDP
    ali_res = validator.validate_link(
        product_id="prod_ali",
        title="Choice Item",
        merchant="AliExpress",
        raw_url="https://www.aliexpress.com/item/1005006283918234.html"
    )
    assert ali_res.is_buy_button_enabled is True
    assert ali_res.verification_status == "VERIFIED_DIRECT_LISTING"
    assert ali_res.verified_product_identifier == "1005006283918234"

    # Chrono24 PDP
    chrono_res = validator.validate_link(
        product_id="prod_chrono",
        title="Rolex Submariner",
        merchant="Chrono24",
        raw_url="https://www.chrono24.com/rolex/submariner-date--mod45.htm"
    )
    assert chrono_res.is_buy_button_enabled is True
    assert chrono_res.verification_status == "VERIFIED_DIRECT_LISTING"


def test_link_validator_rejects_search_and_aggregator_pages():
    validator = ProductLinkValidator()

    # Amazon search page
    amz_search = validator.validate_link("1", "Item", "Amazon", "https://www.amazon.com/s?k=laptop+gaming")
    assert amz_search.is_buy_button_enabled is False
    assert amz_search.verification_status == "SEARCH_PAGE_ONLY"
    assert amz_search.is_search_page is True

    # AliExpress search page
    ali_search = validator.validate_link("2", "Item", "AliExpress", "https://www.aliexpress.com/wholesale?SearchText=phone")
    assert ali_search.is_buy_button_enabled is False
    assert ali_search.is_search_page is True

    # Google general search
    google_search = validator.validate_link("3", "Item", "Google", "https://www.google.com/search?q=best+headphones")
    assert google_search.is_buy_button_enabled is False
    assert google_search.is_search_page is True

    # Generic store homepage
    homepage = validator.validate_link("4", "Item", "Store", "https://www.bestbuy.com/")
    assert homepage.is_buy_button_enabled is False
    assert "homepage" in homepage.disabled_reason.lower()


def test_link_validator_safe_schemes():
    validator = ProductLinkValidator()

    assert validator.is_safe_url("https://www.amazon.com/dp/B09XS7JWHH") is True
    assert validator.is_safe_url("http://localhost:8000/product/1") is True
    assert validator.is_safe_url("javascript:void(0)") is False
    assert validator.is_safe_url("data:text/html;base64,PHNjcmlwdD4=") is False
    assert validator.is_safe_url("file:///etc/passwd") is False
    assert validator.is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    assert validator.is_safe_url("#") is False
    assert validator.is_safe_url("") is False
