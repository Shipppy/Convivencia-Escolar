from fastapi import APIRouter

from app.models.rol import Rol
from app.repositories.rol_repo import RolRepository

router = APIRouter(prefix="/roles", tags=["Roles"])
repo = RolRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{rol_id}")
def obtener(rol_id: int):
    return repo.obtener_por_id(rol_id)


@router.post("/", status_code=201)
def crear(datos: Rol):
    registro = repo.crear(datos)
    return {"mensaje": "Rol registrado correctamente", "registro": registro}


@router.put("/{rol_id}")
def actualizar(rol_id: int, datos: Rol):
    registro = repo.actualizar(rol_id, datos)
    return {"mensaje": "Rol actualizado correctamente", "registro": registro}


@router.delete("/{rol_id}")
def eliminar(rol_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(rol_id)
    return {"mensaje": "Rol desactivado correctamente"}
