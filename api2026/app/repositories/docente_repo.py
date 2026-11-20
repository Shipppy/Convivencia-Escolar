from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class DocenteRepository(BaseRepository):
    tabla = "docentes"
    pk = "id_docente"
    nombre_singular = "docente"
    columnas = ['nombre', 'apellido', 'departamento', 'telefono', 'correo', 'estado']
    ORDEN = "t.apellido, t.nombre"
