from fastapi import APIRouter

from app.models.seguimiento import Seguimiento
from app.repositories.seguimiento_repo import SeguimientoRepository

router = APIRouter(prefix="/seguimientos", tags=["Seguimientos"])
repo = SeguimientoRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{seguimiento_id}")
def obtener(seguimiento_id: int):
    return repo.obtener_por_id(seguimiento_id)


@router.post("/", status_code=201)
def crear(datos: Seguimiento):
    registro = repo.crear(datos)
    return {"mensaje": "Seguimiento registrado correctamente", "registro": registro}


@router.put("/{seguimiento_id}")
def actualizar(seguimiento_id: int, datos: Seguimiento):
    registro = repo.actualizar(seguimiento_id, datos)
    return {"mensaje": "Seguimiento actualizado correctamente", "registro": registro}


@router.delete("/{seguimiento_id}")
def eliminar(seguimiento_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(seguimiento_id)
    return {"mensaje": "Seguimiento desactivado correctamente"}
