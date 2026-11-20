from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class RolRepository(BaseRepository):
    tabla = "roles"
    pk = "id_rol"
    nombre_singular = "rol"
    columnas = ['nombre', 'descripcion', 'estado']
    ORDEN = "t.id_rol"
