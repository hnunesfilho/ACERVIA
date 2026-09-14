# controllers/emprestimo_controller.py

from models.livro_model import Livro
from models.emprestimo_model import Emprestimo


class EmprestimoController:
    """Controller responsável pelas regras de negócio de empréstimos."""

    def alterar_status(self, id_livro, novo_status, observacao):
        """
        UC-012/UC-013: Alterar status do livro e registrar empréstimo.
        RN-010: Status deve ser Disponível, Em uso ou Emprestado.
        RN-011: Observação obrigatória para status "emprestado".
        RN-012: Data do empréstimo registrada automaticamente.
        """
        if novo_status not in ("disponivel", "em_uso", "emprestado"):
            return False, "Status inválido."

        if novo_status == "emprestado" and not observacao.strip():
            return False, "As observações são obrigatórias para o status 'Emprestado'."

        livro_atual = Livro.buscar_por_id(id_livro)

        if novo_status == "disponivel":
            observacao = ""
            if livro_atual and livro_atual["status"] == "emprestado":
                Emprestimo.finalizar_emprestimo_ativo(id_livro)
        elif novo_status == "emprestado":
            Emprestimo.registrar(id_livro, observacao)

        Livro.atualizar_status(id_livro, novo_status, observacao)
        return True, None

    def historico(self, id_livro):
        """UC: Consultar histórico de empréstimos."""
        return Emprestimo.historico_por_livro(id_livro)