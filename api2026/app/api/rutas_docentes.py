from fastapi import APIRouter

from app.models.docente import Docente
from app.repositories.docente_repo import DocenteRepository

router = APIRouter(prefix="/docentes", tags=["Docentes"])
repo = DocenteRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{docente_id}")
def obtener(docente_id: int):
    return repo.obtener_por_id(docente_id)


@router.post("/", status_code=201)
def crear(datos: Docente):
    registro = repo.crear(datos)
    return {"mensaje": "Docente registrado correctamente", "registro": registro}


@router.put("/{docente_id}")
def actualizar(docente_id: int, datos: Docente):
    registro = repo.actualizar(docente_id, datos)
    return {"mensaje": "Docente actualizado correctamente", "registro": registro}


@router.delete("/{docente_id}")
def eliminar(docente_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(docente_id)
    return {"mensaje": "Docente desactivado correctamente"}
