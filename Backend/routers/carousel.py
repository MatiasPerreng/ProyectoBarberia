"""
Fotos del carrusel de la galería (página pública).
Admin puede subir, eliminar y ver el orden.
"""
import os
import json
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from core.dependencias import get_current_admin

router = APIRouter(prefix="/carousel", tags=["Carrusel"])

_THIS_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = _THIS_DIR / "static" / "carousel"
CONFIG_FILE = _THIS_DIR / "carousel_config.json"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 MB


def _ensure_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _read_config():
    _ensure_dir()
    if not CONFIG_FILE.exists():
        return {"imagenes": []}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"imagenes": []}


def _write_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@router.get("")
def listar_imagenes():
    """Lista las imágenes del carrusel en orden. Público."""
    config = _read_config()
    base_url = "/media/carousel"
    return [
        {"filename": fn, "url": f"{base_url}/{fn}"}
        for fn in config.get("imagenes", [])
        if (UPLOAD_DIR / fn).exists()
    ]


@router.post("/upload")
def subir_imagen(
    file: UploadFile = File(...),
    admin=Depends(get_current_admin),
):
    """Sube una imagen al carrusel. Solo admin."""
    _ensure_dir()

    ext = "." + (file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    content = file.file.read()
    file.file.seek(0)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx. 8 MB)")

    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    config = _read_config()
    imagenes = config.get("imagenes", [])
    imagenes.append(filename)
    config["imagenes"] = imagenes
    _write_config(config)

    return {"filename": filename, "url": f"/media/carousel/{filename}"}


@router.delete("/{filename}")
def eliminar_imagen(
    filename: str,
    admin=Depends(get_current_admin),
):
    """Elimina una imagen del carrusel. Solo admin."""
    # Evitar path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")

    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    config = _read_config()
    imagenes = config.get("imagenes", [])
    if filename in imagenes:
        imagenes.remove(filename)
        config["imagenes"] = imagenes
        _write_config(config)

    try:
        filepath.unlink()
    except OSError:
        pass

    return {"ok": True}
