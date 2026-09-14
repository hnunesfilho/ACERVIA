# controllers/livro_controller.py

from models.livro_model import Livro


class LivroController:
    """Controller responsável pelas regras de negócio de livros."""

    def listar_livros(self, filtro=""):
        """UC-003: Consultar Livro."""
        return Livro.listar_todos(filtro)

    def contar_por_status(self):
        return Livro.contar_por_status()

    def salvar_livro(self, dados, id_usuario_cadastro, id_livro=None):
        """
        UC-002/UC-004: Cadastrar ou Alterar Livro.
        RN-005: Título e autor são obrigatórios.
        RN-006: ISBN deve ser único, se informado.
        RN-011: Status "em_uso"/"emprestado" exige observação.
        """
        if not dados.get("titulo", "").strip() or not dados.get("autor", "").strip():
            return False, "Título e autor são obrigatórios."

        isbn = dados.get("isbn", "").strip()
        if isbn and Livro.isbn_existe(isbn, ignorar_id=id_livro):
            return False, "Este ISBN já está cadastrado no sistema."

        status = dados.get("status", "disponivel")
        if status in ("em_uso", "emprestado") and not dados.get("observacao", "").strip():
            return False, "Observações são obrigatórias para os status 'Em uso' ou 'Emprestado'."

        if status == "disponivel":
            dados["observacao"] = ""

        if id_livro:
            Livro.atualizar(id_livro, dados)
        else:
            Livro.salvar(dados, id_usuario_cadastro)

        return True, None

    def excluir_livro(self, id_livro):
        """UC-005: Excluir Livro."""
        Livro.excluir(id_livro)
        return True, None