from fastapi import HTTPException

from app.core.passwords import hash_password
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository):
    tabla = "usuarios"
    pk = "id_usuario"
    nombre_singular = "usuario"
    columnas = [
        "nombre_usuario", "nombre", "apellido", "correo", "password_hash",
        "estado", "id_rol", "id_docente", "id_psicorientador",
    ]
    # Nunca se devuelve password_hash
    SQL_SELECT = """
        SELECT t.id_usuario, t.nombre_usuario, t.nombre, t.apellido, t.correo, t.estado,
               t.id_rol, t.id_docente, t.id_psicorientador, t.creado, t.actualizado,
               r.nombre AS rol,
               COALESCE(d.nombre || ' ' || d.apellido, 'Sin docente') AS docente,
               COALESCE(p.nombre || ' ' || p.apellido, 'Sin psicorientador') AS psicorientador
        FROM usuarios t
        INNER JOIN roles r ON r.id_rol = t.id_rol
        LEFT JOIN docentes d ON d.id_docente = t.id_docente
        LEFT JOIN psicorientadores p ON p.id_psicorientador = t.id_psicorientador
    """
    ORDEN = "t.nombre_usuario"

    def preparar(self, datos, id_registro=None):
        contrasena = datos.pop("contrasena", None)
        if contrasena:
            datos["password_hash"] = hash_password(contrasena)
        elif id_registro is None:
            raise HTTPException(422, "La contraseña es obligatoria")
        return datos
