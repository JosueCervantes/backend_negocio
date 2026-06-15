from pydantic import BaseModel, model_validator
from typing import Optional

class UsuarioDto(BaseModel):
    estado_id: Optional[int] = None 
    editar: Optional[int] = None 
    perfil_id:int
    nombre: str
    correo: str
    telefono: str
    password: str

    @model_validator(mode='after')
    def validar_nombre(self):
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise ValueError('nombre', 'El campo nombre debe tener al menos 2 caracteres')
        return self
