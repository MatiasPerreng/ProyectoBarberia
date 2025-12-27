from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil

from database import get_db
import crud.barbero as crud_barbero
from schemas import (
    BarberoCreate,
    BarberoUpdate,
    BarberoOut,
    AgendaBarberoOut
)

from core.dependencias import get_current_login_barbero

router = APIRouter(
    prefix="/barberos",
    tags=["Barberos"]
)

MEDIA_DIR = Path("media/barberos")


# ---------------------------------------------------------
# PUBLICO
# ---------------------------------------------------------

@router.get("/", response_model=List[BarberoOut])
def listar_barberos(db: Session = Depends(get_db)):
    return crud_barbero.get_barberos(db)


@router.get("/activos", response_model=List[BarberoOut])
def listar_barberos_activos(db: Session = Depends(get_db)):
    return crud_barbero.get_barberos(db, solo_activos=True)


@router.get("/{barbero_id}", response_model=BarberoOut)
def obtener_barbero(barbero_id: int, db: Session = Depends(get_db)):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")
    return barbero


# ---------------------------------------------------------
# DEV – SIN AUTH
# ---------------------------------------------------------

@router.post("/", response_model=BarberoOut, status_code=201)
def crear_barbero(
    barbero_in: BarberoCreate,
    db: Session = Depends(get_db),
):
    return crud_barbero.create_barbero(db, barbero_in)


@router.put("/{barbero_id}", response_model=BarberoOut)
def actualizar_barbero(
    barbero_id: int,
    barbero_in: BarberoUpdate,
    db: Session = Depends(get_db),
):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    return crud_barbero.update_barbero(db, barbero, barbero_in)


@router.patch("/{barbero_id}/toggle", response_model=BarberoOut)
def toggle_barbero(
    barbero_id: int,
    db: Session = Depends(get_db),
):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    return crud_barbero.toggle_barbero_estado(db, barbero)


@router.delete("/{barbero_id}", status_code=204)
def eliminar_barbero(barbero_id: int, db: Session = Depends(get_db)):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    crud_barbero.delete_barbero(db, barbero)
    return None


# ---------------------------------------------------------
# SUBIR FOTO
# ---------------------------------------------------------

@router.post("/{barbero_id}/foto")
def subir_foto_barbero(
    barbero_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix or ".jpg"
    filename = f"barbero_{barbero_id}{ext}"
    filepath = MEDIA_DIR / filename

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    barbero.foto_url = f"/media/barberos/{filename}"
    db.commit()
    db.refresh(barbero)

    return {"foto_url": barbero.foto_url}


# ---------------------------------------------------------
# AGENDA PRIVADA
# ---------------------------------------------------------

@router.get("/mi-agenda", response_model=List[AgendaBarberoOut])
def mi_agenda(
    db: Session = Depends(get_db),
    login=Depends(get_current_login_barbero)
):
    return crud_barbero.get_agenda_barbero(db, login.id_barbero)
