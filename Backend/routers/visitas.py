from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db
import crud.visita as crud_visita
from schemas import VisitaCreate, VisitaOut, VisitaUpdate


router = APIRouter(
    prefix="/visitas",
    tags=["Visitas"]
)

@router.patch("/{visita_id}/estado", response_model=VisitaOut)
def actualizar_estado_visita(
    visita_id: int,
    data: VisitaUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_visita.update_estado_visita(
            db, visita_id, data.estado
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
@router.get("/disponibilidad")
def obtener_disponibilidad(
    fecha: date,
    id_servicio: int,
    id_barbero: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Devuelve los horarios disponibles para una fecha dada,
    considerando duración del servicio y visitas existentes.
    """
    try:
        return crud_visita.get_disponibilidad(
            db=db,
            fecha=fecha,
            id_servicio=id_servicio,
            id_barbero=id_barbero
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

#----------------------------------------------------------------------------------------------------------------------
# CREAR VISITA (con validación de solapamiento en el CRUD)
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
    try:
        return crud_visita.create_visita(db, visita_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

#----------------------------------------------------------------------------------------------------------------------
# LISTAR TODAS LAS VISITAS
#----------------------------------------------------------------------------------------------------------------------

@router.get("/", response_model=List[VisitaOut])
def listar_visitas(db: Session = Depends(get_db)):
    return crud_visita.get_visitas(db)

#----------------------------------------------------------------------------------------------------------------------
# OBTENER VISITA POR ID
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
# CANCELAR VISITA
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
