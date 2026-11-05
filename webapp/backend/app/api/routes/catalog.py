from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.product import VerifiedProduct
from app.models.store import StoreReputation

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/search")
def search_catalog(
    q: str = Query("", description="Search term for products"),
    db: Session = Depends(get_db)
):
    """Search verified products catalog with MSRPs, replica prices, and genuine materials."""
    query = db.query(VerifiedProduct)

    if q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            (VerifiedProduct.name.ilike(term)) |
            (VerifiedProduct.brand.ilike(term)) |
            (VerifiedProduct.category.ilike(term))
        )

    products = query.limit(15).all()

    items = []
    for p in products:
        items.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "original_msrp": float(p.original_msrp),
            "high_copy_avg_price": float(p.high_copy_avg_price),
            "copy_avg_price": float(p.copy_avg_price),
            "authentic_materials": p.authentic_materials,
            "fake_materials": p.fake_materials,
            "verification_telltales": p.verification_telltales or [],
            "recommended_sources": p.recommended_sources or []
        })

    return {
        "success": True,
        "count": len(items),
        "products": items
    }


@router.get("/stores")
def get_stores(db: Session = Depends(get_db)):
    """Retrieve verified stores ordered by trust score."""
    stores = db.query(StoreReputation).order_by(StoreReputation.trust_score.desc()).all()

    items = []
    for s in stores:
        items.append({
            "id": s.id,
            "store_name": s.store_name,
            "platform": s.platform,
            "specialty_tier": s.specialty_tier,
            "trust_score": s.trust_score,
            "material_honesty_rating": float(s.material_honesty_rating),
            "verified_url": s.verified_url,
            "notes": s.notes
        })

    return {
        "success": True,
        "stores": items
    }
