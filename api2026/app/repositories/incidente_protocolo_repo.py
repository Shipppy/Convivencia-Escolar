from datetime import date, timedelta

from fastapi import HTTPException

from app.repositories.base import BaseRepository


class IncidenteProtocoloRepository(BaseRepository):
    tabla = "incidentes_protocolo"
    pk = "id_aplicacion"
    nombre_singular = "aplicación del protocolo"
    columnas = [
        "id_incidente", "id_protocolo", "id_miembro",
        "fecha_inicio", "fecha_limite", "fecha_finalizacion", "estado",
    ]
    SQL_SELECT = """
        SELECT t.*,
               i.descripcion AS incidente,
               p.nombre AS protocolo,
               p.paso AS paso,
               np.nombre AS nivel,
               COALESCE(co.nombre, 'Sin asignar') AS miembro
        FROM incidentes_protocolo t
        INNER JOIN incidentes i ON i.id_incidente = t.id_incidente
        INNER JOIN protocolo p ON p.id_protocolo = t.id_protocolo
        INNER JOIN nivel_protocolo np ON np.id_nivel = p.id_nivel
        LEFT JOIN comites_orientacion co ON co.id_miembro = t.id_miembro
    """
    ORDEN = "t.fecha_inicio DESC, t.id_aplicacion DESC"

    def preparar(self, datos, id_registro=None):
        inicio, limite = datos.get("fecha_inicio"), datos.get("fecha_limite")
        if inicio and limite and limite < inicio:
            raise HTTPException(422, "La fecha límite no puede ser anterior a la fecha de inicio")
        # Al crear, si no hay fecha límite se calcula con los días máximos del paso.
        if id_registro is None and not limite and datos.get("id_protocolo"):
            fila = self.ejecutar(
                "SELECT dias_maximos FROM protocolo WHERE id_protocolo = %s",
                (datos["id_protocolo"],),
                accion="consultar el paso del protocolo",
            )
            if fila and fila["dias_maximos"] is not None:
                base = inicio or date.today()
                datos["fecha_limite"] = base + timedelta(days=fila["dias_maximos"])
        return datos
