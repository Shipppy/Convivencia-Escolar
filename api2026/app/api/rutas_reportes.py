import re
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from app.core import reportes
from app.core.correo import enviar_correo

router = APIRouter(prefix="/reportes", tags=["Reportes"])


class EnvioCorreo(BaseModel):
    correo: str
    formato: str = "pdf"


def _autor(request: Request):
    return request.state.usuario.get("nombre_usuario", "usuario")


@router.get("/tipos")
def tipos():
    return reportes.tipos_disponibles()


# /{tipo}/exportar va antes que /{tipo} (rutas mas especificas primero)
@router.get("/{tipo}/exportar")
def exportar(tipo: str, request: Request, formato: str = "pdf",
             fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None,
             id_tipo: Optional[int] = None, id_nivel: Optional[int] = None, estado: Optional[str] = None):
    """Descarga el reporte en PDF o Excel con los mismos filtros."""
    datos = reportes.consultar(tipo, fecha_desde, fecha_hasta, id_tipo, id_nivel, estado)
    contenido, nombre, mime = reportes.generar(datos, formato, _autor(request))
    return Response(content=contenido, media_type=mime,
                    headers={"Content-Disposition": f'attachment; filename="{nombre}"'})


@router.get("/{tipo}")
def ver(tipo: str, fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None,
        id_tipo: Optional[int] = None, id_nivel: Optional[int] = None, estado: Optional[str] = None):
    """Datos del reporte en pantalla (sin IDs), con los filtros elegidos."""
    return reportes.consultar(tipo, fecha_desde, fecha_hasta, id_tipo, id_nivel, estado)


@router.post("/{tipo}/enviar")
def enviar(tipo: str, envio: EnvioCorreo, request: Request,
           fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None,
           id_tipo: Optional[int] = None, id_nivel: Optional[int] = None, estado: Optional[str] = None):
    """Genera el reporte y lo envía como adjunto al correo indicado."""
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", envio.correo.strip()):
        raise HTTPException(422, "El correo de destino no es válido")
    datos = reportes.consultar(tipo, fecha_desde, fecha_hasta, id_tipo, id_nivel, estado)
    contenido, nombre, mime = reportes.generar(datos, envio.formato, _autor(request))
    enviar_correo(envio.correo.strip(), datos["titulo"],
                  f"Adjunto: {datos['titulo']}.\nFiltros: {datos['filtros']}\nTotal: {datos['total']} registro(s).",
                  nombre, contenido, mime)
    return {"mensaje": f"Reporte enviado a {envio.correo.strip()}"}
