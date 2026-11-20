from fastapi import APIRouter

from app.models.nivel import Nivel
from app.repositories.nivel_repo import NivelRepository

router = APIRouter(prefix="/niveles", tags=["Niveles de protocolo"])
repo = NivelRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{nivel_id}")
def obtener(nivel_id: int):
    return repo.obtener_por_id(nivel_id)


@router.post("/", status_code=201)
def crear(datos: Nivel):
    registro = repo.crear(datos)
    return {"mensaje": "Nivel registrado correctamente", "registro": registro}


@router.put("/{nivel_id}")
def actualizar(nivel_id: int, datos: Nivel):
    registro = repo.actualizar(nivel_id, datos)
    return {"mensaje": "Nivel actualizado correctamente", "registro": registro}


@router.delete("/{nivel_id}")
def eliminar(nivel_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(nivel_id)
    return {"mensaje": "Nivel desactivado correctamente"}
