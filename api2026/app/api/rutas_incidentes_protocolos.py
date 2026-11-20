from fastapi import APIRouter

from app.models.incidente_protocolo import IncidenteProtocolo
from app.repositories.incidente_protocolo_repo import IncidenteProtocoloRepository

router = APIRouter(prefix="/incidentes-protocolos", tags=["Aplicación del protocolo"])
repo = IncidenteProtocoloRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{aplicacion_id}")
def obtener(aplicacion_id: int):
    return repo.obtener_por_id(aplicacion_id)


@router.post("/", status_code=201)
def crear(datos: IncidenteProtocolo):
    registro = repo.crear(datos)
    return {"mensaje": "Aplicación del protocolo registrado correctamente", "registro": registro}


@router.put("/{aplicacion_id}")
def actualizar(aplicacion_id: int, datos: IncidenteProtocolo):
    registro = repo.actualizar(aplicacion_id, datos)
    return {"mensaje": "Aplicación del protocolo actualizado correctamente", "registro": registro}


@router.delete("/{aplicacion_id}")
def eliminar(aplicacion_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(aplicacion_id)
    return {"mensaje": "Aplicación del protocolo desactivado correctamente"}
