from fastapi import APIRouter, HTTPException, Request

from app.models.incidente import Incidente
from app.repositories.incidente_repo import IncidenteRepository

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])
repo = IncidenteRepository()


def _es_docente(request: Request) -> bool:
    return str(request.state.usuario.get("rol", "")).strip().casefold() == "docente"


def _id_docente(request: Request):
    id_docente = request.state.usuario.get("id_docente")
    if not id_docente:
        raise HTTPException(403, "Tu usuario no está asociado a un docente")
    return id_docente


@router.get("/")
def listar(request: Request, todos: bool = False):
    """Un docente solo ve los incidentes que él reportó; los demás roles ven todos."""
    if _es_docente(request):
        return repo.obtener_todos(todos, id_docente=_id_docente(request), solo_del_docente=True)
    return repo.obtener_todos(todos)


@router.get("/{incidente_id}")
def obtener(incidente_id: int, request: Request):
    registro = repo.obtener_por_id(incidente_id)
    if _es_docente(request) and registro["id_docente"] != _id_docente(request):
        raise HTTPException(403, "Solo puedes consultar los incidentes que tú reportaste")
    return registro


@router.post("/", status_code=201)
def crear(incidente: Incidente, request: Request):
    if _es_docente(request):
        # El docente no elige "docente" ni "estado": el servidor los fija
        incidente.id_docente = _id_docente(request)
        incidente.estado = None
    registro = repo.crear(incidente)
    return {"mensaje": "Incidente registrado correctamente", "registro": registro}


@router.put("/{incidente_id}")
def actualizar(incidente_id: int, incidente: Incidente, request: Request):
    if _es_docente(request):
        incidente.id_docente = _id_docente(request)
        incidente.estado = None
    registro = repo.actualizar(incidente_id, incidente)
    return {"mensaje": "Incidente actualizado correctamente", "registro": registro}


@router.delete("/{incidente_id}")
def eliminar(incidente_id: int):
    """Baja lógica: el incidente pasa a estado 'inactivo'."""
    repo.eliminar(incidente_id)
    return {"mensaje": "Incidente desactivado correctamente"}
