from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil

from database import get_db
import crud.barbero as crud_barbero

from models import LoginBarbero
from schemas import (
    BarberoCreate,
    BarberoUpdate,
    BarberoOut,
    AgendaBarberoOut,
    CrearCuentaBarberoIn
)

from core.dependencias import get_current_login_barbero
from core.security import hash_password


router = APIRouter(
    prefix="/barberos",
    tags=["Barberos"]
)

MEDIA_DIR = Path("media/barberos")

# ---------------------------------------------------------
# AGENDA BARBERO (PRODUCCIÓN · CON AUTH + FK)
# ---------------------------------------------------------

@router.get("/mi-agenda", response_model=List[AgendaBarberoOut])
def mi_agenda(
    login = Depends(get_current_login_barbero),
    db: Session = Depends(get_db),
):
    """
    Devuelve la agenda del barbero logueado.
    Usa la FK: login.barbero_id
    """

    # 👑 Admin no tiene agenda
    if login.role != "barbero" or not login.barbero_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuario no tiene agenda"
        )

    return crud_barbero.get_agenda_barbero(
        db,
        barbero_id=login.barbero_id
    )

# ---------------------------------------------------------
# PÚBLICO
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
# ADMIN
# ---------------------------------------------------------

@router.post("/", response_model=BarberoOut, status_code=status.HTTP_201_CREATED)
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
def toggle_barbero(barbero_id: int, db: Session = Depends(get_db)):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    return crud_barbero.toggle_barbero_estado(db, barbero)

@router.delete("/{barbero_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_barbero(barbero_id: int, db: Session = Depends(get_db)):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    crud_barbero.delete_barbero(db, barbero)
    return None

# ---------------------------------------------------------
# CREAR ACCESO PARA BARBERO (ADMIN)
# ---------------------------------------------------------

@router.post("/{barbero_id}/crear-acceso", status_code=status.HTTP_201_CREATED)
def crear_acceso_barbero(
    barbero_id: int,
    data: CrearCuentaBarberoIn,
    db: Session = Depends(get_db),
    admin = Depends(get_current_login_barbero),
):
    # validar admin
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado"
        )

    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)
    if not barbero:
        raise HTTPException(404, "Barbero no encontrado")

    # evitar duplicado
    existe = (
        db.query(LoginBarbero)
        .filter(LoginBarbero.barbero_id == barbero_id)
        .first()
    )
    if existe:
        raise HTTPException(
            status_code=400,
            detail="El barbero ya tiene acceso"
        )

    login = LoginBarbero(
        nombre=barbero.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.rol,              # ✅ CORRECTO
        barbero_id=barbero_id,
        is_active=True
    )

    db.add(login)
    db.commit()
    db.refresh(login)

    return {"ok": True}

# ---------------------------------------------------------
# SUBIR FOTO BARBERO (ADMIN)
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
