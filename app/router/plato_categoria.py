from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlalchemy import desc
from slugify import slugify

from database import get_session
from utils.security import get_current_user
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import PlatosCategoria
from app.dto.plato_categoria_dto import PlatoCategoriaDto


router = APIRouter(prefix="/platos_categoria", tags=["Platos Categorías"])

@router.get("/", response_model=list[PlatosCategoria])
async def index(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(PlatosCategoria).order_by(desc(PlatosCategoria.id)).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[estado.model_dump() for estado in datos],
    )  


@router.get("/{id}", response_model=PlatosCategoria)
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(PlatosCategoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dato.model_dump()
    )


@router.post("/", response_model=GenericInterface)
async def create(dto: PlatoCategoriaDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    # Validación: nombre duplicado
    existe = session.query(PlatosCategoria).filter(PlatosCategoria.nombre == dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ya existe un registro con ese nombre"}
        )
    # hay q crear el slug a partir del nombre, para eso usamos la función slugify
    dato_db = PlatosCategoria(nombre=dto.nombre, slug=slugify(dto.nombre))
    try:
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
async def update(id: int, dto: PlatoCategoriaDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(PlatosCategoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    try:
        dato.nombre = dto.nombre
        dato.slug = slugify(dto.nombre)
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
    dato = session.get(PlatosCategoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    try:
        session.delete(dato)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"estado": "ok", "mensaje": f"Se elimina el registro exitosamente"},
    )  