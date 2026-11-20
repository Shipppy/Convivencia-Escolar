from fastapi import HTTPException, Request

from app.core.database import Database

ROL_ADMIN = "administrador"

# Mapa ruta -> modulo de la tabla modulos
RUTAS_MODULO = {
    "/usuarios": "Usuarios",
    "/roles": "Roles",
    "/modulos": "Roles",
    "/modulos-x-rol": "Roles",
    "/estudiantes": "Estudiantes",
    "/docentes": "Docentes",
    "/incidentes": "Incidentes",
    "/protocolos": "Protocolo",
    "/niveles": "Protocolo",
    "/tipos-incidente": "Protocolo",
    "/incidentes-protocolos": "Protocolo",
    "/compromisos": "Compromisos",
    "/seguimientos": "Seguimientos",
    "/comite": "Comites",
    "/psicorientadores": "Psicorientadores",
    "/reportes": "Reportes",
    "/tablero": "Tablero",
    "/dashboard": "Inicio",
}

# Metodo HTTP -> permiso exigido en modulos_x_rol
ACCION_POR_METODO = {
    "GET": "puede_ver",
    "POST": "puede_crear",
    "PUT": "puede_editar",
    "PATCH": "puede_editar",
    "DELETE": "puede_eliminar",
}

# Rutas que solo exigen haber iniciado sesion
SOLO_SESION = ("/usuarios/logout", "/usuarios/yo", "/catalogos", "/guia")
# Rutas de consulta: cualquier metodo exige solo puede_ver
SOLO_VER = ("/reportes", "/tablero", "/dashboard")


def _modulo_de_ruta(ruta: str):
    # Prefijo mas largo primero: /incidentes-protocolos no debe caer en /incidentes
    for prefijo in sorted(RUTAS_MODULO, key=len, reverse=True):
        if ruta == prefijo or ruta.startswith(prefijo + "/"):
            return RUTAS_MODULO[prefijo]
    return None


def _consultar(sql, params):
    conn = Database().get_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="No fue posible conectar con la base de datos")
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    except Exception as e:
        print(f"Error verificando permisos: {e}")
        raise HTTPException(status_code=500, detail="No fue posible verificar los permisos")
    finally:
        conn.close()


def verificar_permiso(request: Request, usuario: dict):
    ruta = request.url.path.rstrip("/") or "/"
    metodo = request.method.upper()

    # 1. El usuario debe seguir activo (si lo desactivas, su token deja de servir)
    activo = _consultar(
        "SELECT 1 AS ok FROM usuarios WHERE id_usuario = %s AND estado = 'activo'",
        (int(usuario["sub"]),),
    )
    if not activo:
        raise HTTPException(status_code=401, detail="La sesión no es válida o ya venció")

    es_admin = str(usuario.get("rol", "")).strip().casefold() == ROL_ADMIN

    # 2. Rutas que solo exigen sesion
    if ruta.startswith(SOLO_SESION):
        return

    # 3. Cada rol solo puede pedir sus propios modulos
    if ruta.startswith("/modulos-x-rol/rol/"):
        if ruta.split("/")[-1] != str(usuario.get("id_rol")) and not es_admin:
            raise HTTPException(status_code=403, detail="No puedes consultar módulos de otro rol")
        return

    # 4. El administrador tiene acceso a todo
    if es_admin:
        return

    modulo = _modulo_de_ruta(ruta)
    if modulo is None:
        raise HTTPException(status_code=403, detail="No hay permisos configurados para esta ruta")

    accion = "puede_ver" if ruta.startswith(SOLO_VER) else ACCION_POR_METODO.get(metodo)
    if accion is None:
        raise HTTPException(status_code=405, detail="Método no permitido")

    fila = _consultar(
        f"""
        SELECT mxr.{accion} AS permitido
        FROM modulos_x_rol mxr
        INNER JOIN modulos m ON m.id_modulo = mxr.id_modulo
        WHERE mxr.id_rol = %s AND m.nombre = %s
          AND mxr.estado = 'activo' AND m.estado = 'activo'
        """,
        (usuario.get("id_rol"), modulo),
    )
    if not fila or not fila["permitido"]:
        raise HTTPException(
            status_code=403,
            detail=f"Tu rol no tiene permiso para esta operación en el módulo {modulo}",
        )
