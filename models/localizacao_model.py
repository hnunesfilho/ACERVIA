# models/localizacao_model.py

from database.connection import Connection


class Estante:
    """Model da entidade ESTANTES do DER."""

    @staticmethod
    def listar_todas():
        db = Connection()
        query = """
            SELECT e.*, COUNT(l.id_livro) as total_livros
            FROM estantes e
            LEFT JOIN prateleiras p ON e.id_estante = p.id_estante
            LEFT JOIN livros l ON l.id_prateleira = p.id_prateleira
            GROUP BY e.id_estante
            ORDER BY e.nome_estante
        """
        return db.execute(query, fetch=True)

    @staticmethod
    def existe(nome, ignorar_id=None):
        db = Connection()
        if ignorar_id:
            query = "SELECT id_estante FROM estantes WHERE nome_estante=%s AND id_estante != %s"
            row = db.execute(query, (nome, ignorar_id), fetchone=True)
        else:
            query = "SELECT id_estante FROM estantes WHERE nome_estante=%s"
            row = db.execute(query, (nome,), fetchone=True)
        return row is not None

    @staticmethod
    def salvar(nome):
        """RF-011: Criar nova estante."""
        db = Connection()
        return db.execute("INSERT INTO estantes (nome_estante) VALUES (%s)", (nome,))

    @staticmethod
    def atualizar(id_estante, nome):
        db = Connection()
        db.execute("UPDATE estantes SET nome_estante=%s WHERE id_estante=%s", (nome, id_estante))

    @staticmethod
    def excluir(id_estante):
        db = Connection()
        db.execute("DELETE FROM estantes WHERE id_estante=%s", (id_estante,))


class Prateleira:
    """Model da entidade PRATELEIRAS do DER."""

    @staticmethod
    def listar_todas():
        db = Connection()
        query = """
            SELECT p.*, e.nome_estante, COUNT(l.id_livro) as total_livros
            FROM prateleiras p
            JOIN estantes e ON p.id_estante = e.id_estante
            LEFT JOIN livros l ON l.id_prateleira = p.id_prateleira
            GROUP BY p.id_prateleira
            ORDER BY p.nome_prateleira
        """
        return db.execute(query, fetch=True)

    @staticmethod
    def existe(id_estante, nome, ignorar_id=None):
        """RN-013: Cada prateleira pertence a uma única estante (nome único por estante)."""
        db = Connection()
        if ignorar_id:
            query = """SELECT id_prateleira FROM prateleiras
                       WHERE id_estante=%s AND nome_prateleira=%s AND id_prateleira != %s"""
            row = db.execute(query, (id_estante, nome, ignorar_id), fetchone=True)
        else:
            query = "SELECT id_prateleira FROM prateleiras WHERE id_estante=%s AND nome_prateleira=%s"
            row = db.execute(query, (id_estante, nome), fetchone=True)
        return row is not None

    @staticmethod
    def salvar(id_estante, nome):
        """RF-012: Criar nova prateleira."""
        db = Connection()
        query = "INSERT INTO prateleiras (id_estante, nome_prateleira) VALUES (%s, %s)"
        return db.execute(query, (id_estante, nome))

    @staticmethod
    def atualizar(id_prateleira, id_estante, nome):
        db = Connection()
        query = "UPDATE prateleiras SET id_estante=%s, nome_prateleira=%s WHERE id_prateleira=%s"
        db.execute(query, (id_estante, nome, id_prateleira))

    @staticmethod
    def excluir(id_prateleira):
        db = Connection()
        db.execute("DELETE FROM prateleiras WHERE id_prateleira=%s", (id_prateleira,))