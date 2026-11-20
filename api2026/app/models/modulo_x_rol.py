from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class ModuloXRol(ModeloBase):
    id_rol: int
    id_modulo: int
    puede_ver: Optional[bool] = None
    puede_crear: Optional[bool] = None
    puede_editar: Optional[bool] = None
    puede_eliminar: Optional[bool] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
