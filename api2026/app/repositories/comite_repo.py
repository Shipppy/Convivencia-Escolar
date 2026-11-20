from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class ComiteRepository(BaseRepository):
    tabla = "comites_orientacion"
    pk = "id_miembro"
    nombre_singular = "miembro del comité"
    columnas = ['nombre', 'rol', 'departamento', 'telefono', 'id_docente', 'estado']
    SQL_SELECT = """
        SELECT t.*, COALESCE(d.nombre || ' ' || d.apellido, 'Sin docente') AS docente
        FROM comites_orientacion t
        LEFT JOIN docentes d ON d.id_docente = t.id_docente
    """
    ORDEN = "t.id_miembro"
