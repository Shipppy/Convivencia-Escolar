import os

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from app.core.auth import crear_token_acceso
from app.core.passwords import hash_password, verify_password
from app.models.usuario import Usuario
from app.repositories.base import ejecutar
from app.repositories.modulo_x_rol_repo import ModuloXRolRepository
from app.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
repo = UsuarioRepository()


class LoginRequest(BaseModel):
    correo: str
    contrasena: str
    rol: str
    recordar: bool = False


def _cookie_segura() -> bool:
    return os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"


@router.post("/login")
def iniciar_sesion(datos: LoginRequest, response: Response):
    usuario = ejecutar(
        """
        SELECT u.id_usuario, u.nombre_usuario, u.nombre, u.apellido, u.correo,
               u.password_hash, u.id_rol, u.id_docente, u.id_psicorientador,
               r.nombre AS nombre_rol
        FROM usuarios u
        INNER JOIN roles r ON r.id_rol = u.id_rol
        WHERE LOWER(TRIM(u.correo)) = LOWER(TRIM(%s))
          AND u.estado = 'activo' AND r.estado = 'activo'
        """,
        (datos.correo,),
        accion="validar las credenciales",
    )
    if usuario is None:
        raise HTTPException(401, "Correo o contraseña incorrectos")

    valida, migrar = verify_password(datos.contrasena, usuario["password_hash"])
    if not valida:
        raise HTTPException(401, "Correo o contraseña incorrectos")

    # Si la clave estaba en texto plano, se cifra automáticamente
    if migrar:
        ejecutar(
            "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s",
            (hash_password(datos.contrasena), usuario["id_usuario"]),
            accion="actualizar la contraseña",
            fetch=None,
        )

    # El rol elegido en el login debe coincidir con el de la base de datos
    if usuario["nombre_rol"].strip().casefold() != datos.rol.strip().casefold():
        raise HTTPException(403, "El rol seleccionado no corresponde a este usuario")

    try:
        token, expira = crear_token_acceso(usuario, datos.recordar)
    except RuntimeError as e:
        print(f"Configuración incompleta: {e}")
        raise HTTPException(500, "El servidor no está configurado correctamente")

    segura = _cookie_segura()
    # La cookie queda de respaldo; el frontend usa el encabezado Authorization: Bearer
    response.set_cookie(
        key="access_token", value=token, httponly=True, secure=segura,
        samesite="none" if segura else "lax", max_age=expira, path="/",
    )
    return {
        "mensaje": "Inicio de sesión exitoso",
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expira,
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre_usuario": usuario["nombre_usuario"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"],
            "correo": usuario["correo"],
            "id_rol": usuario["id_rol"],
            "rol": usuario["nombre_rol"],
            "id_docente": usuario["id_docente"],
            "id_psicorientador": usuario["id_psicorientador"],
        },
    }


@router.post("/logout")
def cerrar_sesion(response: Response):
    segura = _cookie_segura()
    response.delete_cookie(
        key="access_token", httponly=True, secure=segura,
        samesite="none" if segura else "lax", path="/",
    )
    return {"mensaje": "Sesión cerrada correctamente"}


@router.get("/yo")
def usuario_actual(request: Request):
    """Datos del usuario autenticado y los módulos que su rol puede ver."""
    claims = request.state.usuario
    usuario = repo.obtener_por_id(int(claims["sub"]))
    return {
        "usuario": usuario,
        "modulos": ModuloXRolRepository().modulos_del_rol(claims["id_rol"]),
    }


@router.get("/")
def listar(todos: bool = False):
    return repo.obtener_todos(incluir_inactivos=todos)


@router.get("/{usuario_id}")
def obtener(usuario_id: int):
    return repo.obtener_por_id(usuario_id)


@router.post("/", status_code=201)
def crear(usuario: Usuario):
    registro = repo.crear(usuario)
    return {"mensaje": "Usuario registrado correctamente", "registro": registro}


@router.put("/{usuario_id}")
def actualizar(usuario_id: int, usuario: Usuario):
    registro = repo.actualizar(usuario_id, usuario)
    return {"mensaje": "Usuario actualizado correctamente", "registro": registro}


@router.delete("/{usuario_id}")
def eliminar(usuario_id: int):
    """Baja lógica: el usuario pasa a 'inactivo' y su token deja de servir."""
    repo.eliminar(usuario_id)
    return {"mensaje": "Usuario desactivado correctamente"}
