from fastapi import APIRouter

from app.models.comite import Comite
from app.repositories.comite_repo import ComiteRepository

router = APIRouter(prefix="/comite", tags=["Comité de orientación"])
repo = ComiteRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{miembro_id}")
def obtener(miembro_id: int):
    return repo.obtener_por_id(miembro_id)


@router.post("/", status_code=201)
def crear(datos: Comite):
    registro = repo.crear(datos)
    return {"mensaje": "Miembro del comité registrado correctamente", "registro": registro}


@router.put("/{miembro_id}")
def actualizar(miembro_id: int, datos: Comite):
    registro = repo.actualizar(miembro_id, datos)
    return {"mensaje": "Miembro del comité actualizado correctamente", "registro": registro}


@router.delete("/{miembro_id}")
def eliminar(miembro_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(miembro_id)
    return {"mensaje": "Miembro del comité desactivado correctamente"}
