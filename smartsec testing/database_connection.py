import psycopg2

from constants import PG_DBNAME, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT


class DatabaseCursor:
    def __init__(self):
        pass

    def __enter__(self):
        self.conn = psycopg2.connect(
            dbname=PG_DBNAME,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
