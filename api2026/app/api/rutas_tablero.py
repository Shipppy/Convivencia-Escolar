from typing import Optional

from fastapi import APIRouter, HTTPException

from app.repositories.base import ejecutar

router = APIRouter(prefix="/tablero", tags=["Tablero"])


def _filtros(fecha_desde, fecha_hasta, id_nivel, id_tipo):
    """Condiciones sobre incidentes (alias i). Todos los filtros son opcionales."""
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise HTTPException(422, "La fecha 'desde' no puede ser posterior a la fecha 'hasta'")
    cond, params = ["i.estado <> 'inactivo'"], []
    if fecha_desde:
        cond.append("i.fecha >= %s"); params.append(fecha_desde)
    if fecha_hasta:
        cond.append("i.fecha <= %s"); params.append(fecha_hasta)
    if id_nivel:
        cond.append("i.id_nivel = %s"); params.append(id_nivel)
    if id_tipo:
        cond.append("i.id_tipo = %s"); params.append(id_tipo)
    return " AND ".join(cond), tuple(params)


@router.get("/datos")
def datos_tablero(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    id_nivel: Optional[int] = None,
    id_tipo: Optional[int] = None,
):
    """Indicadores y series para el tablero. Acepta fecha_desde, fecha_hasta, id_nivel e id_tipo."""
    donde, p = _filtros(fecha_desde, fecha_hasta, id_nivel, id_tipo)
    acc = "consultar el tablero"

    ind = ejecutar(
        f"""
        SELECT
          (SELECT COUNT(*) FROM incidentes i WHERE {donde}) AS incidentes,
          (SELECT COUNT(*) FROM incidentes i
             INNER JOIN nivel_protocolo np ON np.id_nivel = i.id_nivel
             WHERE {donde} AND np.nombre IN ('Grave', 'Muy grave')) AS graves_muy_graves,
          (SELECT COUNT(*) FROM compromisos c
             INNER JOIN incidentes i ON i.id_incidente = c.id_incidente
             WHERE {donde} AND c.estado = 'activo') AS compromisos_activos,
          (SELECT COUNT(*) FROM compromisos c
             INNER JOIN incidentes i ON i.id_incidente = c.id_incidente
             WHERE {donde} AND c.estado = 'cumplido') AS compromisos_cumplidos,
          (SELECT COUNT(*) FROM compromisos c
             INNER JOIN incidentes i ON i.id_incidente = c.id_incidente
             WHERE {donde} AND c.estado <> 'inactivo') AS compromisos_total,
          (SELECT ROUND(AVG(s.nivel_cumplimiento), 1) FROM seguimientos_compromisos s
             INNER JOIN compromisos c ON c.id_compromiso = s.id_compromiso
             INNER JOIN incidentes i ON i.id_incidente = c.id_incidente
             WHERE {donde} AND s.estado <> 'inactivo') AS cumplimiento_promedio
        """,
        p * 6,
        accion=acc,
    )
    if ind["cumplimiento_promedio"] is not None:
        ind["cumplimiento_promedio"] = float(ind["cumplimiento_promedio"])

    por_tipo = ejecutar(
        f"""SELECT ti.nombre AS etiqueta, COUNT(*) AS total FROM incidentes i
            INNER JOIN tipos_incidente ti ON ti.id_tipo = i.id_tipo
            WHERE {donde} GROUP BY ti.nombre ORDER BY ti.nombre""",
        p, accion=acc, fetch="all")
    por_nivel = ejecutar(
        f"""SELECT np.nombre AS etiqueta, COUNT(*) AS total FROM incidentes i
            INNER JOIN nivel_protocolo np ON np.id_nivel = i.id_nivel
            WHERE {donde} GROUP BY np.nombre, np.id_nivel ORDER BY np.id_nivel""",
        p, accion=acc, fetch="all")
    por_estado = ejecutar(
        f"""SELECT i.estado AS etiqueta, COUNT(*) AS total FROM incidentes i
            WHERE {donde} GROUP BY i.estado ORDER BY i.estado""",
        p, accion=acc, fetch="all")
    por_mes = ejecutar(
        f"""SELECT to_char(i.fecha, 'YYYY-MM') AS etiqueta, COUNT(*) AS total FROM incidentes i
            WHERE {donde} GROUP BY 1 ORDER BY 1""",
        p, accion=acc, fetch="all")
    comp_estado = ejecutar(
        f"""SELECT c.estado AS etiqueta, COUNT(*) AS total FROM compromisos c
            INNER JOIN incidentes i ON i.id_incidente = c.id_incidente
            WHERE {donde} AND c.estado <> 'inactivo' GROUP BY c.estado ORDER BY c.estado""",
        p, accion=acc, fetch="all")

    return {
        "indicadores": ind,
        "por_tipo": por_tipo,
        "por_nivel": por_nivel,
        "por_estado": por_estado,
        "por_mes": por_mes,
        "compromisos_por_estado": comp_estado,
    }
