import re
from typing import Dict, Any, List, Optional, Tuple, Set
from pydantic import BaseModel, Field


class IdentityMatchResult(BaseModel):
    is_exact_match: bool
    is_acceptable_alternative: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    rejection_reason: Optional[str] = None
    target_brand: Optional[str] = None
    target_model: Optional[str] = None
    detected_brand: Optional[str] = None
    detected_model: Optional[str] = None
    is_accessory: bool = False
    condition_match: bool = True
    variant_info: Dict[str, Any] = Field(default_factory=dict)


class ProductIdentityMatcher:
    """
    Deterministic identity matching engine enforcing exact model constraints,
    accessory elimination, variant segregation, and explicit rejection rules.
    """

    # Disallowed accessory keywords when searching for main devices/products
    ACCESSORY_KEYWORDS: Set[str] = {
        "case", "cover", "protector", "tempered glass", "screen protector",
        "film", "skin", "pouch", "sleeve", "bumper", "holster", "housing",
        "replacement screen", "lcd replacement", "battery replacement", "replacement",
        "digitizer", "touch screen", "lcd display", "display assembly",
        "charging cable", "charger", "adapter", "dock", "holder", "mount",
        "strap", "band", "lanyard", "ear tips", "cushions", "foam tips"
    }


    # Brand synonyms and normalizations
    BRAND_NORMALIZATION: Dict[str, str] = {
        "xiaomi": "Xiaomi",
        "redmi": "Xiaomi",
        "apple": "Apple",
        "sony": "Sony",
        "samsung": "Samsung",
        "nike": "Nike",
        "jordan": "Nike Jordan",
        "rolex": "Rolex",
        "lenovo": "Lenovo",
        "bose": "Bose",
        "anker": "Anker",
        "dyson": "Dyson"
    }

    # Sub-model modifiers that denote completely different hardware
    HARDWARE_MODIFIERS: Set[str] = {
        "note", "pro", "plus", "max", "ultra", "lite", "c", "se", "mini", "fe", "gt"
    }

    def check_is_accessory(self, candidate_title: str) -> Tuple[bool, Optional[str]]:
        """Returns True if the candidate listing represents an accessory rather than the primary device."""
        title_lower = candidate_title.lower()
        # Tokenize preserving spaces
        for keyword in self.ACCESSORY_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, title_lower):
                return True, f"Rejected as an accessory or spare part ('{keyword}')"
        return False, None

    def extract_brand_and_model(self, text: str) -> Tuple[Optional[str], Optional[str], Set[str]]:
        """Extracts candidate brand, base model name, and specific modifiers."""
        text_clean = re.sub(r"[?!,.:;\"()]+", " ", text.lower())
        raw_tokens = [t for t in text_clean.split() if t]
        tokens = []
        for t in raw_tokens:
            m = re.match(r"^(\d+)([a-zA-Z]+)$", t)
            if m:
                tokens.append(m.group(1))
                tokens.append(m.group(2))
            else:
                tokens.append(t)

        detected_brand = None
        for t in tokens:
            if t in self.BRAND_NORMALIZATION:
                detected_brand = self.BRAND_NORMALIZATION[t]
                break

        modifiers = set()
        for t in tokens:
            if t in self.HARDWARE_MODIFIERS:
                modifiers.add(t)

        return detected_brand, " ".join(tokens), modifiers

    def evaluate_match(
        self,
        query: str,
        candidate_title: str,
        candidate_brand: Optional[str] = None,
        candidate_category: Optional[str] = None,
        candidate_condition: str = "new",
        expected_condition: str = "new"
    ) -> IdentityMatchResult:
        """
        Deterministically evaluates whether candidate listing matches target query.
        Applies rigorous non-semantic constraints.
        """
        # 1. Accessory Check
        is_accessory, acc_reason = self.check_is_accessory(candidate_title)
        query_is_seeking_accessory = any(re.search(rf"\b{k}\b", query.lower()) for k in self.ACCESSORY_KEYWORDS)

        if is_accessory and not query_is_seeking_accessory:
            return IdentityMatchResult(
                is_exact_match=False,
                is_acceptable_alternative=False,
                confidence_score=0.0,
                rejection_reason=acc_reason,
                is_accessory=True
            )

        q_brand, q_clean, q_modifiers = self.extract_brand_and_model(query)
        c_brand, c_clean, c_modifiers = self.extract_brand_and_model(candidate_title)
        if candidate_brand and candidate_brand.lower() in self.BRAND_NORMALIZATION:
            c_brand = self.BRAND_NORMALIZATION[candidate_brand.lower()]

        # 2. Brand Compatibility
        if q_brand and c_brand and q_brand != c_brand:
            return IdentityMatchResult(
                is_exact_match=False,
                is_acceptable_alternative=False,
                confidence_score=0.1,
                rejection_reason=f"Brand mismatch: requested '{q_brand}' but candidate is '{c_brand}'",
                target_brand=q_brand,
                detected_brand=c_brand
            )

        # 3. Exact Model Token Evaluation (Critical for Redmi 13 vs Redmi Note 13 / Redmi 13C)
        def tokenize_decomposed(s: str) -> Set[str]:
            words = re.findall(r"\b[a-zA-Z0-9]+\b", s.lower())
            result = set()
            for w in words:
                m = re.match(r"^(\d+)([a-zA-Z]+)$", w)
                if m:
                    result.add(m.group(1))
                    result.add(m.group(2))
                result.add(w)
            return result

        q_tokens = tokenize_decomposed(query)
        c_tokens = tokenize_decomposed(candidate_title)

        # Extract numeric components (e.g. "13", "1000", "5", "4")
        q_numbers = {t for t in q_tokens if t.isdigit()}
        c_numbers = {t for t in c_tokens if t.isdigit()}

        if q_numbers and not q_numbers.issubset(c_tokens):
            return IdentityMatchResult(
                is_exact_match=False,
                is_acceptable_alternative=False,
                confidence_score=0.2,
                rejection_reason=f"Numeric model identifier mismatch: requested numbers {q_numbers} missing in candidate",
                target_model=query,
                detected_model=candidate_title
            )


        # Check for unrequested hardware modifiers (e.g. query has no 'note', but candidate has 'note')
        unwanted_modifiers = c_modifiers - q_modifiers
        if unwanted_modifiers:
            mod_list = ", ".join(sorted(unwanted_modifiers))
            return IdentityMatchResult(
                is_exact_match=False,
                is_acceptable_alternative=True,  # Could be considered a variant/alternative, but NOT exact match
                confidence_score=0.45,
                rejection_reason=f"Distinct model variant: candidate contains modifier(s) '{mod_list}' not requested in query",
                target_model=query,
                detected_model=candidate_title
            )

        # 4. Condition Validation
        condition_matches = True
        if expected_condition != "any" and candidate_condition.lower() != expected_condition.lower():
            condition_matches = False

        # 5. Calculate Deterministic Confidence Score
        # Check token overlap
        overlap = q_tokens.intersection(c_tokens)
        overlap_ratio = len(overlap) / max(1, len(q_tokens))

        is_exact = overlap_ratio >= 0.75 and not unwanted_modifiers and condition_matches

        confidence = round(0.5 + (0.5 * overlap_ratio), 3) if is_exact else round(0.3 * overlap_ratio, 3)
        if not condition_matches:
            confidence = max(0.1, confidence - 0.2)

        return IdentityMatchResult(
            is_exact_match=is_exact,
            is_acceptable_alternative=overlap_ratio >= 0.5,
            confidence_score=confidence,
            rejection_reason=None if is_exact else "Partial match only; does not meet exact model specifications",
            target_brand=q_brand,
            target_model=query,
            detected_brand=c_brand,
            detected_model=candidate_title,
            is_accessory=False,
            condition_match=condition_matches
        )
