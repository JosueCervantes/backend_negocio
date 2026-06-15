from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from utils.security import get_current_user
from fastapi.responses import RedirectResponse

import time
import uuid
from dotenv import load_dotenv
load_dotenv()
import os

from database import get_session
from utils.utils import generate_hash
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import Usuario
from app.dto.recovery_dto import RecoveryDto
from app.dto.recovery_update import RecoveryUpdateDto

#aws
import boto3
from botocore.exceptions import ClientError

router = APIRouter(prefix="/recovery", tags=["Recovery"])

#si es local, se usa el url de la imagen en el bucket, si no, se usa la url del bucket en s3
if os.getenv('ENVIRONMENT')=="local":
    sqs_client = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fake"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
    endpoint_url=os.getenv("AWS_SECRET_ACCESS_URL")
)
else:
    sqs_client = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fake"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
)


@router.post("/update/{token}")
async def update(token: str, dto: RecoveryUpdateDto, session: Session = Depends(get_session)):
    # Validar el token y obtener el usuario asociado
    dato = session.exec(
        select(Usuario).where(Usuario.token == token, Usuario.estado_id == 1)
    ).first()
# Validamos que exista el token
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existe el token"
        )
    try:
        # Actualizamos el token del usuario
        dato.password = generate_hash(dto.password)
        dato.token=''
        # Guardamos los cambios
        session.commit()
        session.refresh(dato)
        #redireccionar aquí
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado": "ok", "mensaje": "Se modificó el registro exitosamente"},
        )
    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )


@router.post("/restablecer", response_model=GenericInterface)
async def create(dto: RecoveryDto, session: Session = Depends(get_session) ):
    # Buscar al usuario por correo
    dato = session.exec(
        select(Usuario).where(Usuario.correo == dto.correo, Usuario.estado_id == 1)
    ).first()
    # Validamos que exista el correo
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existe el correo"
        )
    # Generamos un token aleatorio para la recuperación de contraseña
    token = f"{uuid.uuid4()}{int(time.time())}{uuid.uuid4()}"
    # Generamos el url para redireccionar al usuario a la página de actualización de contraseña
    url = f"{os.getenv('BASE_URL_FRONTEND')}/recovery/update/{token}"

    try:
        # Actualizamos el token del usuario
        dato.token = token
        session.commit()
        session.refresh(dato)
        # Generamos un MessageGroupId único
        message_group_id = str(int(time.time()))
        # Enviamos mensaje a la cola SQS
        sqs_client.send_message(
            QueueUrl=os.getenv("SQS_ENVIO_CORREO"),
            MessageBody=url,
            MessageAttributes={
                'Nombre': {
                    'DataType': 'String',
                    'StringValue': dato.nombre
                },
                'Token': {
                    'DataType': 'String',
                    'StringValue': token
                }
            },
            # Generamos un MessageGroupId único
            MessageGroupId=message_group_id,
            MessageDeduplicationId=str(uuid.uuid4()) 
        )

        
        return GenericInterface(estado="ok", mensaje="Se modifica el registro exitosamente")

    except ClientError as ce:
        # Si ocurre un error en el envio del mensaje a la cola, se devuelve el error
        session.rollback()
        error_code = ce.response['Error']['Code']
        error_msg = ce.response['Error']['Message']
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"code error={error_code} | message={error_msg}"
        ) from ce

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo enviar el mensaje a la cola"
        ) from e

