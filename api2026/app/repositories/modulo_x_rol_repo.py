from app.repositories.base import BaseRepository


class ModuloXRolRepository(BaseRepository):
    tabla = "modulos_x_rol"
    pk = "id_modulo_rol"
    nombre_singular = "permiso del rol"
    columnas = [
        "id_rol", "id_modulo", "puede_ver", "puede_crear",
        "puede_editar", "puede_eliminar", "estado",
    ]
    SQL_SELECT = """
        SELECT t.*, r.nombre AS rol, m.nombre AS modulo
        FROM modulos_x_rol t
        INNER JOIN roles r ON r.id_rol = t.id_rol
        INNER JOIN modulos m ON m.id_modulo = t.id_modulo
    """
    ORDEN = "t.id_rol, t.id_modulo"

    def modulos_del_rol(self, id_rol):
        """Modulos activos del rol con sus permisos (alimenta el menu del frontend)."""
        return self.ejecutar(
            """
            SELECT m.id_modulo, m.nombre, m.descripcion,
                   COALESCE(t.puede_ver, FALSE) AS puede_ver,
                   COALESCE(t.puede_crear, FALSE) AS puede_crear,
                   COALESCE(t.puede_editar, FALSE) AS puede_editar,
                   COALESCE(t.puede_eliminar, FALSE) AS puede_eliminar
            FROM modulos_x_rol t
            INNER JOIN modulos m ON m.id_modulo = t.id_modulo
            WHERE t.id_rol = %s AND t.estado = 'activo' AND m.estado = 'activo'
            ORDER BY m.id_modulo
            """,
            (id_rol,),
            accion="consultar los módulos del rol",
            fetch="all",
        )

    def crear(self, modelo):
        """Asignar dos veces actualiza, no duplica."""
        datos = self._datos(modelo)
        previo = self.ejecutar(
            "SELECT id_modulo_rol FROM modulos_x_rol WHERE id_rol = %s AND id_modulo = %s",
            (datos["id_rol"], datos["id_modulo"]),
            accion="consultar el permiso",
        )
        if previo:
            datos.setdefault("estado", "activo")
            if datos["estado"] is None:
                datos["estado"] = "activo"
            return self.actualizar(previo["id_modulo_rol"], type(modelo)(**datos))
        return super().crear(modelo)

    def preparar(self, datos, id_registro=None):
        # Un permiso vacio no debe borrar el valor guardado
        for c in ("puede_ver", "puede_crear", "puede_editar", "puede_eliminar"):
            if c in datos and datos[c] is None:
                datos.pop(c)
        return datos
