# controllers/exemplar_controller.py

from models.exemplar_model import Exemplar
from models.emprestimo_model import Emprestimo
from utils.gerenciador_fotos import remover_foto


class ExemplarController:

    def listar_por_livro(self, id_livro):
        """Usado em livros_view.py (JanelaExemplares) para listar os exemplares de uma obra específica."""
        return Exemplar.listar_por_livro(id_livro)

    def listar_todos(self, filtro=""):
        """Usado em emprestimos_view.py para listar todos os exemplares do acervo, com filtro de busca."""
        return Exemplar.listar_todos(filtro)

    def buscar_por_id(self, id_exemplar):
        """Usado internamente e no FormExemplar, para carregar dados na edição."""
        return Exemplar.buscar_por_id(id_exemplar)

    def sugerir_codigo(self, id_livro):
        """Usado em FormExemplar, para sugerir um código de tombo ao cadastrar um novo exemplar."""
        return Exemplar.proximo_codigo_sugerido(id_livro)

    def salvar_exemplar(self, id_livro, dados, id_usuario, id_exemplar=None):
        """
        Salva um exemplar (novo ou existente).

        Ao mudar o status em relação ao valor anterior, registra
        automaticamente um novo item no histórico de empréstimos,
        com usuário, data e observação.
        """
        status_anterior = None

        if id_exemplar:
            exemplar_atual = Exemplar.buscar_por_id(id_exemplar)
            if exemplar_atual:
                status_anterior = exemplar_atual["status"]

        if not dados.get("codigo_tombo"):
            return False, "O código do exemplar é obrigatório."

        if dados["status"] in ("em_uso", "emprestado") and not dados.get("observacao"):
            return False, "Observações são obrigatórias quando o status é 'Em uso' ou 'Emprestado'."

        try:
            if id_exemplar:
                Exemplar.atualizar(id_exemplar, dados)
            else:
                id_exemplar = Exemplar.salvar(id_livro, dados)
        except Exception as e:
            return False, f"Erro ao salvar exemplar: {e}"

        status_mudou = status_anterior is None or status_anterior != dados["status"]

        if status_mudou:
            try:
                Emprestimo.registrar(id_exemplar, id_usuario, dados.get("observacao") or "")
            except Exception as e:
                return True, f"Exemplar salvo, mas houve um erro ao registrar o histórico: {e}"

        return True, None

    def excluir_exemplar(self, id_exemplar):
        """Usado em livros_view.py (JanelaExemplares), com validação básica antes de remover."""
        try:
            exemplar = Exemplar.buscar_por_id(id_exemplar)
            if exemplar and exemplar.get("foto_path"):
                remover_foto(exemplar["foto_path"])
            Exemplar.excluir(id_exemplar)
            return True, None
        except Exception as e:
            return False, f"Erro ao excluir exemplar: {e}"