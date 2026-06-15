from pydantic import BaseModel


class GenericInterface(BaseModel):
    estado: str
    mensaje: str

class NegocioInterface(BaseModel):
    nombre: str
    correo: str
    telefono: str
    descripcion: str
    logo: str
    mapa: str
    estado_id: int | None = None
    estado: str | None = None
    categoria_id: int | None = None
    categoria: str | None = None
    usuario_id: int | None = None
    usuario: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        from_attributes = True

class PlatoResponse(BaseModel):
    id: int
    nombre: str
    ingredientes: str
    precio: int
    foto: str
    platoscategoria: str 

    class Config:
        from_attributes = True


class NegocioSlugResponse(BaseModel):
    id: int
    nombre: str
    logo: str
    mapa: str
    descripcion: str
    slug: str
    correo: str
    telefono: str
    estado_id: int
    estado: str
    usuario_id: int
    usuario: str
    categoria_id: int
    categoria: str
    direccion: str
    fecha: str
    platos: list[PlatoResponse]  #lista los platos de un negocio

    class Config:
        from_attributes = True


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    telefono: str
    estado_id: int
    estado: str
    perfil_id: int
    perfil: str
    fecha: str 

    class Config:
        from_attributes = True



class LoginResponse(BaseModel):
    estado: str
    mensaje: str
    data: dict | None = None 
