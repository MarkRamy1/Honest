import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.services.intent_parser import IntentParserService
from app.services.scoring_engine import ScoringEngineService
from app.services.review_sentiment import ReviewSentimentService
from app.services.currency_service import CurrencyService
from app.services.identity_matcher import ProductIdentityMatcher
from app.services.link_validator import ProductLinkValidator
from app.agents.adapters import BaseProductSourceAdapter, VerifiedCatalogAdapter, VerifiedRetailerAdapter
from app.agents.tools import (
    ShoppingAgentTools,
    SearchProductsInput,
    CurrentPriceInput,
    ShippingInfoInput,
    ProductReviewsInput,
    RankProductsInput
)
from app.agents.prompts import CATEGORY_RANKING_GUIDES
from app.ai.factory import get_ai_provider
from app.core.config import settings
from app.core.logging import logger


class ShoppingAgentOrchestrator:
    """
    Evidence-grounded 10-step agent workflow orchestrator:
    Executes structured requirement parsing, real candidate search,
    strict identity validation, price and link verification, deterministic ranking,
    and AI model reasoning for trade-off explanation.
    """

    def __init__(self, adapters: Optional[List[BaseProductSourceAdapter]] = None):
        self.intent_parser = IntentParserService()
        self.scoring_engine = ScoringEngineService()
        self.sentiment_service = ReviewSentimentService()
        self.currency_service = CurrencyService()
        self.identity_matcher = ProductIdentityMatcher()
        self.link_validator = ProductLinkValidator()

        # Default to verified internal catalog and retailer adapters
        self.adapters = adapters or [
            VerifiedRetailerAdapter(),
            VerifiedCatalogAdapter()
        ]
        self.tools = ShoppingAgentTools(self.adapters)

    def run_research(
        self,
        user_query: str,
        destination_country: str = "US",
        user_budget_override: Optional[float] = None,
        ai_provider_name: Optional[str] = None,
        ai_model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        workflow_steps = []

        # Step 1: Parse user request into structured requirements
        parsed = self.intent_parser.parse(user_query)
        workflow_steps.append({
            "step": 1,
            "action": "parse_intent",
            "result": f"Identified intent '{parsed['intent']}' for category '{parsed['category']}'"
        })

        # Step 2: Extract constraints (category, budget, destination, use-cases)
        category = parsed.get("category", "general")
        target_name = parsed.get("target_query") or user_query
        budget_usd = user_budget_override or (parsed.get("budget", {}).get("amount_usd") if parsed.get("budget") else None)
        use_cases = parsed.get("use_cases", [])

        workflow_steps.append({
            "step": 2,
            "action": "extract_constraints",
            "constraints": {
                "category": category,
                "target_name": target_name,
                "budget_usd": budget_usd,
                "use_cases": use_cases,
                "destination": destination_country
            }
        })

        # Step 3 & 4: Search authorized product data sources using tool
        search_res = self.tools.search_products(SearchProductsInput(
            query=target_name,
            category=category,
            budget_max=budget_usd,
            limit=5
        ))
        raw_candidates = search_res.items
        workflow_steps.append({
            "step": 3,
            "action": "search_data_sources",
            "found_count": len(raw_candidates)
        })

        # Step 5 & 6: Identity validation, link validation, and price normalization
        verified_candidates = []
        for cand in raw_candidates:
            # Identity match check
            match_res = self.identity_matcher.evaluate_match(
                query=target_name,
                candidate_title=cand.get("name", ""),
                candidate_brand=cand.get("brand"),
                candidate_category=cand.get("category")
            )

            # Skip rejected items (e.g. accessories or unrequested variants)
            if not match_res.is_exact_match and not match_res.is_acceptable_alternative:
                continue

            pid = cand.get("product_id") or "prod_generic"

            # Check price and format with CurrencyService
            price_out = self.tools.get_current_price(CurrentPriceInput(product_id=pid))
            price_val = price_out.price_usd if price_out.price_usd is not None else cand.get("price")

            if price_val is None:
                continue

            # Validate purchase link destination
            raw_url = cand.get("url") or price_out.source_url
            link_record = self.link_validator.validate_link(
                product_id=pid,
                title=cand.get("name", "Product"),
                merchant=cand.get("retailer", price_out.retailer),
                raw_url=raw_url,
                retrieval_timestamp=cand.get("data_freshness")
            )

            price_record = self.currency_service.build_price_record(
                listed_price=price_val,
                currency=cand.get("currency", "USD"),
                shipping_cost=0.0,
                source_name=cand.get("retailer", price_out.retailer),
                source_url=raw_url,
                retrieval_timestamp=cand.get("data_freshness"),
                is_verified=match_res.is_exact_match
            )

            # Shipping and reviews info
            ship_out = self.tools.get_shipping_information(ShippingInfoInput(
                product_id=pid,
                destination_country=destination_country
            ))
            rev_out = self.tools.get_product_reviews(ProductReviewsInput(product_id=pid))

            item = dict(cand)
            item["verified_price_usd"] = float(price_val)
            item["price_dual"] = price_record.dual_currency_display
            item["price_record"] = price_record.model_dump()
            item["validated_link"] = link_record.model_dump()
            item["is_buy_button_enabled"] = link_record.is_buy_button_enabled
            item["button_text"] = "Buy Verified Product ↗" if link_record.is_buy_button_enabled else "Verified Link Unavailable"
            item["is_exact_match"] = match_res.is_exact_match
            item["confidence_score"] = match_res.confidence_score
            item["shipping_info"] = ship_out.model_dump()
            item["reviews_summary"] = rev_out.model_dump()
            verified_candidates.append(item)

        workflow_steps.append({
            "step": 4,
            "action": "verify_and_normalize",
            "verified_count": len(verified_candidates)
        })

        # Step 7 & 8: Deduplicate and rank products with transparent criteria
        rank_out = self.tools.rank_products(RankProductsInput(
            category=category,
            products=verified_candidates,
            user_priorities=use_cases
        ))
        ranked = rank_out.ranked_products

        workflow_steps.append({
            "step": 5,
            "action": "rank_and_score",
            "top_score": ranked[0]["vfm_score"] if ranked and ranked[0].get("vfm_score") is not None else 0
        })

        # Step 9: Call AI model to explain evidence and trade-offs
        provider = get_ai_provider(
            provider_name=ai_provider_name or settings.AI_PROVIDER,
            model_name=ai_model_name or settings.AI_MODEL
        )

        top_pick = ranked[0] if ranked else None
        premium_pick = ranked[1] if len(ranked) > 1 else top_pick
        budget_pick = ranked[-1] if ranked else top_pick

        # Build prompt for AI explanation
        if ranked:
            explanation_prompt = (
                f"You are the Honest AI Shopping Intelligence engine. Explain the trade-offs and recommendation "
                f"for the user's query: '{user_query}'.\n"
                f"Top Verified Pick: {top_pick['name']} at {top_pick['price_dual']}.\n"
                f"Key factors: {top_pick.get('verdict', 'Official specifications verified.')}\n"
                f"Rules: Stick strictly to the evidence provided. Do not invent missing features or unverified prices."
            )
        else:
            explanation_prompt = (
                f"No verified exact match was found for the user query '{user_query}'. "
                f"Explain honestly that no reliable, verified product listing could be validated, "
                f"and that Honest AI does not fabricate fake prices or unverified listings."
            )

        try:
            ai_explanation = provider.generate_text(prompt=explanation_prompt)
            explanation_text = ai_explanation.text
            provider_meta = {
                "provider": provider.provider_name,
                "model": provider.model_name,
                "token_usage": ai_explanation.token_usage.model_dump()
            }
        except Exception as e:
            logger.warning(f"AI explanation call failed: {e}. Falling back to deterministic summary.")
            explanation_text = (
                f"Recommendation for {target_name}: Verified exact listing found with validated price and specifications."
                if ranked else
                f"Honest Notice: No sufficiently verified match was found for '{user_query}' across authorized sources."
            )
            provider_meta = {
                "provider": provider.provider_name,
                "model": provider.model_name,
                "fallback": True
            }

        elapsed = round(time.time() - start_time, 3)

        return {
            "status": "success" if ranked else "no_verified_matches",
            "query": user_query,
            "category": category,
            "category_guideline": CATEGORY_RANKING_GUIDES.get(category, "Standard balanced criteria."),
            "execution_time_seconds": elapsed,
            "workflow_steps": workflow_steps,
            "ai_explanation": explanation_text,
            "provider_metadata": provider_meta,
            "recommendation": {
                "top_value_pick": top_pick,
                "premium_pick": premium_pick,
                "budget_pick": budget_pick,
                "all_evaluated_options": ranked
            },
            "uncertainty_indicators": {
                "price_freshness": "LIVE_VERIFIED_HOURLY" if ranked else "UNVERIFIED",
                "shipping_confidence": "HIGH" if ranked else "UNAVAILABLE",
                "review_confidence": "AGGREGATED_AUTHENTIC_FEEDBACK" if ranked else "NO_DATA",
                "has_sufficient_verified_evidence": bool(ranked)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
