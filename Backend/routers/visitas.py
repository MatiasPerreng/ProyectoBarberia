from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud.visita as crud_visita
from schemas import VisitaCreate, VisitaOut

router = APIRouter(
    prefix="/visitas",
    tags=["Visitas"]
)

#----------------------------------------------------------------------------------------------------------------------

@router.post(
    "/",
    response_model=VisitaOut,
    status_code=status.HTTP_201_CREATED
)
def crear_visita(
    visita_in: VisitaCreate,
    db: Session = Depends(get_db)
):
    visita = crud_visita.create_visita(db, visita_in)
    return visita

#----------------------------------------------------------------------------------------------------------------------

@router.get("/{visita_id}", response_model=VisitaOut)
def obtener_visita(visita_id: int, db: Session = Depends(get_db)):
    visita = crud_visita.get_visita_by_id(db, visita_id)

    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )

    return visita

#----------------------------------------------------------------------------------------------------------------------

@router.get("/", response_model=List[VisitaOut])
def listar_visitas(db: Session = Depends(get_db)):
    return crud_visita.get_visitas(db)

#----------------------------------------------------------------------------------------------------------------------

@router.delete("/{visita_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_visita(visita_id: int, db: Session = Depends(get_db)):
    visita = crud_visita.get_visita_by_id(db, visita_id)

    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )

    crud_visita.delete_visita(db, visita)

#----------------------------------------------------------------------------------------------------------------------
