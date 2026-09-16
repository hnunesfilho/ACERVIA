# controllers/emprestimo_controller.py

from models.exemplar_model import Exemplar
from models.emprestimo_model import Emprestimo


class EmprestimoController:
    """Controller responsável pelas regras de negócio de empréstimos por exemplar."""

    def alterar_status(self, id_exemplar, novo_status, observacao):
        """
        UC-012/UC-013: Alterar status do exemplar e registrar empréstimo.
        RN-010: Status deve ser Disponível, Em uso ou Emprestado.
        RN-011: Observação obrigatória para status "emprestado".
        RN-012: Data do empréstimo registrada automaticamente.
        """
        if novo_status not in ("disponivel", "em_uso", "emprestado"):
            return False, "Status inválido."

        if novo_status == "emprestado" and not observacao.strip():
            return False, "As observações são obrigatórias para o status 'Emprestado'."

        exemplar_atual = Exemplar.buscar_por_id(id_exemplar)

        if novo_status == "disponivel":
            observacao = ""
            if exemplar_atual and exemplar_atual["status"] == "emprestado":
                Emprestimo.finalizar_emprestimo_ativo(id_exemplar)
        elif novo_status == "emprestado":
            Emprestimo.registrar(id_exemplar, observacao)

        Exemplar.atualizar_status(id_exemplar, novo_status, observacao)
        return True, None

    def historico(self, id_exemplar):
        return Emprestimo.historico_por_exemplar(id_exemplar)