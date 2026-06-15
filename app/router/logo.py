from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi.responses import JSONResponse
from database import get_session
from sqlmodel import Session
from starlette import status
from interfaces.interfaces import GenericInterface, UsuarioResponse
from utils.security import get_current_user
from utils.utils import format_date
import boto3
import os
from models.models import Negocio
from typing import Annotated
import uuid

from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/logo", tags=["logo"])

#cliente s3 apuntando a localstack
if os.getenv('ENVIRONMENT') == "local":
    s3_client = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        endpoint_url=os.getenv("LOCALSTACK_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
else:
        s3_client = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

@router.post("/", response_model=GenericInterface)
async def create(id: Annotated[int, Form()], file: UploadFile, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos que existe el negocio
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    logo=dato.logo
    
    #subimos el archivo
    extension = None
    if file.content_type == "image/jpeg":
        extension = "jpg"
    elif file.content_type == "image/png":
        extension = "png"
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "BAD REQUEST", "mensaje": "Formato de imagen no permitido"},
        )

    nombre = f"{uuid.uuid4()}.{extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            os.getenv('S3_BUCKET_NAME'),
            f"archivos/{nombre}",
            ExtraArgs={"ContentType": file.content_type}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "BAD REQUEST", "mensaje": "Error al subir archivo a S3", "detalle": str(e)},
        )
    #actualizamos el valor del logo en la BD
    try:
        dato.logo = f"{nombre}"
        session.commit()
        session.refresh(dato)
        
    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )
    
    #borramos el archivo anterior de la BD (si no es el logo por defecto)
    if logo == os.getenv("S3_LOGO_NEGOCIO"):
        pass
    else:
        try:
            s3_client.delete_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{logo}")
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Error al borrar archivo de S3",
            )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "estado": "ok",
            "mensaje": "Se modifica el registro exitosamente"
        },
    )