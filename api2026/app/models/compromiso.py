from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Compromiso(ModeloBase):
    id_incidente: int
    id_estudiante: int
    descripcion: str = Field(min_length=1)
    fecha: Optional[date] = None
    fecha_limite: Optional[date] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|cumplido|incumplido|inactivo)$")
    asignado_por: Optional[int] = None
