from fastapi import APIRouter

from app.models.psicorientador import Psicorientador
from app.repositories.psicorientador_repo import PsicorientadorRepository

router = APIRouter(prefix="/psicorientadores", tags=["Psicorientadores"])
repo = PsicorientadorRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{psicorientador_id}")
def obtener(psicorientador_id: int):
    return repo.obtener_por_id(psicorientador_id)


@router.post("/", status_code=201)
def crear(datos: Psicorientador):
    registro = repo.crear(datos)
    return {"mensaje": "Psicorientador registrado correctamente", "registro": registro}


@router.put("/{psicorientador_id}")
def actualizar(psicorientador_id: int, datos: Psicorientador):
    registro = repo.actualizar(psicorientador_id, datos)
    return {"mensaje": "Psicorientador actualizado correctamente", "registro": registro}


@router.delete("/{psicorientador_id}")
def eliminar(psicorientador_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(psicorientador_id)
    return {"mensaje": "Psicorientador desactivado correctamente"}
