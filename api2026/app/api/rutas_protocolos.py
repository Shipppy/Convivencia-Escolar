from fastapi import APIRouter

from app.models.protocolo import Protocolo
from app.repositories.protocolo_repo import ProtocoloRepository

router = APIRouter(prefix="/protocolos", tags=["Protocolo"])
repo = ProtocoloRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{protocolo_id}")
def obtener(protocolo_id: int):
    return repo.obtener_por_id(protocolo_id)


@router.post("/", status_code=201)
def crear(datos: Protocolo):
    registro = repo.crear(datos)
    return {"mensaje": "Paso del protocolo registrado correctamente", "registro": registro}


@router.put("/{protocolo_id}")
def actualizar(protocolo_id: int, datos: Protocolo):
    registro = repo.actualizar(protocolo_id, datos)
    return {"mensaje": "Paso del protocolo actualizado correctamente", "registro": registro}


@router.delete("/{protocolo_id}")
def eliminar(protocolo_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(protocolo_id)
    return {"mensaje": "Paso del protocolo desactivado correctamente"}
