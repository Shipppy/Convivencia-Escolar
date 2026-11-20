from fastapi import APIRouter

from app.models.modulo_x_rol import ModuloXRol
from app.repositories.modulo_x_rol_repo import ModuloXRolRepository

router = APIRouter(prefix="/modulos-x-rol", tags=["Permisos por rol"])
repo = ModuloXRolRepository()


@router.get("/")
def listar(todos: bool = False):
    return repo.obtener_todos(incluir_inactivos=todos)


# /rol/{id} va ANTES de /{id} para que no se confunda
@router.get("/rol/{id_rol}")
def modulos_por_rol(id_rol: int):
    """Módulos (con permisos) que puede ver un rol. Cada rol solo consulta el suyo."""
    return repo.modulos_del_rol(id_rol)


@router.get("/{permiso_id}")
def obtener(permiso_id: int):
    return repo.obtener_por_id(permiso_id)


@router.post("/", status_code=201)
def crear(datos: ModuloXRol):
    registro = repo.crear(datos)
    return {"mensaje": "Permiso guardado correctamente", "registro": registro}


@router.put("/{permiso_id}")
def actualizar(permiso_id: int, datos: ModuloXRol):
    registro = repo.actualizar(permiso_id, datos)
    return {"mensaje": "Permiso actualizado correctamente", "registro": registro}


@router.delete("/{permiso_id}")
def eliminar(permiso_id: int):
    repo.eliminar(permiso_id)
    return {"mensaje": "Permiso desactivado correctamente"}
