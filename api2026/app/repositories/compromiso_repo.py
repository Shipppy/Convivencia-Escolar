from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class CompromisoRepository(BaseRepository):
    tabla = "compromisos"
    pk = "id_compromiso"
    nombre_singular = "compromiso"
    columnas = ['id_incidente', 'id_estudiante', 'descripcion', 'fecha', 'fecha_limite', 'estado', 'asignado_por']
    SQL_SELECT = """
        SELECT t.*,
               e.nombre || ' ' || e.apellido AS estudiante,
               i.descripcion AS incidente,
               COALESCE(co.nombre, 'Sin asignar') AS asignado_por_nombre
        FROM compromisos t
        INNER JOIN estudiantes e ON e.id_estudiante = t.id_estudiante
        INNER JOIN incidentes i ON i.id_incidente = t.id_incidente
        LEFT JOIN comites_orientacion co ON co.id_miembro = t.asignado_por
    """
    ORDEN = "t.fecha DESC, t.id_compromiso DESC"

    def preparar(self, datos, id_registro=None):
        f, lim = datos.get("fecha"), datos.get("fecha_limite")
        if f and lim and lim < f:
            raise HTTPException(422, "La fecha límite no puede ser anterior a la fecha del compromiso")
        return datos
