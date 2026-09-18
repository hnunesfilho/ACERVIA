# models/emprestimo_model.py

from database.connection import Connection


class Emprestimo:
    """
    Model da entidade EMPRESTIMOS.
    Registra o histórico de alterações de status de um exemplar,
    incluindo o usuário responsável, a data e as observações.
    """

    @staticmethod
    def registrar(id_exemplar, id_usuario, observacoes):
        """
        RF-016/RF-017: Registrar mudança de status com data automática
        e usuário responsável pela alteração.
        """
        db = Connection()
        query = """
            INSERT INTO emprestimos (id_exemplar, id_usuario, observacoes, status)
            VALUES (%s, %s, %s, 'ativo')
        """
        return db.execute(query, (id_exemplar, id_usuario, observacoes))

    @staticmethod
    def finalizar_emprestimo_ativo(id_exemplar):
        """Ao devolver o exemplar, finaliza o registro de empréstimo ativo mais recente."""
        db = Connection()
        query = """
            UPDATE emprestimos
            SET status='finalizado', data_devolucao=NOW()
            WHERE id_exemplar=%s AND status='ativo'
        """
        db.execute(query, (id_exemplar,))

    @staticmethod
    def ultima_alteracao_por_exemplar(id_exemplar):
        """
        Retorna o registro mais recente de alteração de status de um exemplar,
        já com o nome do usuário responsável, para exibição na tela de Empréstimos.
        """
        db = Connection()
        query = """
            SELECT e.*, u.nome_completo AS nome_usuario
            FROM emprestimos e
            LEFT JOIN usuarios u ON u.id_usuario = e.id_usuario
            WHERE e.id_exemplar = %s
            ORDER BY e.data_emprestimo DESC
            LIMIT 1
        """
        return db.execute(query, (id_exemplar,), fetchone=True)

    @staticmethod
    def historico_por_exemplar(id_exemplar):
        """RF-018: Consultar histórico completo de alterações de um exemplar."""
        db = Connection()
        query = """
            SELECT e.*, u.nome_completo AS nome_usuario
            FROM emprestimos e
            LEFT JOIN usuarios u ON u.id_usuario = e.id_usuario
            WHERE e.id_exemplar = %s
            ORDER BY e.data_emprestimo DESC
        """
        return db.execute(query, (id_exemplar,), fetch=True)