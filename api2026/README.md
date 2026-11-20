# API de Convivencia Escolar (FastAPI + Neon)

Backend adaptado del proyecto de semilleros (api2026) al tema de Seguimiento Socioemocional y Convivencia Escolar,
siguiendo la guía paso a paso. La base de datos es la del script SQL de Neon (16 tablas): no se cambió ninguna tabla.

## Ejecutar en local
```
cd api
python -m venv myvenv
myvenv\Scripts\activate        # Linux/Mac: source myvenv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Linux/Mac: cp .env.example .env  (y completa DATABASE_URL y JWT_SECRET_KEY)
uvicorn main:app --reload
```
Documentación: http://localhost:8000/docs  (login de prueba: admin@gmail.com / 12345 / rol Administrador)

## Qué hay
- app/core: database (DATABASE_URL), passwords (PBKDF2), auth (JWT), permissions (modulos_x_rol), reportes (PDF/Excel), correo (Brevo/SMTP)
- app/models: validación Pydantic · app/repositories: todo el SQL (BaseRepository + una clase por tabla) · app/api: rutas
- Eliminar = baja lógica (estado = 'inactivo'). Errores de BD -> 404/409/422/503.
- Login devuelve access_token (encabezado Authorization: Bearer); la cookie queda de respaldo.
- Rutas extra: /catalogos/{nombre}, /guia, /dashboard/resumen, /tablero/datos, /reportes/..., /health

## Para publicar en Render (lo haces tú)
Root Directory `api` · Build `pip install -r requirements.txt` · Start `uvicorn main:app --host 0.0.0.0 --port $PORT`
Variables: DATABASE_URL, JWT_SECRET_KEY, JWT_COOKIE_SECURE=true, CORS_ORIGINS (URL de Netlify, sin barra final), y BREVO_API_KEY/EMAIL_FROM si envías reportes.
