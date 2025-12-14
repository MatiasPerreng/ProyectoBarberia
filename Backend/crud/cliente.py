from sqlalchemy.orm import Session
from typing import List, Optional

from models import Cliente
from schemas import ClienteCreate, ClienteUpdate


 #----------------------------------------------------------------------------------------------------------------------

def create_cliente(db: Session, cliente_in: ClienteCreate) -> Cliente:
    cliente = Cliente(
        nombre=cliente_in.nombre,
        telefono=cliente_in.telefono,
        email=cliente_in.email,
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente

def get_clientes(db: Session) -> List[Cliente]:
    return db.query(Cliente).all()


 #----------------------------------------------------------------------------------------------------------------------

def get_cliente_by_id(db: Session, cliente_id: int) -> Optional[Cliente]:
    return db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()


 #----------------------------------------------------------------------------------------------------------------------

def update_cliente(
    db: Session,
    cliente: Cliente,
    cliente_in: ClienteUpdate
) -> Cliente:
    
    if cliente_in.nombre is not None:
        cliente.nombre = cliente_in.nombre
    if cliente_in.telefono is not None:
        cliente.telefono = cliente_in.telefono
    if cliente_in.email is not None:
        cliente.email = cliente_in.email

    db.commit()
    db.refresh(cliente)

    return cliente

 #----------------------------------------------------------------------------------------------------------------------

def delete_cliente(db: Session, cliente: Cliente) -> None:
    db.delete(cliente)
    db.commit()

 #----------------------------------------------------------------------------------------------------------------------