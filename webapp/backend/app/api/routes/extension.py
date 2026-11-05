import io
import os
import zipfile
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["Extension"])


@router.get("/extension/download")
def download_extension():
    """Zip and download the Chrome Extension package directly from the server."""
    # Resolve extension folder (checks D:\Honest\extension and fallback locations)
    here = Path(__file__).resolve()
    candidates = [p / "extension" for p in here.parents]
    extension_dir = str(next((p for p in candidates if p.is_dir()), candidates[0]))
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(extension_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extension_dir)
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=honest4-extension.zip"}
    )
