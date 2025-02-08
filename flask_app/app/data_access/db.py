import psycopg2 as pg
from psycopg2 import pool
from contextlib import contextmanager
from typing import Generator

class BaseDB:
    _pool = None  # Shared pool for all subclasses

    @classmethod
    def initialize_pool(cls, db_str: str, minconn: int = 1, maxconn: int = 10):
        """Initialize a single connection pool for all database classes."""
        if cls._pool is None:  # Ensure only one pool is created
            cls._pool = pool.SimpleConnectionPool(
                minconn, maxconn, dsn=db_str
            )

    @contextmanager
    def connect_db(self) -> Generator[pg.extensions.connection, None, None]:
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)
