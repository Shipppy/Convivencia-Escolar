from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class TipoIncidente(ModeloBase):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    nivel_gravedad: Optional[int] = Field(default=None, ge=1, le=5)
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
