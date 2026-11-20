from fastapi import APIRouter, HTTPException

from app.repositories.base import ejecutar

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])

# Listas cortas (id + etiqueta) para llenar los desplegables: el usuario ve nombres, se envía el id.
CATALOGOS = {
    "roles": "SELECT id_rol AS id, nombre AS etiqueta FROM roles WHERE estado = 'activo' ORDER BY nombre",
    "modulos": "SELECT id_modulo AS id, nombre AS etiqueta FROM modulos WHERE estado = 'activo' ORDER BY id_modulo",
    "docentes": "SELECT id_docente AS id, nombre || ' ' || apellido AS etiqueta FROM docentes WHERE estado = 'activo' ORDER BY apellido, nombre",
    "estudiantes": "SELECT id_estudiante AS id, nombre || ' ' || apellido || ' (' || COALESCE(grado, '') || COALESCE(curso, '') || ')' AS etiqueta FROM estudiantes WHERE estado = 'activo' ORDER BY apellido, nombre",
    "comite": "SELECT id_miembro AS id, nombre || ' · ' || rol AS etiqueta FROM comites_orientacion WHERE estado = 'activo' ORDER BY nombre",
    "psicorientadores": "SELECT id_psicorientador AS id, nombre || ' ' || apellido AS etiqueta FROM psicorientadores WHERE estado = 'activo' ORDER BY apellido, nombre",
    "tipos-incidente": "SELECT id_tipo AS id, nombre AS etiqueta FROM tipos_incidente WHERE estado = 'activo' ORDER BY nombre",
    "niveles": "SELECT id_nivel AS id, nombre AS etiqueta FROM nivel_protocolo WHERE estado = 'activo' ORDER BY id_nivel",
    "protocolos": "SELECT p.id_protocolo AS id, np.nombre || ' · paso ' || p.paso || ' · ' || p.nombre AS etiqueta FROM protocolo p INNER JOIN nivel_protocolo np ON np.id_nivel = p.id_nivel WHERE p.estado = 'activo' ORDER BY p.id_nivel, p.paso",
    "incidentes": "SELECT id_incidente AS id, to_char(fecha, 'DD/MM/YYYY') || ' · ' || descripcion AS etiqueta FROM incidentes WHERE estado <> 'inactivo' ORDER BY fecha DESC, id_incidente DESC",
    "compromisos": "SELECT id_compromiso AS id, descripcion AS etiqueta FROM compromisos WHERE estado <> 'inactivo' ORDER BY fecha DESC, id_compromiso DESC",
}


@router.get("/{nombre}")
def obtener_catalogo(nombre: str):
    if nombre not in CATALOGOS:
        raise HTTPException(404, "Catálogo no encontrado")
    return ejecutar(CATALOGOS[nombre], accion=f"consultar el catálogo {nombre}", fetch="all")
