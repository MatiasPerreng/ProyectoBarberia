from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud.servicio as crud_servicio
from schemas import ServicioCreate, ServicioUpdate, ServicioOut


router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"]
)

#----------------------------------------------------------------------------------------------------------------------

@router.get("/", response_model=List[ServicioOut])
def listar_servicios(db: Session = Depends(get_db)):
    return crud_servicio.get_servicios(db)

#----------------------------------------------------------------------------------------------------------------------

@router.get("/{servicio_id}", response_model=ServicioOut)
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    servicio = crud_servicio.get_servicio_by_id(db, servicio_id)

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )

    return servicio

#----------------------------------------------------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ServicioOut,
    status_code=status.HTTP_201_CREATED
)
def crear_servicio(
    servicio_in: ServicioCreate,
    db: Session = Depends(get_db)
):
    return crud_servicio.create_servicio(db, servicio_in)

#----------------------------------------------------------------------------------------------------------------------

@router.put("/{servicio_id}", response_model=ServicioOut)
def actualizar_servicio(
    servicio_id: int,
    servicio_in: ServicioUpdate,
    db: Session = Depends(get_db)
):
    servicio = crud_servicio.get_servicio_by_id(db, servicio_id)

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )

    return crud_servicio.update_servicio(db, servicio, servicio_in)

#----------------------------------------------------------------------------------------------------------------------

@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    servicio = crud_servicio.get_servicio_by_id(db, servicio_id)

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )

    crud_servicio.delete_servicio(db, servicio)
    return None
