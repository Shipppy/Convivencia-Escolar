import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class Database:
    """Crea la conexion a PostgreSQL (Neon).

    Prioridad: si existe DATABASE_URL se usa esa cadena (lo normal en Render).
    Si no, se usan las variables DB_HOST, DB_NAME, DB_USER, etc.
    """

    def __init__(self):
        self.url = os.getenv("DATABASE_URL")
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT", "5432")
        self.sslmode = os.getenv("DB_SSLMODE", "require")

    def get_connection(self):
        try:
            if self.url:
                return psycopg2.connect(self.url, cursor_factory=RealDictCursor)
            return psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                sslmode=self.sslmode,
                cursor_factory=RealDictCursor,
            )
        except Exception as e:
            print(f"Error de conexión a la BD: {e}")
            return None
