from fastapi import APIRouter

from app.models.compromiso import Compromiso
from app.repositories.compromiso_repo import CompromisoRepository

router = APIRouter(prefix="/compromisos", tags=["Compromisos"])
repo = CompromisoRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{compromiso_id}")
def obtener(compromiso_id: int):
    return repo.obtener_por_id(compromiso_id)


@router.post("/", status_code=201)
def crear(datos: Compromiso):
    registro = repo.crear(datos)
    return {"mensaje": "Compromiso registrado correctamente", "registro": registro}


@router.put("/{compromiso_id}")
def actualizar(compromiso_id: int, datos: Compromiso):
    registro = repo.actualizar(compromiso_id, datos)
    return {"mensaje": "Compromiso actualizado correctamente", "registro": registro}


@router.delete("/{compromiso_id}")
def eliminar(compromiso_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(compromiso_id)
    return {"mensaje": "Compromiso desactivado correctamente"}
