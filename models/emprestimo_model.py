# models/emprestimo_model.py

from database.connection import Connection


class Emprestimo:
    """
    Model da entidade EMPRESTIMOS.
    Agora vinculado ao EXEMPLAR (cópia física), não mais à obra,
    já que é a cópia específica que é emprestada.
    """

    @staticmethod
    def registrar(id_exemplar, observacoes):
        """
        RF-016/RF-017: Registrar empréstimo com data automática.
        RN-012: Data do empréstimo registrada automaticamente (CURRENT_TIMESTAMP).
        """
        db = Connection()
        query = """
            INSERT INTO emprestimos (id_exemplar, observacoes, status)
            VALUES (%s, %s, 'ativo')
        """
        return db.execute(query, (id_exemplar, observacoes))

    @staticmethod
    def finalizar_emprestimo_ativo(id_exemplar):
        """Ao devolver o exemplar, finaliza o empréstimo ativo mais recente."""
        db = Connection()
        query = """
            UPDATE emprestimos
            SET status='finalizado', data_devolucao=NOW()
            WHERE id_exemplar=%s AND status='ativo'
        """
        db.execute(query, (id_exemplar,))

    @staticmethod
    def historico_por_exemplar(id_exemplar):
        """RF-018: Consultar histórico de empréstimos de um exemplar."""
        db = Connection()
        query = """
            SELECT * FROM emprestimos
            WHERE id_exemplar=%s
            ORDER BY data_emprestimo DESC
        """
        return db.execute(query, (id_exemplar,), fetch=True)