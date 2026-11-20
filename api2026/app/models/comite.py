from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Comite(ModeloBase):
    nombre: str = Field(max_length=100)
    rol: str = Field(max_length=50)
    departamento: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    id_docente: Optional[int] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
