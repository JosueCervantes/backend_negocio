from fastapi import APIRouter, HTTPException, Depends
from app.dto.estado_dto import EstadoDTO
from interfaces.interfaces import UsuarioResponse
from models.models import Estado
from fastapi.responses import JSONResponse
from database import get_session
from sqlmodel import Session
from starlette import status

from utils.security import get_current_user

router = APIRouter(prefix="/estado", tags=["estado"])

@router.get("/")
async def index(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):   
    datos = session.query(Estado).all()
    return JSONResponse(
       status_code=200,
       content=[dato.model_dump() for dato in datos]
    )

#listar registros por id
@router.get("/{id}")
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.query(Estado).filter(Estado.id == id).first()
    if not dato:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return JSONResponse(
        status_code=200,
        content=dato.model_dump()
    )

#crear registros con commit y refresh, con http exception si falla con rollback
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(dto: EstadoDTO, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = Estado(**dto.model_dump())
    existe = session.query(Estado).filter(Estado.nombre == dato.nombre).first()
    # Si el estado ya existe, se lanza una excepción HTTP 400 Bad Request
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado ya existente"
        )
    try:
        session.add(dato)
        session.commit()
        session.refresh(dato)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el estado",
        )
    return dato.model_dump()

#editar un registro con commit y refresh, con http exception si falla con rollback
@router.put("/{id}", status_code=status.HTTP_200_OK)
def update(id: int, dto: EstadoDTO, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.query(Estado).filter(Estado.id == id).first()
    if not dato:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    existe = (
        session.query(Estado)
        .filter(Estado.nombre == dto.nombre, Estado.id != id)
        .first()
    ) 
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado ya existente",
        )
    try:
        dato.nombre = dto.nombre
        dato.descripcion = dto.descripcion
        session.commit()
        session.refresh(dato)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo actualizar el estado",
        )
    return dato.model_dump()

#eliminar un registro con commit y refresh, con http exception si falla con rollback
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.query(Estado).filter(Estado.id == id).first()
    if not dato:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    try:
        session.delete(dato)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo eliminar el estado",
        )
    return {"message": "Estado eliminado"}