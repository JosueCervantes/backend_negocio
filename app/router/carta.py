from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy import desc

from utils.utils import format_date

from dotenv import load_dotenv
load_dotenv()
import os

from database import get_session
from interfaces.interfaces import  NegocioSlugResponse, PlatoResponse
from models.models import Negocio, Platos


router = APIRouter(prefix="/carta-menu", tags=["Carta"])


@router.get("/{slug}", response_model=NegocioSlugResponse) #slug como parámetro de la url
async def show(slug: str, session: Session = Depends(get_session)):
    dato = session.exec( #query de negocio por slug
        select(Negocio).where(Negocio.slug == slug, Negocio.estado_id == 1)
    ).first()
    #validamos que exista el negocio
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (No existe negocio por slug)"
        )

    platos = session.exec( #query de platos por negocio
        select(Platos).order_by(desc(Platos.id)).where(Platos.negocio_id == dato.id)
    ).all()

    # Convertimos cada Plato a PlatoResponse
    platos_response = [
        PlatoResponse(
            id=plato.id,
            nombre=plato.nombre,
            ingredientes=plato.ingredientes,
            precio=plato.precio,
            foto=f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{plato.foto}",
            platoscategoria=plato.platoscategoria.nombre if plato.platoscategoria else None
        ) for plato in platos
    ]
    #si es local, se usa el url de la imagen en el bucket, si no, se usa la url del bucket en s3
    if os.getenv('ENVIRONMENT') == "local":
        logo_url = f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}"
    else:
        logo_url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.logo}"
    resultado = {
        "id": dato.id,
        "nombre": dato.nombre,
        "logo": logo_url,
        "mapa": dato.mapa,
        "facebook": dato.facebook,
        "descripcion": dato.descripcion,
        "instagram": dato.instagram,
        "twitter": dato.twitter,
        "slug": dato.slug,
        "correo": dato.correo,
        "tiktok": dato.tiktok,
        "telefono": dato.telefono,
        "estado_id": dato.estado_id,
        "estado": dato.estado.nombre if dato.estado else None,
        "usuario_id": dato.usuario_id,
        "usuario": dato.usuario.nombre if dato.usuario else None,
        "categoria_id": dato.categoria_id,
        "categoria": dato.categoria.nombre if dato.categoria else None,
        "direccion": dato.direccion,
        "fecha": format_date(dato.fecha),
        "platos": platos_response  
    }

    return resultado