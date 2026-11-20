from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class IncidenteProtocolo(ModeloBase):
    id_incidente: int
    id_protocolo: int
    id_miembro: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None
    fecha_finalizacion: Optional[date] = None
    estado: Optional[str] = Field(default=None, pattern="^(pendiente|en_proceso|completado|inactivo)$")
