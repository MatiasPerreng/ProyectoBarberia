from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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

#----------------------------------------------------------------------------------------------------------------------
# BARBEROS (PUBLICO)
#----------------------------------------------------------------------------------------------------------------------

@router.get("/", response_model=List[BarberoOut])
def listar_barberos(db: Session = Depends(get_db)):
    return crud_barbero.get_barberos(db)

#----------------------------------------------------------------------------------------------------------------------

@router.get("/{barbero_id}", response_model=BarberoOut)
def obtener_barbero(barbero_id: int, db: Session = Depends(get_db)):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)

    if not barbero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no encontrado"
        )

    return barbero

#----------------------------------------------------------------------------------------------------------------------
# BARBEROS (PRIVADO)
#----------------------------------------------------------------------------------------------------------------------

@router.post(
    "/",
    response_model=BarberoOut,
    status_code=status.HTTP_201_CREATED
)
def crear_barbero(
    barbero_in: BarberoCreate,
    db: Session = Depends(get_db),
    login=Depends(get_current_login_barbero)
):
    return crud_barbero.create_barbero(db, barbero_in)

#----------------------------------------------------------------------------------------------------------------------

@router.put("/{barbero_id}", response_model=BarberoOut)
def actualizar_barbero(
    barbero_id: int,
    barbero_in: BarberoUpdate,
    db: Session = Depends(get_db),
    login=Depends(get_current_login_barbero)
):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)

    if not barbero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no encontrado"
        )

    return crud_barbero.update_barbero(db, barbero, barbero_in)

#----------------------------------------------------------------------------------------------------------------------

@router.delete("/{barbero_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_barbero(
    barbero_id: int,
    db: Session = Depends(get_db),
    login=Depends(get_current_login_barbero)
):
    barbero = crud_barbero.get_barbero_by_id(db, barbero_id)

    if not barbero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no encontrado"
        )

    crud_barbero.delete_barbero(db, barbero)
    return None

#----------------------------------------------------------------------------------------------------------------------
# AGENDA BARBERO (PRIVADO)
#----------------------------------------------------------------------------------------------------------------------

@router.get(
    "/mi-agenda",
    response_model=List[AgendaBarberoOut]
)
def mi_agenda(
    db: Session = Depends(get_db),
    login=Depends(get_current_login_barbero)
):
    return crud_barbero.get_agenda_barbero(db, login.id_barbero)
