from fastapi import APIRouter

from app.models.estudiante import Estudiante
from app.repositories.estudiante_repo import EstudianteRepository

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])
repo = EstudianteRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{estudiante_id}")
def obtener(estudiante_id: int):
    return repo.obtener_por_id(estudiante_id)


@router.post("/", status_code=201)
def crear(datos: Estudiante):
    registro = repo.crear(datos)
    return {"mensaje": "Estudiante registrado correctamente", "registro": registro}


@router.put("/{estudiante_id}")
def actualizar(estudiante_id: int, datos: Estudiante):
    registro = repo.actualizar(estudiante_id, datos)
    return {"mensaje": "Estudiante actualizado correctamente", "registro": registro}


@router.delete("/{estudiante_id}")
def eliminar(estudiante_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(estudiante_id)
    return {"mensaje": "Estudiante desactivado correctamente"}
