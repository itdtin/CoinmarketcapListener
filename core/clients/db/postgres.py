from _collections_abc import dict_keys
from collections import namedtuple

import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs
from psycopg2.errors import (
    DuplicateSchema,
    UndefinedColumn,
    UniqueViolation,
    InvalidTextRepresentation,
    DuplicateTable,
    DuplicateObject,
)

from core.logger.logger import logger
from core.clients.db.base_client import BaseClient


class PGClient(BaseClient):
    """PostgreSQL client"""

    def __init__(self, host: str, port: int, user: str, password: str, db_name: str):
        super(PGClient, self).__init__(host, port, user, password, db_name)
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    dbname=self.db_name,
                )
                self.conn.autocommit = True
            except psycopg2.DatabaseError as e:
                logger.error(e)
                raise e
            finally:
                logger.info(
                    f"Connection to Postgres DB '{self.db_name}' opened successfully."
                )

    def close_connect(self):
        """Close connect"""
        self.conn.close()

    def execute(self, query: str, fetch: bool = True, update: bool = False):
        """Execute sql query"""
        assert self.conn is not None, f"Connection to Postgres DB is unavailable"
        with self.conn.cursor() as curr:
            try:
                result = curr.execute(query)
                logger.debug(f"Executed sql query: {query}")
                if fetch:
                    result = curr.fetchall()
                elif update:
                    result = curr.rowcount
                return result
            except (DuplicateSchema, DuplicateTable, DuplicateObject) as err:
                args = self.psql_exception_handle(err)
                error_msg = f"Cannot execute query '{query}'.\n {args[0]}"
                logger.debug(error_msg)
                return False

    def create_record(self, query: str, columns: dict_keys, values: list):
        """Create record in pg table"""
        assert self.conn is not None, f"Connection to Postgres DB is unavailable"
        with self.conn.cursor() as curr:
            try:
                curr.execute(query, (AsIs(",".join(columns)), tuple(values)))
            except UndefinedColumn as err:
                logger.error(f"Please check column names. Found undefined column")
                raise err
            except UniqueViolation as err:
                logger.error(
                    f"Check input data, discover duplicate while executing query: '{query}'"
                )
                raise err
            except InvalidTextRepresentation as err:
                logger.error(f"")
                raise err

    def create_record_v2(self, query: str, row):
        """Create record in pg table"""
        ### This one for quoting Identifiers and Placeholders
        assert self.conn is not None, f"Connection to Postgres DB is unavailable"
        with self.conn.cursor() as curr:
            insert_str = sql.SQL(query).format(
                sql.SQL(",").join(map(sql.Identifier, row)),
                sql.SQL(",").join(map(sql.Placeholder, row)),
            )
            curr.execute(insert_str, row)

    def execute_dict_cursor(self, query: str, fetch: bool = True) -> list:
        """Execute sql query with dict cursor"""
        assert self.conn is not None, f"Connection to Postgres DB is unavailable"
        with self.conn.cursor(cursor_factory=DictCursor) as dict_curr:
            dict_curr.execute(query)
            logger.debug(f"Executed sql query with DictCursor: {query}")
            if fetch:
                results = dict_curr.fetchall()
                return results

    def select_rows(self, query: str) -> list:
        """Run a SQL query to select rows from table."""
        return self.execute(query, fetch=True)

    def select_rows_dict_cursor(self, query: str) -> list:
        """Run SELECT query and return dictionaries."""
        return self.execute_dict_cursor(query, fetch=True)

    def update_rows(self, query: str) -> int:
        """Run a SQL query to update rows in table."""
        return self.execute(query, update=True)

    def psql_exception_handle(self, err):
        """"""
        return err.args[0].split("\n")

    def create_schema(self, schema_name: str):
        """Create schema"""
        query = f"CREATE SCHEMA {schema_name}"

        result = self.execute(query, fetch=False)
        logger.debug(f"Created schema {schema_name}")
        if result is not None:
            logger.info(f"Created schema {schema_name}")
        else:
            result = schema_name
            logger.info(f"Schema '{schema_name}' already exist.")
        return result

    def delete_schema(self, schema_name: str):
        """Drop schema if exist"""
        query = f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"
        result = self.execute(query, fetch=False)
        return result

    def delete_table(self, table_name: str):
        """Delete table"""
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
        result = self.execute(query, fetch=False)
        return result

    def clear_data(self, schema_name: str):
        """HARD. Not use in production
        Clear data in all tables in PG database"""
        tables = self.list_tables(schema_name=schema_name)
        for table in tables:
            self.truncate_table(table, schema_name)
        logger.debug(
            f"Truncated Postgres tables {', '.join(tables)} in schema '{schema_name}'"
        )

    def list_tables(self, schema_name: str):
        """List all tables in schema"""
        query = f"SELECT table_name FROM INFORMATION_SCHEMA.tables where table_schema='{schema_name}';"
        result = self.execute_dict_cursor(query)
        assert (
            isinstance(result, list) and len(result) > 0 and isinstance(result[0], list)
        ), f"Cannot get tables for {schema_name} in db {self.db_name}"
        tables = [table[0] for table in result]
        return tables

    def truncate_table(self, table_name: str, schema_name: str):
        """Delete all records from {table}"""
        query = f"TRUNCATE table {schema_name}.{table_name} CASCADE;"
        self.execute(query, fetch=False)
        logger.debug(f"Truncated table {schema_name}.{table_name}")

    def count_rows_in_table(self, table_name: str, schema_name: str):
        """
        :param table_name:
        :param schema_name:
        """
        query = f"SELECT COUNT(*) FROM {schema_name}.{table_name};"
        return self.execute(query)

    def get_table_columns_data(
        self, table_name: str, schema_name: str, excluded_columns: list = None
    ):
        """Get table columns data"""
        query = (
            f"SELECT column_name, data_type, is_nullable FROM information_schema.columns "
            f"WHERE table_schema='{schema_name}' AND table_name='{table_name}';"
        )
        result = {col[0]: (col[1], col[2]) for col in self.execute_dict_cursor(query)}
        if excluded_columns is not None:
            for ex_col in excluded_columns:
                if ex_col in result.keys():
                    result.pop(ex_col)
        return result

    def get_indexes(self, table_name: str, schema_name: str):
        """Get foreign keys for the table"""
        query = f"SELECT  indexname, indexdef FROM pg_indexes WHERE tablename = '{table_name}' and schemaname = '{schema_name}';"
        result = self.execute_dict_cursor(query)
        indexes = list()
        for ind in result:
            index = "(" + ind[1].split("(")[-1]
            indexes.append(index)
        return indexes

    def get_foreign_keys(self, table_name: str, schema_name: str):
        """Get foreign keys for the table
        :return: dict fith foregn keys, format:
        {}
        """
        query = (
            f"SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, "
            f"ccu.column_name AS foreign_column_name, tc.constraint_name "
            f"FROM information_schema.table_constraints AS tc "
            f"JOIN information_schema.key_column_usage AS kcu "
            f"ON tc.constraint_name = kcu.constraint_name "
            f"AND tc.table_schema = kcu.table_schema "
            f"JOIN information_schema.constraint_column_usage AS ccu "
            f"ON ccu.constraint_name = tc.constraint_name "
            f"AND ccu.table_schema = tc.table_schema "
            f"WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table_name}' and tc.table_schema = '{schema_name}';"
        )
        result = self.execute_dict_cursor(query)
        relationship_nt = namedtuple(table_name, ["table", "column", "fk_name"])
        result = {i[1]: relationship_nt(*i[2:]) for i in result}
        return result
