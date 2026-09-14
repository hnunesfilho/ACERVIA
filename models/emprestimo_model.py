# models/emprestimo_model.py

from database.connection import Connection


class Emprestimo:
    """Model da entidade EMPRESTIMOS do DER."""

    @staticmethod
    def registrar(id_livro, observacoes):
        """
        RF-016/RF-017: Registrar empréstimo com data automática.
        RN-012: Data do empréstimo registrada automaticamente (CURRENT_TIMESTAMP).
        """
        db = Connection()
        query = """
            INSERT INTO emprestimos (id_livro, observacoes, status)
            VALUES (%s, %s, 'ativo')
        """
        return db.execute(query, (id_livro, observacoes))

    @staticmethod
    def finalizar_emprestimo_ativo(id_livro):
        """Ao devolver o livro, finaliza o empréstimo ativo mais recente."""
        db = Connection()
        query = """
            UPDATE emprestimos
            SET status='finalizado', data_devolucao=NOW()
            WHERE id_livro=%s AND status='ativo'
        """
        db.execute(query, (id_livro,))

    @staticmethod
    def historico_por_livro(id_livro):
        """RF-018: Consultar histórico de empréstimos de um livro."""
        db = Connection()
        query = """
            SELECT * FROM emprestimos
            WHERE id_livro=%s
            ORDER BY data_emprestimo DESC
        """
        return db.execute(query, (id_livro,), fetch=True)