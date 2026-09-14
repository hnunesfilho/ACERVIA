# controllers/usuario_controller.py — com tratamento de exceção

from models.usuario_model import Usuario


class UsuarioController:
    """
    Controller responsável por validar as regras de negócio (RN)
    relacionadas a usuários antes de repassar ao Model.
    """

    def __init__(self):
        self.usuario_logado = None

    def login(self, login, senha):
        """UC-001: Fazer Login."""
        if not login or not senha:
            return None, "Login e senha são obrigatórios."

        usuario = Usuario.autenticar(login, senha)
        if not usuario:
            return None, "Login ou senha inválidos, ou usuário inativo."

        self.usuario_logado = usuario
        return usuario, None

    def tem_permissao(self, permissao):
        """Verifica se o usuário logado tem determinada permissão."""
        if not self.usuario_logado:
            return False
        if self.usuario_logado.perfil == "admin":
            return True
        return self.usuario_logado.permissoes.get(permissao, False)

    def listar_usuarios(self):
        return Usuario.listar_todos()

    def salvar_usuario(self, dados, id_usuario=None):
        """
        UC-006/UC-007: Criar ou alterar usuário.
        RN-001: Apenas administradores podem gerenciar usuários (validado na View/Controller de acesso).
        RN-007: Login deve ser único.
        RN-008: Senha deve ter no mínimo 6 caracteres.
        """
        if not dados.get("nome_completo") or not dados.get("login") or not dados.get("senha"):
            return False, "Nome, login e senha são obrigatórios."

        if len(dados["senha"]) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres."

        existente = Usuario.buscar_por_login(dados["login"])
        if existente and (id_usuario is None or existente["id_usuario"] != id_usuario):
            return False, "Este login já está em uso por outro usuário."

        try:
            if id_usuario:
                Usuario.atualizar(id_usuario, dados)
            else:
                Usuario.salvar(dados)
        except Exception as e:
            # Antes, uma falha aqui era engolida silenciosamente.
            # Agora o erro real do banco de dados é reportado à View.
            return False, f"Erro ao salvar no banco de dados: {e}"

        return True, None

    def excluir_usuario(self, id_usuario, id_usuario_logado):
        """RF-009: Excluir usuário (impede autoexclusão)."""
        if id_usuario == id_usuario_logado:
            return False, "Não é possível excluir seu próprio usuário."
        try:
            Usuario.excluir(id_usuario)
        except Exception as e:
            return False, f"Erro ao excluir usuário: {e}"
        return True, None