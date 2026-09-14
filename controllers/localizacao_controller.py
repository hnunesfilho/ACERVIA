# controllers/localizacao_controller.py

from models.localizacao_model import Estante, Prateleira


class LocalizacaoController:
    """Controller responsável pelas regras de negócio de estantes e prateleiras."""

    def listar_estantes(self):
        return Estante.listar_todas()

    def listar_prateleiras(self):
        return Prateleira.listar_todas()

    def salvar_estante(self, nome, id_estante=None):
        """UC-006/UC-008: Criar ou editar estante."""
        nome = nome.strip()
        if not nome:
            return False, "O nome da estante não pode ser vazio."
        if Estante.existe(nome, ignorar_id=id_estante):
            return False, "Já existe uma estante com este nome."

        if id_estante:
            Estante.atualizar(id_estante, nome)
        else:
            Estante.salvar(nome)
        return True, None

    def excluir_estante(self, id_estante):
        """UC-010: Deletar estante (prateleiras filhas removidas em cascata pelo BD)."""
        Estante.excluir(id_estante)
        return True, None

    def salvar_prateleira(self, id_estante, nome, id_prateleira=None):
        """
        UC-007/UC-009: Criar ou editar prateleira.
        RN-013: Cada prateleira pertence a uma única estante (nome único por estante).
        """
        nome = nome.strip()
        if not id_estante:
            return False, "Selecione uma estante."
        if not nome:
            return False, "O nome da prateleira não pode ser vazio."
        if Prateleira.existe(id_estante, nome, ignorar_id=id_prateleira):
            return False, "Já existe uma prateleira com este nome nesta estante."

        if id_prateleira:
            Prateleira.atualizar(id_prateleira, id_estante, nome)
        else:
            Prateleira.salvar(id_estante, nome)
        return True, None

    def excluir_prateleira(self, id_prateleira):
        """UC-011: Deletar prateleira."""
        Prateleira.excluir(id_prateleira)
        return True, None