import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from jwt import InvalidTokenError

load_dotenv()

ALGORITHM = "HS256"
TOKEN_LIFETIME_HOURS = 8
TOKEN_LIFETIME_DAYS = 30


def _clave_secreta():
    clave = os.getenv("JWT_SECRET_KEY")
    if not clave:
        raise RuntimeError("JWT_SECRET_KEY no está configurada")
    return clave


def crear_token_acceso(usuario, recordar=False):
    """Crea el JWT con los datos que el backend necesita en cada petición."""
    ahora = datetime.now(timezone.utc)
    duracion = (
        timedelta(days=TOKEN_LIFETIME_DAYS)
        if recordar
        else timedelta(hours=TOKEN_LIFETIME_HOURS)
    )
    claims = {
        "sub": str(usuario["id_usuario"]),
        "id_rol": usuario["id_rol"],
        "rol": usuario["nombre_rol"],
        "nombre_usuario": usuario["nombre_usuario"],
        "id_docente": usuario.get("id_docente"),
        "id_psicorientador": usuario.get("id_psicorientador"),
        "iat": ahora,
        "exp": ahora + duracion,
    }
    token = jwt.encode(claims, _clave_secreta(), algorithm=ALGORITHM)
    return token, int(duracion.total_seconds())


def decodificar_token(token):
    claims = jwt.decode(token, _clave_secreta(), algorithms=[ALGORITHM])
    if not claims.get("sub") or not claims.get("id_rol") or not claims.get("rol"):
        raise InvalidTokenError("Faltan datos de autenticación en el token")
    return claims
