from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class NivelRepository(BaseRepository):
    tabla = "nivel_protocolo"
    pk = "id_nivel"
    nombre_singular = "nivel"
    columnas = ['nombre', 'descripcion', 'estado']
    ORDEN = "t.id_nivel"
