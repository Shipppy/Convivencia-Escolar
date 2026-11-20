from fastapi import APIRouter

from app.models.modulo import Modulo
from app.repositories.modulo_repo import ModuloRepository

router = APIRouter(prefix="/modulos", tags=["Módulos"])
repo = ModuloRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{modulo_id}")
def obtener(modulo_id: int):
    return repo.obtener_por_id(modulo_id)


@router.post("/", status_code=201)
def crear(datos: Modulo):
    registro = repo.crear(datos)
    return {"mensaje": "Módulo registrado correctamente", "registro": registro}


@router.put("/{modulo_id}")
def actualizar(modulo_id: int, datos: Modulo):
    registro = repo.actualizar(modulo_id, datos)
    return {"mensaje": "Módulo actualizado correctamente", "registro": registro}


@router.delete("/{modulo_id}")
def eliminar(modulo_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(modulo_id)
    return {"mensaje": "Módulo desactivado correctamente"}
