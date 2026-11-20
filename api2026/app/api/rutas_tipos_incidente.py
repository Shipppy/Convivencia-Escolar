from fastapi import APIRouter

from app.models.tipo_incidente import TipoIncidente
from app.repositories.tipo_incidente_repo import TipoIncidenteRepository

router = APIRouter(prefix="/tipos-incidente", tags=["Tipos de incidente"])
repo = TipoIncidenteRepository()


@router.get("/")
def listar(todos: bool = False):
    """Lista los registros activos. Con ?todos=true incluye los inactivos."""
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{tipo_id}")
def obtener(tipo_id: int):
    return repo.obtener_por_id(tipo_id)


@router.post("/", status_code=201)
def crear(datos: TipoIncidente):
    registro = repo.crear(datos)
    return {"mensaje": "Tipo de incidente registrado correctamente", "registro": registro}


@router.put("/{tipo_id}")
def actualizar(tipo_id: int, datos: TipoIncidente):
    registro = repo.actualizar(tipo_id, datos)
    return {"mensaje": "Tipo de incidente actualizado correctamente", "registro": registro}


@router.delete("/{tipo_id}")
def eliminar(tipo_id: int):
    """Baja lógica: el registro pasa a estado 'inactivo', no se borra."""
    repo.eliminar(tipo_id)
    return {"mensaje": "Tipo de incidente desactivado correctamente"}
