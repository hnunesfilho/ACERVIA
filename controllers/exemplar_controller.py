# controllers/exemplar_controller.py

from models.exemplar_model import Exemplar


class ExemplarController:
    """
    Controller responsável pelas regras de negócio de exemplares
    (cópias físicas de uma obra).
    """

    def listar_por_livro(self, id_livro):
        return Exemplar.listar_por_livro(id_livro)

    def listar_todos(self, filtro=""):
        return Exemplar.listar_todos(filtro)

    def sugerir_codigo(self, id_livro):
        return Exemplar.proximo_codigo_sugerido(id_livro)

    def salvar_exemplar(self, id_livro, dados, id_exemplar=None):
        """
        Cadastra ou altera um exemplar (cópia física) de uma obra existente.
        RN-006 (adaptada): o código de tombo, se informado, deve ser único.
        RN-011: Observação obrigatória quando status é "em_uso" ou "emprestado".
        """
        codigo = (dados.get("codigo_tombo") or "").strip()
        if codigo and Exemplar.codigo_tombo_existe(codigo, ignorar_id=id_exemplar):
            return False, "Este código de exemplar já está em uso."

        status = dados.get("status", "disponivel")
        if status in ("em_uso", "emprestado") and not dados.get("observacao", "").strip():
            return False, "Observações são obrigatórias para os status 'Em uso' ou 'Emprestado'."

        if status == "disponivel":
            dados["observacao"] = ""

        try:
            if id_exemplar:
                Exemplar.atualizar(id_exemplar, dados)
            else:
                Exemplar.salvar(id_livro, dados)
        except Exception as e:
            return False, f"Erro ao salvar exemplar: {e}"

        return True, None

    def excluir_exemplar(self, id_exemplar):
        """
        RN-017 (nova, aplicada também no nível do exemplar): não é permitido
        excluir um exemplar específico caso ele esteja "Em uso" ou "Emprestado".
        """
        exemplar = Exemplar.buscar_por_id(id_exemplar)

        if not exemplar:
            return False, "Exemplar não encontrado."

        if exemplar["status"] in ("em_uso", "emprestado"):
            status_label = "em uso" if exemplar["status"] == "em_uso" else "emprestado"
            return False, (
                f"Não é possível excluir este exemplar: ele está atualmente {status_label}. "
                f"Realize a devolução antes de excluir."
            )

        try:
            Exemplar.excluir(id_exemplar)
        except Exception as e:
            return False, f"Erro ao excluir exemplar: {e}"

        return True, None