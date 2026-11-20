from fastapi import HTTPException

from app.core.database import Database


def traducir_error(e: Exception, accion: str) -> HTTPException:
    """Convierte los errores de PostgreSQL (pgcode) en respuestas HTTP claras."""
    codigo = getattr(e, "pgcode", None) or ""
    if codigo == "23505":
        return HTTPException(409, "Ya existe un registro con esos datos únicos")
    if codigo == "23503":
        return HTTPException(422, "Un registro relacionado no existe o todavía está en uso")
    if codigo == "23514":
        return HTTPException(422, "Un valor está fuera del rango permitido")
    if codigo == "23502":
        return HTTPException(422, "Falta un dato obligatorio")
    if codigo.startswith("22"):
        return HTTPException(422, "Un dato tiene un formato o una longitud inválida")
    print(f"Error al {accion}: {e}")  # el detalle solo se escribe en la consola
    return HTTPException(500, f"No fue posible {accion}")


def ejecutar(sql, params=(), accion="procesar la solicitud", fetch="one"):
    """Ejecuta una consulta. fetch: 'one' | 'all' | None."""
    conn = Database().get_connection()
    if conn is None:
        raise HTTPException(503, "No fue posible conectar con la base de datos")
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "one":
                resultado = cur.fetchone()
            elif fetch == "all":
                resultado = cur.fetchall()
            else:
                resultado = None
        conn.commit()
        return resultado
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise traducir_error(e, accion)
    finally:
        conn.close()


class BaseRepository:
    """CRUD generico. Cada repositorio hijo declara tabla, pk, columnas y (opcional) SQL_SELECT."""

    tabla = ""
    pk = ""
    nombre_singular = "registro"
    columnas: list = []
    SQL_SELECT = None
    ORDEN = "t.estado, t.creado DESC"

    def _select(self):
        return self.SQL_SELECT or f"SELECT t.* FROM {self.tabla} t"

    def _datos(self, modelo):
        datos = modelo.model_dump(exclude_unset=True)
        limpio = {}
        for k, v in datos.items():
            if v == "":
                v = None
            limpio[k] = v
        return limpio

    def preparar(self, datos, id_registro=None):
        """Gancho para reglas de negocio. Devuelve los datos listos para guardar."""
        return datos

    def obtener_todos(self, incluir_inactivos=False, filtro=None, params=()):
        condiciones = []
        if not incluir_inactivos:
            condiciones.append("t.estado <> 'inactivo'")
        if filtro:
            condiciones.append(filtro)
        donde = f" WHERE {' AND '.join(condiciones)}" if condiciones else ""
        return ejecutar(
            f"{self._select()}{donde} ORDER BY {self.ORDEN}",
            tuple(params),
            accion=f"consultar {self.nombre_singular}",
            fetch="all",
        )

    def obtener_por_id(self, id_registro):
        fila = ejecutar(
            f"{self._select()} WHERE t.{self.pk} = %s",
            (id_registro,),
            accion=f"consultar {self.nombre_singular}",
        )
        if not fila:
            raise HTTPException(404, f"{self.nombre_singular.capitalize()} no encontrado")
        return fila

    def crear(self, modelo):
        datos = self.preparar(self._datos(modelo))
        # Los valores vacios se omiten para que la base use sus valores por defecto.
        datos = {c: v for c, v in datos.items() if v is not None and c in self.columnas}
        if not datos:
            raise HTTPException(422, "No se recibieron datos para registrar")
        columnas = ", ".join(datos)
        marcas = ", ".join(["%s"] * len(datos))
        fila = self.ejecutar(
            f"INSERT INTO {self.tabla} ({columnas}) VALUES ({marcas}) RETURNING {self.pk}",
            tuple(datos.values()),
            accion=f"registrar {self.nombre_singular}",
        )
        return self.obtener_por_id(fila[self.pk])

    def actualizar(self, id_registro, modelo):
        self.obtener_por_id(id_registro)  # 404 si no existe
        datos = self.preparar(self._datos(modelo), id_registro)
        datos = {c: v for c, v in datos.items() if c in self.columnas}
        if datos.get("estado", "x") is None:
            datos.pop("estado")
        if not datos:
            raise HTTPException(422, "No se recibieron datos para actualizar")
        cambios = ", ".join(f"{c} = %s" for c in datos)
        self.ejecutar(
            f"UPDATE {self.tabla} SET {cambios}, actualizado = CURRENT_TIMESTAMP "
            f"WHERE {self.pk} = %s RETURNING {self.pk}",
            (*datos.values(), id_registro),
            accion=f"actualizar {self.nombre_singular}",
        )
        return self.obtener_por_id(id_registro)

    def eliminar(self, id_registro):
        """Baja logica: estado = 'inactivo'. La fila queda en la base de datos."""
        fila = self.ejecutar(
            f"UPDATE {self.tabla} SET estado = 'inactivo', actualizado = CURRENT_TIMESTAMP "
            f"WHERE {self.pk} = %s AND estado <> 'inactivo' RETURNING {self.pk}",
            (id_registro,),
            accion=f"desactivar {self.nombre_singular}",
        )
        if not fila:
            raise HTTPException(
                404, f"{self.nombre_singular.capitalize()} no encontrado o ya inactivo"
            )
        return True

    def ejecutar(self, sql, params=(), accion="procesar la solicitud", fetch="one"):
        return ejecutar(sql, params, accion, fetch)
