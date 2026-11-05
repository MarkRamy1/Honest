from app.services.intent_parser import IntentParserService
from app.services.scoring_engine import ScoringEngineService
from app.services.review_sentiment import ReviewSentimentService


def test_intent_parser():
    parser = IntentParserService()

    # Query 1: Open-ended recommendation with budget in USD
    p1 = parser.parse("I want to buy the best laptop for video editing under $1000")
    assert p1["intent"] == "recommendation"
    assert p1["category"] == "laptops"
    assert p1["budget"]["amount_usd"] == 1000.0
    assert p1["budget"]["amount_egp"] == 50000.0
    assert "creative" in p1["use_cases"]

    # Query 2: Product audit for Rolex
    p2 = parser.parse("Rolex Submariner Date 126610LN")
    assert p2["intent"] == "product_audit"
    assert "Rolex Submariner" in p2["target_query"]

    # Query 3: Greeting
    p3 = parser.parse("Hello, how are you?")
    assert p3["intent"] == "greeting"


def test_scoring_engine():
    scoring = ScoringEngineService()
    vfm = scoring.calculate_vfm_score(
        price_usd=328.00,
        category_avg_price_usd=399.99,
        specs_score=96,
        durability_score=92,
        warranty_score=90,
        review_rating=4.8
    )
    assert vfm["vfm_score"] >= 85
    assert vfm["grade"] in ["A+", "A"]
    assert "Winner" in vfm["badge"] or "Pick" in vfm["badge"]


def test_review_sentiment():
    sentiment = ReviewSentimentService()
    rev = sentiment.analyze_product_reviews("Sony WH-1000XM5", "headphones")
    assert rev["durability_score"] >= 90
    assert "Noise cancellation" in rev["verified_pros"][0]
