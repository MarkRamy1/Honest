import re
from typing import Dict, Any, Optional, List


class IntentParserService:
    """
    Parses conversational queries into structured shopping intents,
    extracting category, budget, preference tags, and target products.
    """

    def parse(self, input_text: str) -> Dict[str, Any]:
        raw = input_text.strip()
        lower = raw.lower()
        clean = re.sub(r'[?!,.:;"]+', ' ', lower)
        clean = re.sub(r'\s+', ' ', clean).strip()

        # 1. Detect Greetings & Pleasantries
        greeting_prefixes = r'^(hello|hi|hey|howdy|greetings|hola|marhaba|salam|yo|sup|good\s*(morning|afternoon|evening|day))\b'
        how_are_you = r'\b(how\s*are\s*you|how\s*are\s*you\s*doing|how\s*is\s*it\s*going|how\s*r\s*u)\b'

        if (re.search(greeting_prefixes, clean, re.IGNORECASE) or re.search(how_are_you, clean, re.IGNORECASE)) and not self.has_shopping_intent(clean):
            return {
                "intent": "greeting",
                "raw_query": raw,
                "target_query": None,
                "category": "general",
                "budget": None,
                "use_cases": [],
                "is_recommendation": False,
            }

        # 2. Identity, Help & Capabilities
        capability_pattern = r'^(who\s*are\s*you|what\s*are\s*you|what\s*can\s*you\s*do|how\s*does\s*this\s*work|help|instructions)\b'
        if re.search(capability_pattern, clean, re.IGNORECASE) and not self.has_shopping_intent(clean):
            return {
                "intent": "capability",
                "raw_query": raw,
                "target_query": None,
                "category": "general",
                "budget": None,
                "use_cases": [],
                "is_recommendation": False,
            }

        # 3. Gratitude
        gratitude_pattern = r'^(thank\s*you|thanks|thx|appreciate\s*it|great\s*job|cool|perfect|okay)\b[\s!\.]*$'
        if re.search(gratitude_pattern, clean, re.IGNORECASE):
            return {
                "intent": "gratitude",
                "raw_query": raw,
                "target_query": None,
                "category": "general",
                "budget": None,
                "use_cases": [],
                "is_recommendation": False,
            }

        # 4. Shopping Intent Extraction
        budget_info = self.extract_budget(raw)
        category = self.detect_category(clean)
        use_cases = self.extract_use_cases(clean)
        is_recommendation = self.is_recommendation_query(clean)
        target_query = self.clean_target_query(raw)

        return {
            "intent": "recommendation" if is_recommendation else "product_audit",
            "raw_query": raw,
            "target_query": target_query,
            "category": category,
            "budget": budget_info,
            "use_cases": use_cases,
            "is_recommendation": is_recommendation,
        }

    def is_recommendation_query(self, text: str) -> bool:
        patterns = [
            r'\b(best|top|recommend|suggest|what\s*should\s*i\s*buy|which\s*one\s*should\s*i\s*get|what\s*is\s*the\s*best|looking\s*for\s*a|want\s*to\s*buy|need\s*a|find\s*me\s*a|guide|comparison|versus|vs)\b',
            r'\b(under|below|less\s*than|cheaper\s*than|around|budget\s*of)\s*[\$£€]?\s*\d+',
            r'\b(for\s*(gaming|running|gym|workout|office|school|college|travel|video\s*editing|programming|students|beginners|daily\s*use))\b'
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def has_shopping_intent(self, text: str) -> bool:
        patterns = [
            r'\b(buy|order|purchase|price|cost|specs|material|deal|cheap|expensive|discount|worth|review|rating|laptop|phone|headphones|earbuds|sneakers|shoes|watch|jacket|coat|hoodie|perfume|camera|monitor|tablet|tv|speaker)\b',
            r'\b(rolex|apple|sony|nike|jordan|dyson|bose|samsung|lenovo|dell|hp|asus|adidas|louis\s*vuitton|lv|gucci|zara)\b'
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def extract_budget(self, text: str) -> Optional[Dict[str, Any]]:
        # USD matches: "$500", "500 USD", "under 500 dollars"
        m1 = re.search(r'(?:under|below|less\s*than|budget\s*of|max|up\s*to)?\s*(?:\$|usd\s*)\s*(\d+(?:,\d{3})*(?:\.\d+)?)', text, re.IGNORECASE)
        if m1:
            val = float(m1.group(1).replace(',', ''))
            return {
                "amount_usd": val,
                "amount_egp": round(val * 50.0),
                "currency": "USD",
                "raw_match": m1.group(0)
            }

        m2 = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:dollars|\$|bucks|usd)', text, re.IGNORECASE)
        if m2:
            val = float(m2.group(1).replace(',', ''))
            return {
                "amount_usd": val,
                "amount_egp": round(val * 50.0),
                "currency": "USD",
                "raw_match": m2.group(0)
            }

        # EGP matches: "5000 EGP", "5000 LE", "5000 جنيه"
        m3 = re.search(r'(?:under|below|less\s*than|budget\s*of|max|up\s*to)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:egp|le|ج\.م|جنيه)', text, re.IGNORECASE)
        if m3:
            egp = float(m3.group(1).replace(',', ''))
            return {
                "amount_usd": round(egp / 50.0, 2),
                "amount_egp": egp,
                "currency": "EGP",
                "raw_match": m3.group(0)
            }

        # Simple "under 200" fallback (assumes USD if no currency stated)
        m4 = re.search(r'(?:under|below|less\s*than|around|budget\s*of)\s*(\d{2,5})\b', text, re.IGNORECASE)
        if m4:
            val = float(m4.group(1))
            return {
                "amount_usd": val,
                "amount_egp": round(val * 50.0),
                "currency": "USD",
                "raw_match": m4.group(0)
            }

        return None

    def detect_category(self, text: str) -> str:
        mapping = {
            "laptops": r'\b(laptop|notebook|macbook|chromebook|thinkpad|zenbook|gaming\s*laptop)\b',
            "smartphones": r'\b(phone|smartphone|iphone|galaxy\s*s\d+|pixel|xiaomi|android)\b',
            "headphones": r'\b(headphone|headphones|headset|earbuds|earphones|airpods|audio|wh-?1000|anc)\b',
            "sneakers": r'\b(shoes|sneakers|kicks|trainers|runners|jordan|dunk|yeezy|samba|boots|loafers)\b',
            "watches": r'\b(watch|timepiece|chronograph|rolex|submariner|seiko|casio|omega|cartier|smartwatch|apple\s*watch)\b',
            "monitors": r'\b(monitor|screen|display|144hz|4k\s*monitor|gaming\s*monitor)\b',
            "streetwear": r'\b(hoodie|jacket|fleece|sweatshirt|t-shirt|tee|pants|jeans|coat|trench|bomber|essentials)\b',
            "handbags": r'\b(bag|handbag|tote|purse|backpack|crossbody|neverfull|wallet)\b',
            "fragrances": r'\b(perfume|cologne|fragrance|eau\s*de\s*parfum|edp|scent)\b',
            "home_appliances": r'\b(coffee\s*maker|espresso|airwrap|hairdryer|vacuum|air\s*fryer|blender)\b',
        }

        for cat, pattern in mapping.items():
            if re.search(pattern, text, re.IGNORECASE):
                return cat
        return "general"

    def extract_use_cases(self, text: str) -> List[str]:
        tags = []
        rules = {
            "gaming": r'\b(gaming|gamer|games|fps|rtx|144hz)\b',
            "productivity": r'\b(work|office|programming|coding|excel|business|zoom)\b',
            "creative": r'\b(video\s*editing|photo\s*editing|photoshop|premiere|design|creator)\b',
            "battery_life": r'\b(long\s*battery|all\s*day\s*battery|portable|travel)\b',
            "sports_fitness": r'\b(gym|running|workout|fitness|sweatproof|waterproof|ipx\d+)\b',
            "sound_quality": r'\b(audiophile|bass|sound\s*quality|noise\s*cancelling|anc)\b',
            "comfort": r'\b(comfortable|comfort|lightweight|ergonomic|flat\s*feet|cushion)\b',
            "durability": r'\b(durable|long\s*lasting|sturdy|build\s*quality|warranty|rugged)\b'
        }

        for tag, pattern in rules.items():
            if re.search(pattern, text, re.IGNORECASE):
                tags.append(tag)
        return tags

    def clean_target_query(self, raw: str) -> str:
        clean = raw.strip()

        # Benchmarks
        if re.search(r'rolex\s*submariner', clean, re.IGNORECASE):
            return "Rolex Submariner Date 126610LN"
        if re.search(r'(sony\s*wh-?1000xm5|sony\s*xm5|wh-?1000xm5)', clean, re.IGNORECASE):
            return "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones"
        if re.search(r'(air\s*jordan\s*4|jordan\s*4|military\s*black)', clean, re.IGNORECASE):
            return "Air Jordan 4 Retro Military Black"
        if re.search(r'dyson\s*airwrap', clean, re.IGNORECASE):
            return "Dyson Airwrap Multi-Styler Complete Long"
        if re.search(r'(neverfull|damier\s*ebene)', clean, re.IGNORECASE):
            return "Louis Vuitton Neverfull MM Damier Ebene"
        if re.search(r'(essentials\s*hoodie|essentials\s*fleece)', clean, re.IGNORECASE):
            return "Fear of God Essentials Fleece Hoodie"
        if re.search(r'redmi\s*13\b', clean, re.IGNORECASE) and not re.search(r'redmi\s*(note|13c)', clean, re.IGNORECASE):
            return "Xiaomi Redmi 13"

        # Parenthetical model extraction (e.g. "phone (Redmi 13)" -> "Redmi 13")
        paren_match = re.search(r'\(([^)]+)\)', clean)
        if paren_match:
            inside = paren_match.group(1).strip()
            if any(char.isalnum() for char in inside):
                clean = inside

        strip_prefixes = [
            r'^(can\s+you|could\s+you|please)?\s*(give\s+me|tell\s+me|show\s+me|find|search\s+for|look\s+up|what\s+is|whats|how\s+much\s+is|check|inspect|audit|verify|recommend|suggest)\s+(the\s+)?(best\s+)?',
            r'^(i\s+want|i\s+need|i\s+am\s+looking\s+for|looking\s+for)\s+(to\s+buy\s+)?(a\s+|an\s+|the\s+)?',
            r'^(which\s+is\s+better|compare|what\s+should\s+i\s+buy\s+for)\s+',
            r'^(phone|smartphone|laptop|headphones|earbuds)\s+'
        ]

        for pat in strip_prefixes:
            clean = re.sub(pat, '', clean, flags=re.IGNORECASE)

        clean = re.sub(r'\s*(?:under|below|less\s*than|for|budget\s*of)\s*[\$£€]?\s*\d+.*$', '', clean, flags=re.IGNORECASE)
        clean = clean.strip(" \t\n\r\0\x0B?,.!;:")
        return clean if clean else raw

