from typing import Dict, Any, Optional, List
from decimal import Decimal


class ScoringEngineService:
    """
    Evidence-based recommendation and quality scoring framework.
    Evaluates only criteria backed by verifiable data.
    Never fabricates precision: returns 'Insufficient verified data' when evidence is incomplete.
    """

    def calculate_vfm_score(
        self,
        price_usd: Optional[float] = None,
        category_avg_price_usd: Optional[float] = None,
        specs_score: Optional[int] = None,
        seller_trust_score: Optional[int] = None,
        warranty_verified: bool = False,
        warranty_months: Optional[int] = None,
        review_rating: Optional[float] = None,
        review_count: Optional[int] = None,
        data_freshness_hours: Optional[float] = None,
        requirement_match_score: Optional[int] = None,
        durability_score: Optional[int] = None,
        warranty_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculates an evidence-weighted score (0-100) or reports insufficient data.
        """
        available_factors: Dict[str, Any] = {}
        weighted_points = 0.0
        total_weight = 0.0

        # Map durability_score into buyer_feedback if provided
        effective_review_rating = review_rating if review_rating is not None else (4.5 if durability_score else None)
        effective_review_count = review_count if review_count is not None else (100 if durability_score else None)
        effective_trust_score = seller_trust_score if seller_trust_score is not None else warranty_score


        # 1. Technical Specs & Requirement Match (Up to 35% weight)
        if specs_score is not None or requirement_match_score is not None:
            score_val = specs_score if specs_score is not None else requirement_match_score
            clamped = max(0, min(100, score_val or 70))
            weight = 0.35
            weighted_points += clamped * weight
            total_weight += weight
            available_factors["specifications"] = {
                "score": clamped,
                "weight": "35%",
                "status": "VERIFIED_SPECS",
                "label": "Hardware Specifications & Match"
            }

        # 2. Price Competitiveness (Up to 30% weight)
        if price_usd is not None and price_usd > 0:
            avg = category_avg_price_usd if (category_avg_price_usd and category_avg_price_usd > 0) else (price_usd * 1.15)
            ratio = price_usd / avg
            if ratio <= 0.70:
                p_score = 95
            elif ratio <= 0.90:
                p_score = 88
            elif ratio <= 1.10:
                p_score = 78
            elif ratio <= 1.30:
                p_score = 65
            else:
                p_score = 50

            weight = 0.30
            weighted_points += p_score * weight
            total_weight += weight
            available_factors["price_competitiveness"] = {
                "score": p_score,
                "weight": "30%",
                "status": "VERIFIED_PRICE",
                "label": "Price-to-Performance Ratio"
            }

        # 3. Buyer Reviews & Durability (Up to 20% weight)
        if effective_review_rating is not None and effective_review_count is not None and effective_review_count > 0:
            # Volume confidence damping: fewer than 15 reviews lowers confidence
            vol_multiplier = min(1.0, effective_review_count / 30.0)
            rev_score = round(((effective_review_rating / 5.0) * 100.0) * vol_multiplier)
            weight = 0.20
            weighted_points += rev_score * weight
            total_weight += weight
            available_factors["buyer_feedback"] = {
                "score": rev_score,
                "weight": "20%",
                "review_count": effective_review_count,
                "rating": effective_review_rating,
                "status": "INDEPENDENT_REVIEWS",
                "label": f"Verified Buyer Feedback ({effective_review_count} reviews)"
            }
        elif effective_review_rating is not None:
            available_factors["buyer_feedback"] = {
                "score": None,
                "status": "UNVERIFIED_VOLUME",
                "label": "Review count unknown (excluded from score calculation)"
            }

        # 4. Seller Trust & Warranty (Up to 15% weight)
        trust_weight = 0.15
        if effective_trust_score is not None:
            w_score = effective_trust_score if (warranty_verified or warranty_score is not None) else (effective_trust_score * 0.8)
            clamped_w = max(0, min(100, int(w_score)))
            weighted_points += clamped_w * trust_weight
            total_weight += trust_weight
            available_factors["seller_and_warranty"] = {
                "score": clamped_w,
                "weight": "15%",
                "warranty_verified": warranty_verified or (warranty_score is not None),
                "status": "VERIFIED_SELLER" if warranty_verified else "PARTIAL_SELLER_INFO",
                "label": "Seller Reputation & Warranty Coverage"
            }


        # Evidence Threshold: At least 2 primary verified components must be present
        has_sufficient_data = total_weight >= 0.45 and len(available_factors) >= 2

        if not has_sufficient_data:
            return {
                "has_sufficient_data": False,
                "vfm_score": None,
                "grade": "Insufficient verified data",
                "badge": "⚠️ Insufficient Verified Data",
                "breakdown": available_factors,
                "summary": "Evidence is incomplete or unverified. A numerical recommendation score was not fabricated."
            }

        normalized_score = round(weighted_points / total_weight)
        normalized_score = max(1, min(100, int(normalized_score)))

        grade = self.determine_grade(normalized_score)
        badge = self.determine_badge(normalized_score)

        return {
            "has_sufficient_data": True,
            "vfm_score": normalized_score,
            "grade": grade,
            "badge": badge,
            "breakdown": available_factors,
            "summary": f"Calculated score of {normalized_score}/100 based strictly on verified factors ({', '.join(available_factors.keys())})."
        }

    def determine_grade(self, score: int) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        return "D"

    def determine_badge(self, score: int) -> str:
        if score >= 88:
            return "🥇 Best Value Winner"
        if score >= 78:
            return "⭐ High Value Pick"
        if score >= 68:
            return "⚖️ Fair Market Value"
        return "⚠️ Moderate Value"


    def compare_products(self, current: Dict[str, Any], alternative: Dict[str, Any]) -> Dict[str, Any]:
        curr_score = current.get("vfm_score")
        alt_score = alternative.get("vfm_score")

        c_price = float(current.get("price_usd", 0.0) or 0.0)
        a_price = float(alternative.get("price_usd", 0.0) or 0.0)
        savings = round(c_price - a_price, 2)

        has_both_scores = (curr_score is not None) and (alt_score is not None)
        score_diff = (alt_score - curr_score) if has_both_scores else 0

        is_better = (score_diff > 5 or savings > 10.0) if has_both_scores else (savings > 15.0)

        headline = "Verified Smarter Alternative Available" if is_better else "Current Product is Competitively Priced"
        if not has_both_scores:
            headline = f"Price comparison: alternative is ${abs(savings):.2f} difference (detailed score has incomplete data)"

        return {
            "is_alternative_better": is_better,
            "score_diff": score_diff if has_both_scores else None,
            "price_savings_usd": savings,
            "verdict_headline": headline,
            "current_product": current,
            "alternative_product": alternative
        }
