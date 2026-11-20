from fastapi import APIRouter, Request

from app.repositories.base import ejecutar

router = APIRouter(prefix="/guia", tags=["Guía"])


@router.get("/")
def obtener_guia(request: Request):
    """Guía de uso de los módulos que el rol del usuario puede ver (se muestra en Inicio)."""
    id_rol = request.state.usuario["id_rol"]
    return ejecutar(
        """
        SELECT g.id_guia, g.titulo, g.descripcion, g.instrucciones, m.nombre AS modulo
        FROM guia g
        INNER JOIN modulos m ON m.id_modulo = g.id_modulo
        INNER JOIN modulos_x_rol mxr ON mxr.id_modulo = m.id_modulo
        WHERE mxr.id_rol = %s AND mxr.puede_ver = TRUE AND mxr.estado = 'activo'
          AND g.estado = 'activo' AND m.estado = 'activo'
        ORDER BY m.id_modulo
        """,
        (id_rol,),
        accion="consultar la guía",
        fetch="all",
    )
