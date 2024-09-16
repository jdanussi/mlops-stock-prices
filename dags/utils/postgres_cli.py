"""Postgres_cli module."""

from utils.db_handler import DatabaseHandler


class PostgresClient(DatabaseHandler):
    """Extends DatabaseHandler class for use with Postgres."""

    def __init__(self, db):
        """Class Init."""
        super().__init__(db=db)
        self.dialect = "postgresql+psycopg2"
        self.db_uri = f"{self.dialect}://{self.db}"
        self.engine = self._get_engine()
