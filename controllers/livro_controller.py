# controllers/livro_controller.py

from models.livro_model import Livro
from models.exemplar_model import Exemplar


class LivroController:
    """Controller responsável pelas regras de negócio da OBRA (livro)."""

    def listar_livros(self, filtro=""):
        """UC-003: Consultar Livro (obra), com contagem de exemplares."""
        return Livro.listar_todos(filtro)

    def buscar_livro(self, id_livro):
        return Livro.buscar_por_id(id_livro)

    def contar_por_status(self):
        return Livro.contar_por_status()

    def salvar_livro(self, dados, id_usuario_cadastro, id_livro=None):
        """
        UC-002/UC-004: Cadastrar ou Alterar a obra (dados bibliográficos).
        RN-005: Título é obrigatório.
        RN-006: ISBN deve ser único, se informado.
        RN-016 (nova): Pelo menos um autor deve ser informado.
        """
        if not dados.get("titulo", "").strip():
            return False, "O título é obrigatório.", None

        autores = [a.strip() for a in dados.get("autores", []) if a.strip()]
        if not autores:
            return False, "Informe pelo menos um autor.", None

        isbn = (dados.get("isbn") or "").strip()
        if isbn and Livro.isbn_existe(isbn, ignorar_id=id_livro):
            return False, "Este ISBN já está cadastrado no sistema.", None

        dados["autores"] = autores

        try:
            if id_livro:
                Livro.atualizar(id_livro, dados)
            else:
                id_livro = Livro.salvar(dados, id_usuario_cadastro)
        except Exception as e:
            return False, f"Erro ao salvar no banco de dados: {e}", None

        return True, None, id_livro

    def excluir_livro(self, id_livro):
        """
        UC-005: Excluir Livro (obra).
        Todos os exemplares dessa obra são removidos em cascata.
        """
        try:
            Livro.excluir(id_livro)
        except Exception as e:
            return False, f"Erro ao excluir: {e}"
        return True, None