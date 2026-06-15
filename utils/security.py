from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from models.models import Usuario
from sqlmodel import Session
from database import get_session

from interfaces.interfaces import UsuarioResponse
from utils.utils import format_date


import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# Esquema de seguridad
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#funcion para obtener el usuario actual
def get_current_user(
    # almacenamos el token en la variable token 
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decodificamos el token
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # obtenemos el usuario
    usuario = session.get(Usuario, user_id)

    if usuario is None:
        raise credentials_exception

    return UsuarioResponse(
        id=usuario.id,
        nombre=usuario.nombre,
        telefono=usuario.telefono,
        correo=usuario.correo,
        estado_id=usuario.estado_id,
        estado=usuario.estado.nombre,
        perfil_id=usuario.perfil_id,
        perfil=usuario.perfil.nombre,
        fecha=format_date(usuario.fecha),
    )