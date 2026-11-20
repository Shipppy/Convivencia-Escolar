from datetime import date
from typing import Optional

from pydantic import Field

from app.models.base import ModeloBase


class Usuario(ModeloBase):
    nombre_usuario: str = Field(max_length=50)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    correo: str = Field(max_length=100)
    contrasena: Optional[str] = None
    id_rol: int
    id_docente: Optional[int] = None
    id_psicorientador: Optional[int] = None
    estado: Optional[str] = Field(default=None, pattern="^(activo|inactivo)$")
