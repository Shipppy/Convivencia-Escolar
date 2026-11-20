from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class EstudianteRepository(BaseRepository):
    tabla = "estudiantes"
    pk = "id_estudiante"
    nombre_singular = "estudiante"
    columnas = ['nombre', 'apellido', 'grado', 'curso', 'acudiente', 'telefono_acudiente', 'estado']
    ORDEN = "t.apellido, t.nombre"
