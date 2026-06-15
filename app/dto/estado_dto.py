from pydantic import BaseModel, model_validator, field_validator

class EstadoDTO(BaseModel):
    nombre: str
    descripcion: str

    @model_validator(mode="after")
    def validate_name(self):
        if not self.nombre.strip():
            raise ValueError("El nombre del estado no puede estar vacío.")

        if not self.descripcion.strip():
            raise ValueError("La descripción del estado no puede estar vacía.")

        return self