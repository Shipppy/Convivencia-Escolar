from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Seguimiento(ModeloBase):
    id_compromiso: int
    fecha: date
    observaciones: Optional[str] = None
    nivel_cumplimiento: Optional[int] = Field(default=None, ge=1, le=5)
    realizado_por: Optional[int] = None
    proximo_seguimiento: Optional[date] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
