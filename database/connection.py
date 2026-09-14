# database/connection.py

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class Connection:
    """
    Classe responsável por gerenciar a conexão única (Singleton)
    com o banco de dados MySQL.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Connection, cls).__new__(cls)
            cls._instance._conn = None
        return cls._instance

    def get_connection(self):
        if self._conn is None or not self._conn.is_connected():
            try:
                self._conn = mysql.connector.connect(**DB_CONFIG)
            except Error as e:
                raise Exception(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return self._conn

    def execute(self, query, params=None, fetch=False, fetchone=False):
        """
        Executa uma query genérica.
        fetch=True retorna todos os resultados.
        fetchone=True retorna um único resultado.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return result
            if fetchone:
                result = cursor.fetchone()
                return result
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            conn.rollback()
            raise Exception(f"Erro ao executar query: {e}")
        finally:
            cursor.close()

    def close(self):
        if self._conn and self._conn.is_connected():
            self._conn.close()