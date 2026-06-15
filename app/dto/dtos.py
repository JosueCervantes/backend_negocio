from pydantic import BaseModel, model_validator, field_validator
from typing import Optional

class User(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str]

    @model_validator(mode="after")
    def validate_name(self):
        if not self.name or len(self.name) < 3:
            raise ValueError("Name must be at least 3 characters long")
        return self

    @model_validator(mode="after")
    def validate_email(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email address")
        return self

    @model_validator(mode="after")
    def validate_password(self):
        if not self.password or len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return self

    @field_validator("phone")
    #cls representa la clase UserCreate
    def validate_phone(cls, v):
        if v and len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits long")
        return v
class UserCreate(User):
    pass