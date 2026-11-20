from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Psicorientador(ModeloBase):
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo: Optional[str] = Field(default=None, max_length=100)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    id_miembro: Optional[int] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
