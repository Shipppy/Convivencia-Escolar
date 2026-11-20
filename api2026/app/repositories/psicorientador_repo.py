from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class PsicorientadorRepository(BaseRepository):
    tabla = "psicorientadores"
    pk = "id_psicorientador"
    nombre_singular = "psicorientador"
    columnas = ['nombre', 'apellido', 'telefono', 'correo', 'especialidad', 'id_miembro', 'estado']
    SQL_SELECT = """
        SELECT t.*, COALESCE(co.nombre, 'Sin miembro') AS miembro_comite
        FROM psicorientadores t
        LEFT JOIN comites_orientacion co ON co.id_miembro = t.id_miembro
    """
    ORDEN = "t.apellido, t.nombre"
