import datetime
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Estado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    usuarios: list["Usuario"] = Relationship(back_populates="estado") #lista de usuarios que pertenecen a este estado
    negocios: list["Negocio"] = Relationship(back_populates="estado") #lista de negocios que pertenecen a este estado

class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    negocios: list["Negocio"] = Relationship(back_populates="categoria") #lista de negocios que pertenecen a esta categoria

class Perfil(SQLModel, table=True): #si es admin o cliente
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    usuarios: list["Usuario"] = Relationship(back_populates="perfil") #lista de usuarios que pertenecen a este perfil

class Usuario(SQLModel, table=True): 
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    email: str
    password: str
    token: str
    perfil_id: int | None = Field(default=None, foreign_key="perfil.id")
    perfil: Optional[Perfil] = Relationship(back_populates="usuarios") #relacion con perfil, un usuario pertenece a un perfil, y un perfil tiene muchos usuarios

    estado_id: int | None = Field(default=None, foreign_key="estado.id")
    estado: Optional[Estado] = Relationship(back_populates="usuarios") #relacion con estado, un usuario pertenece a un estado, y un estado tiene muchos usuarios

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    negocios: list["Negocio"] = Relationship(back_populates="usuario") #lista de negocios que pertenecen a este usuario

class Negocio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    correo: str
    telefono: str
    descripcion: str
    logo: str
    mapa: str
    estado_id: int | None = Field(default=None, foreign_key="estado.id")
    estado: Optional[Estado] = Relationship(back_populates="negocios") #relacion con estado, un negocio pertenece a un estado, y un estado tiene muchos negocios

    categoria_id: int | None = Field(default=None, foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="negocios") #relacion con categoria, un negocio pertenece a una categoria, y una categoria tiene muchos negocios

    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="negocios") #relacion con usuario, un negocio pertenece a un usuario, y un usuario tiene muchos negocios

    platos: list["Platos"] = Relationship(back_populates="negocio")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PlatosCategoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    slug: str

    # Relación inversa con Platos
    platos: list["Platos"] = Relationship(back_populates="platoscategoria")


class Platos(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    ingredientes: str
    precio: int
    foto: str

    # Clave foránea hacia Negocio
    negocio_id: int | None = Field(default=None, foreign_key="negocio.id")
    negocio: Optional[Negocio] = Relationship(back_populates="platos")

    # Clave foránea hacia PlatosCategoria
    platoscategoria_id: int | None = Field(default=None, foreign_key="platoscategoria.id")
    platoscategoria: Optional[PlatosCategoria] = Relationship(back_populates="platos")