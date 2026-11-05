from datetime import datetime, timezone
from fastapi import APIRouter
from app.services.honest_audit import HonestAuditService
from app.schemas.vlm import VlmAuditRequest, GenerateRealityRequest

router = APIRouter(prefix="/vlm", tags=["Multimodal VLM"])
audit_service = HonestAuditService()


@router.post("/audit")
def audit_product(payload: VlmAuditRequest):
    """Multimodal catalog vs video frame visual audit."""
    p_name = payload.get_product_name()
    img_url = payload.get_image_url()
    cat = payload.category or ""

    audit_result = audit_service.audit_product(p_name, img_url, cat)

    return {
        "success": True,
        "audit": audit_result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/generate-reality")
def generate_reality(payload: GenerateRealityRequest):
    """Generative reality synthesis prompt generator (FLUX.1 / SD)."""
    prompt = payload.prompt or "Real-world consumer product photo under natural room light"
    lighting = payload.lighting or "natural"

    return audit_service.generate_reality(prompt, lighting)
