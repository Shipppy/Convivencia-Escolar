from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Incidente(ModeloBase):
    id_reportante: int
    id_reportado: int
    id_docente: Optional[int] = None
    id_tipo: int
    id_nivel: int
    fecha: date
    lugar: Optional[str] = Field(default=None, max_length=150)
    descripcion: str = Field(min_length=1)
    gravedad: Optional[int] = Field(default=None, ge=1, le=5)
    estado: Optional[str] = Field(default=None, pattern="^(reportado|en_proceso|resuelto|inactivo)$")
    responsable: Optional[int] = None
