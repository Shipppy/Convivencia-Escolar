from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class TipoIncidenteRepository(BaseRepository):
    tabla = "tipos_incidente"
    pk = "id_tipo"
    nombre_singular = "tipo de incidente"
    columnas = ['nombre', 'descripcion', 'nivel_gravedad', 'estado']
    ORDEN = "t.id_tipo"
