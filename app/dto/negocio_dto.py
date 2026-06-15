from pydantic import BaseModel, model_validator, field_validator
from typing import Optional

class NegocioDTO(BaseModel):
    usuario_id: int | None = None
    categoria_id: int | None = None
    estado_id: Optional[int] = None
    nombre: str
    correo: str
    telefono: str
    descripcion: str
    logo: str
    mapa: str

@model_validator(mode="after")
def validate_name(self):
    if not self.nombre or len(self.nombre) < 3:
        raise ValueError("El nombre del negocio debe tener al menos 3 caracteres")
    return self

@model_validator(mode="after")
def validate_email(self):
    if not self.correo or "@" not in self.correo:
        raise ValueError("Correo electrónico inválido")
    return self
   