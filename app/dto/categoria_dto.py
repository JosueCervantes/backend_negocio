from pydantic import BaseModel, model_validator, field_validator

class CategoriaDTO(BaseModel):
    nombre: str

    @model_validator(mode="after")
    def validate_name(self):
        if not self.nombre.strip():
            raise ValueError("El nombre de la categoria no puede estar vacío.")
        return self