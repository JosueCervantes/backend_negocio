from datetime import datetime
import os

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from app.dto.negocio_dto import NegocioDTO
from models.models import Negocio, Usuario
from fastapi.responses import JSONResponse
from database import get_session
from sqlmodel import Session
from starlette import status
from interfaces.interfaces import NegocioInterface, UsuarioResponse
from utils.security import get_current_user
from utils.utils import format_date

router = APIRouter(prefix="/negocio_by_user", tags=["negocio_by_user"])

load_dotenv()

@router.get("/{id}", response_model=list[NegocioInterface])
async def get_by_user(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos que existe el usuario
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    dato = session.query(Negocio).filter(Negocio.usuario_id == id).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negocio no encontrado",
        )
    if os.getenv('ENVIRONMENT') == "local":
        logo_url = f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}"
    else:
        logo_url = f"https://{os.getenv('AWS_BUCKET_URL')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.logo}"
    return NegocioInterface(
        id=dato.id,
        nombre=dato.nombre,
        correo=dato.correo,
        telefono=dato.telefono,
        descripcion=dato.descripcion,
        logo=logo_url,
        mapa=dato.mapa,
        estado_id=dato.estado_id,
        estado=dato.estado.nombre if dato.estado else None,
        categoria_id=dato.categoria_id,
        categoria=dato.categoria.nombre if dato.categoria else None,
        usuario_id=dato.usuario_id,
        usuario=dato.usuario.nombre if dato.usuario else None,
        created_at=format_date(dato.created_at) if dato.created_at else None,
        updated_at=format_date(dato.updated_at) if dato.updated_at else None,
    )