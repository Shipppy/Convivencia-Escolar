from fastapi import APIRouter, Request

from app.repositories.base import ejecutar
from app.repositories.incidente_repo import IncidenteRepository

router = APIRouter(prefix="/dashboard", tags=["Inicio"])


@router.get("/resumen")
def resumen(request: Request):
    """Totales y últimos incidentes para Inicio. Un docente solo ve las cifras de sus incidentes."""
    claims = request.state.usuario
    es_docente = str(claims.get("rol", "")).strip().casefold() == "docente"
    filtro, params = "", ()
    if es_docente:
        filtro, params = " AND id_docente = %s", (claims.get("id_docente"),)

    totales = ejecutar(
        f"""
        SELECT
          (SELECT COUNT(*) FROM incidentes WHERE estado <> 'inactivo'{filtro}) AS incidentes,
          (SELECT COUNT(*) FROM incidentes WHERE estado = 'reportado'{filtro}) AS reportados,
          (SELECT COUNT(*) FROM incidentes WHERE estado = 'en_proceso'{filtro}) AS en_proceso,
          (SELECT COUNT(*) FROM incidentes WHERE estado = 'resuelto'{filtro}) AS resueltos,
          (SELECT COUNT(*) FROM estudiantes WHERE estado = 'activo') AS estudiantes_activos,
          (SELECT COUNT(*) FROM compromisos WHERE estado = 'activo') AS compromisos_activos
        """,
        params * 4,
        accion="consultar el resumen",
    )
    repo = IncidenteRepository()
    ultimos = (
        repo.obtener_todos(id_docente=claims.get("id_docente"), solo_del_docente=True)
        if es_docente
        else repo.obtener_todos()
    )[:5]
    return {"totales": totales, "ultimos_incidentes": ultimos}
