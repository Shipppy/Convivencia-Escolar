from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class ModuloRepository(BaseRepository):
    tabla = "modulos"
    pk = "id_modulo"
    nombre_singular = "módulo"
    columnas = ['nombre', 'descripcion', 'estado']
    ORDEN = "t.id_modulo"
