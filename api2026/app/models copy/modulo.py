from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Modulo(ModeloBase):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
