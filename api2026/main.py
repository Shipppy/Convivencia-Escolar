import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError

from app.api import (
    rutas_catalogos, rutas_comite, rutas_compromisos, rutas_dashboard, rutas_docentes,
    rutas_estudiantes, rutas_guia, rutas_incidentes, rutas_incidentes_protocolos,
    rutas_modulos, rutas_modulos_x_rol, rutas_niveles, rutas_protocolos,
    rutas_psicorientadores, rutas_reportes, rutas_roles, rutas_seguimientos,
    rutas_tablero, rutas_tipos_incidente, rutas_usuarios,
)
from app.core.auth import decodificar_token
from app.core.permissions import verificar_permiso

load_dotenv()

app = FastAPI(
    title="API de Seguimiento Socioemocional y Convivencia Escolar",
    description="Backend modular (FastAPI + PostgreSQL/Neon) con login JWT y permisos por rol.",
    version="1.0.0",
)

RUTAS_PUBLICAS = {
    "/", "/health", "/usuarios/login",
    "/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect",
}


def _token_de(request: Request):
    esquema, _, token = request.headers.get("Authorization", "").partition(" ")
    if esquema.lower() == "bearer" and token:
        return token
    return request.cookies.get("access_token")  # respaldo


# El middleware se declara ANTES que CORS: CORS queda como el mas externo
# y asi las respuestas 401/403 tambien llevan los encabezados CORS.
@app.middleware("http")
async def autenticar_y_autorizar(request: Request, call_next):
    ruta = request.url.path.rstrip("/") or "/"
    if request.method == "OPTIONS" or ruta in RUTAS_PUBLICAS:
        return await call_next(request)

    token = _token_de(request)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Debes iniciar sesión"})

    try:
        claims = decodificar_token(token)
    except InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "La sesión no es válida o ya venció"})
    except RuntimeError as e:
        print(f"Configuración incompleta: {e}")
        return JSONResponse(status_code=500, content={"detail": "El servidor no está configurado correctamente"})

    request.state.usuario = claims
    try:
        # verificar_permiso consulta la base de datos (codigo sincrono)
        await run_in_threadpool(verificar_permiso, request, claims)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    return await call_next(request)


origenes = [o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

for modulo in (
    rutas_usuarios, rutas_roles, rutas_modulos, rutas_modulos_x_rol, rutas_catalogos, rutas_guia,
    rutas_dashboard, rutas_estudiantes, rutas_docentes, rutas_comite, rutas_psicorientadores,
    rutas_tipos_incidente, rutas_niveles, rutas_protocolos, rutas_incidentes,
    rutas_incidentes_protocolos, rutas_compromisos, rutas_seguimientos, rutas_tablero, rutas_reportes,
):
    app.include_router(modulo.router)


@app.get("/")
def estado_api():
    return {"mensaje": "La API de convivencia escolar se encuentra en línea y funcional"}


@app.get("/health")
def health():
    """Render usa esta ruta para saber si el servicio está vivo."""
    return {"estado": "ok"}
