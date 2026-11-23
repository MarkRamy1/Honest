# Honest AI 4.0 — Agent Guidelines & Performance Profile

## Performance profile
- Tier: S  (decided 2026-11-23)
- Expected users (6 months): 100–1,000 users (Early Launch)
- Biggest growing tables: `reviews`, `verified_products`, `stores_reputation` (~10k–100k rows/year)
- Freshness needs: Within 1 minute is fine (60s short client & HTTP cache, immediate invalidation on review/upvote write)
- Images: Product & specimen images (`width` and `height` set to prevent CLS, `loading="lazy"` below the fold, `fetchPriority="high"` on primary analysis specimen image)
- Infra budget: Free tier only (no Redis or paid external CDN services required at Tier S)
- Always use the `speed-engineer` skill when touching DB queries/schema, lists, data fetching, images or loading states.
