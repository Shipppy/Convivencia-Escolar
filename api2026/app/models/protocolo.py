from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Protocolo(ModeloBase):
    nombre: str = Field(max_length=150)
    paso: int = Field(ge=1)
    descripcion: str = Field(min_length=1)
    responsable: Optional[str] = Field(default=None, max_length=100)
    dias_maximos: Optional[int] = Field(default=None, ge=0)
    id_nivel: int
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
