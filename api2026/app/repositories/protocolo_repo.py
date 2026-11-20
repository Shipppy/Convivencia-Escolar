from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class ProtocoloRepository(BaseRepository):
    tabla = "protocolo"
    pk = "id_protocolo"
    nombre_singular = "paso del protocolo"
    columnas = ['nombre', 'paso', 'descripcion', 'responsable', 'dias_maximos', 'id_nivel', 'estado']
    SQL_SELECT = """
        SELECT t.*, np.nombre AS nivel
        FROM protocolo t
        INNER JOIN nivel_protocolo np ON np.id_nivel = t.id_nivel
    """
    ORDEN = "t.id_nivel, t.paso"
