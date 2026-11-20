from fastapi import HTTPException

from app.repositories.base import BaseRepository


class IncidenteRepository(BaseRepository):
    tabla = "incidentes"
    pk = "id_incidente"
    nombre_singular = "incidente"
    columnas = [
        "id_reportante", "id_reportado", "id_docente", "id_tipo", "id_nivel",
        "fecha", "lugar", "descripcion", "gravedad", "estado", "responsable",
    ]
    SQL_SELECT = """
        SELECT t.*,
               er.nombre || ' ' || er.apellido AS reportante,
               ed.nombre || ' ' || ed.apellido AS reportado,
               COALESCE(d.nombre || ' ' || d.apellido, 'Sin docente') AS docente,
               ti.nombre AS tipo_incidente,
               np.nombre AS nivel,
               COALESCE(co.nombre, 'Sin asignar') AS responsable_nombre
        FROM incidentes t
        INNER JOIN estudiantes er ON er.id_estudiante = t.id_reportante
        INNER JOIN estudiantes ed ON ed.id_estudiante = t.id_reportado
        INNER JOIN tipos_incidente ti ON ti.id_tipo = t.id_tipo
        INNER JOIN nivel_protocolo np ON np.id_nivel = t.id_nivel
        LEFT JOIN docentes d ON d.id_docente = t.id_docente
        LEFT JOIN comites_orientacion co ON co.id_miembro = t.responsable
    """
    ORDEN = "t.fecha DESC, t.id_incidente DESC"

    def preparar(self, datos, id_registro=None):
        if datos.get("id_reportante") is not None and datos.get("id_reportante") == datos.get("id_reportado"):
            raise HTTPException(422, "El estudiante que reporta y el reportado deben ser diferentes")
        return datos

    def obtener_todos(self, incluir_inactivos=False, id_docente=None, solo_del_docente=False):
        """Un docente solo ve los incidentes que él mismo reportó."""
        if solo_del_docente:
            return super().obtener_todos(incluir_inactivos, "t.id_docente = %s", (id_docente,))
        return super().obtener_todos(incluir_inactivos)
