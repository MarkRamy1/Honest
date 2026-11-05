import html
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Embed"])


@router.get("/embed", response_class=HTMLResponse)
def embed_player(
    v: str = Query("", description="Video ID"),
    platform: str = Query("youtube", description="Platform: youtube or tiktok")
):
    """Embedded video player relay for social unboxing video clips."""
    safe_v = html.escape(v)
    safe_plat = html.escape(platform)

    if safe_plat == "tiktok":
        iframe_src = f"https://www.tiktok.com/player/v1/{safe_v}?autoplay=1"
    else:
        iframe_src = f"https://www.youtube.com/embed/{safe_v}?autoplay=1&rel=0"

    content = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>* {{ margin:0; padding:0; box-sizing:border-box; }} html, body {{ width:100%; height:100%; background:#000; overflow:hidden; display:flex; align-items:center; justify-content:center; }} iframe {{ width:100%; height:100%; border:none; }}</style>
</head><body>
<iframe src="{iframe_src}" allow="autoplay; encrypted-media" allowfullscreen></iframe>
</body></html>"""

    return HTMLResponse(content=content, status_code=200)
