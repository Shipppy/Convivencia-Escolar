from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Estudiante(ModeloBase):
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    grado: Optional[str] = Field(default=None, max_length=20)
    curso: Optional[str] = Field(default=None, max_length=10)
    acudiente: Optional[str] = Field(default=None, max_length=150)
    telefono_acudiente: Optional[str] = Field(default=None, max_length=20)
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
