from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Docente(ModeloBase):
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    departamento: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
