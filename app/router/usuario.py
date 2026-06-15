from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlalchemy import desc

from utils.security import get_current_user
from database import get_session
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import Usuario, Estado, Perfil
from app.dto.usuario_dto import UsuarioDto
from utils.utils import format_date, generate_hash


router = APIRouter(prefix="/usuarios", tags=["Usuario"])

@router.get("/", response_model=list[UsuarioResponse])
async def index(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #datos = session.query(Estado).all()
    datos = session.query(Usuario).order_by(desc(Usuario.id)).all()
    resultado = [
        UsuarioResponse(
            id=dato.id,
            nombre=dato.nombre,
            correo=dato.correo,
            telefono=dato.telefono,
            estado_id=dato.estado_id,
            estado=dato.estado.nombre,
            perfil_id=dato.perfil_id,
            perfil=dato.perfil.nombre,
            fecha=format_date(dato.fecha)
        ) for dato in datos
    ]
    
    return resultado


@router.get("/{id}", response_model=UsuarioResponse)
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Usuario, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    resultado = {
        "id": dato.id,
        "nombre": dato.nombre,
        "correo": dato.correo,
        "telefono": dato.telefono,
        "estado_id": dato.estado_id,
        "estado": dato.estado.nombre,
        "perfil_id": dato.perfil_id,
        "perfil": dato.perfil.nombre,
        "fecha": format_date(dato.fecha)
    }

    return resultado


@router.post("/", response_model=GenericInterface)
async def create(dto: UsuarioDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe perfil
    perfil = session.get(Perfil, dto.perfil_id)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El perfil no existe"
        )
    # Validación: correo duplicado
    existe = session.query(Usuario).filter(Usuario.correo == dto.correo).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con el correo proporcionado"
        )
    #se guarda el usuario, por defecto se asigna el estado activo (estado_id=1) y token vacío
    dato_db = Usuario(
        estado_id=1,
        perfil_id=dto.perfil_id,
        nombre=dto.nombre, 
        correo=dto.correo,
        telefono=dto.telefono,
        token='',
        password=generate_hash(dto.password)
        )
    try:
        session.rollback()
        session.add(dato_db)
        session.commit()
        session.refresh(dato_db)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error al crear el registro", "detalle": str(e)}
        )


@router.put("/{id}", response_model=GenericInterface)
async def update(id: int, dto: UsuarioDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe perfil
    perfil = session.get(Perfil, dto.perfil_id)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El perfil no existe"
        )
    #validamos si existe estado
    estado = session.get(Estado, dto.estado_id)
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el estado)"
        )
    dato = session.get(Usuario, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    #actualizamos los datos
    dato.nombre = dto.nombre
    dato.perfil_id=dto.perfil_id
    dato.estado_id=dto.estado_id
    dato.correo=dto.correo
    dato.telefono=dto.telefono
    #si se edita, se genera el hash de la contraseña
    if dto.editar==1:
        dato.password=generate_hash(dto.password)
    try:
       
        session.commit()
        session.refresh(dato)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= {"estado": "ok", "mensaje": f"Se modifica el registro exitosamente"},
        )
    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )


@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #obtenemos el usuario
    dato = session.get(Usuario, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    try:
        #eliminamos el usuario
        session.delete(dato)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"estado": "ok", "mensaje": f"Se elimina el registro exitosamente"},
    )  
