from fastapi import HTTPException  # noqa: F401

from app.repositories.base import BaseRepository


class SeguimientoRepository(BaseRepository):
    tabla = "seguimientos_compromisos"
    pk = "id_seguimiento"
    nombre_singular = "seguimiento"
    columnas = ['id_compromiso', 'fecha', 'observaciones', 'nivel_cumplimiento', 'realizado_por', 'proximo_seguimiento', 'estado']
    SQL_SELECT = """
        SELECT t.*,
               c.descripcion AS compromiso,
               COALESCE(co.nombre, 'Sin asignar') AS realizado_por_nombre
        FROM seguimientos_compromisos t
        INNER JOIN compromisos c ON c.id_compromiso = t.id_compromiso
        LEFT JOIN comites_orientacion co ON co.id_miembro = t.realizado_por
    """
    ORDEN = "t.fecha DESC, t.id_seguimiento DESC"

    def preparar(self, datos, id_registro=None):
        f, prox = datos.get("fecha"), datos.get("proximo_seguimiento")
        if f and prox and prox < f:
            raise HTTPException(422, "El próximo seguimiento no puede ser anterior a la fecha del seguimiento")
        return datos
