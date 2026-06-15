from datetime import datetime
import os

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from app.dto.negocio_dto import NegocioDTO
from models.models import Categoria, Estado, Negocio, Usuario
from fastapi.responses import JSONResponse
from database import get_session
from sqlmodel import Session
from starlette import status
from interfaces.interfaces import NegocioInterface, UsuarioResponse
from utils.security import get_current_user
from utils.utils import format_date

router = APIRouter(prefix="/negocio", tags=["negocio"])

load_dotenv()

@router.get("/", response_model=list[NegocioInterface])
def get(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Negocio).all()
    return [
        NegocioInterface(
            id=dato.id,
            nombre=dato.nombre,
            correo=dato.correo,
            telefono=dato.telefono,
            descripcion=dato.descripcion,
            #logo dinamico para que sea visible en frontend
            logo=(f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}"
                if os.getenv('ENVIRONMENT') == "local" else f"https://{os.getenv('AWS_BUCKET_URL')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.logo}"),
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
        for dato in datos
    ]

#listar registros por id
@router.get("/{id}", response_model=NegocioInterface)
def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.query(Negocio).filter(Negocio.id == id).first()

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
#crear registros con commit y refresh, con http exception si falla con rollback
@router.post("/", status_code=status.HTTP_201_CREATED)
def create(dto: NegocioDTO, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    existe = session.query(Negocio).filter(Negocio.nombre == dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Negocio ya existente",
        )
    if dto.usuario_id is not None:
        usuario = session.query(Usuario).filter(Usuario.id == dto.usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    if dto.categoria_id is not None:
        categoria = session.query(Categoria).filter(Categoria.id == dto.categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria no encontrada",
            )
    if dto.estado_id is not None:
        estado = session.query(Estado).filter(Estado.id == dto.estado_id).first()
        if not estado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado no encontrado",
            )
    dato = Negocio(**dto.model_dump())
    try:
        session.add(dato)
        session.commit()
        session.refresh(dato)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el negocio",
        )
    return dato.model_dump()

#editar un registro con commit y refresh, con http exception si falla con rollback
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=NegocioInterface)
def update(id: int, dto: NegocioDTO, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.query(Negocio).filter(Negocio.id == id).first()

    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negocio no encontrado",
        )

    existe = (
        session.query(Negocio)
        .filter(Negocio.nombre == dto.nombre, Negocio.id != id)
        .first()
    )

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Negocio ya existente",
        )

    if dto.usuario_id is not None:
        usuario = session.query(Usuario).filter(Usuario.id == dto.usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )

    if dto.categoria_id is not None:
        categoria = session.query(Categoria).filter(Categoria.id == dto.categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria no encontrada",
            )

    if dto.estado_id is not None:
        estado = session.query(Estado).filter(Estado.id == dto.estado_id).first()
        if not estado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado no encontrado",
            )

    try:
        dato.nombre = dto.nombre
        dato.correo = dto.correo
        dato.telefono = dto.telefono
        dato.descripcion = dto.descripcion
        dato.logo = dto.logo
        dato.mapa = dto.mapa
        dato.usuario_id = dto.usuario_id
        dato.categoria_id = dto.categoria_id
        dato.estado_id = dto.estado_id
        dato.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(dato)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo actualizar el negocio",
        )

    return NegocioInterface(
        id=dato.id,
        nombre=dato.nombre,
        correo=dato.correo,
        telefono=dato.telefono,
        descripcion=dato.descripcion,
        logo=dato.logo,
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

#eliminar un registro con commit y refresh, con http exception si falla con rollback
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.query(Negocio).filter(Negocio.id == id).first()

    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negocio no encontrado",
        )

    try:
        session.delete(dato)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo eliminar el negocio",
        )

    return {
        "message": "Negocio eliminado",
        "id": id,
    }