# models/usuario_model.py — com correção no encadeamento do lastrowid

from database.connection import Connection


class Usuario:
    """
    Model responsável pelo acesso e persistência de dados de usuários.
    Corresponde às entidades USUARIOS e PERMISSOES do DER.
    """

    def __init__(self, id_usuario=None, nome_completo="", login="", senha="",
                 perfil="operador", ativo=True, permissoes=None):
        self.id_usuario = id_usuario
        self.nome_completo = nome_completo
        self.login = login
        self.senha = senha
        self.perfil = perfil
        self.ativo = ativo
        self.permissoes = permissoes or {}

    @staticmethod
    def autenticar(login, senha):
        """RF-010: Autenticação de usuário por login e senha."""
        db = Connection()
        query = "SELECT * FROM usuarios WHERE login = %s AND senha = %s AND ativo = TRUE"
        row = db.execute(query, (login, senha), fetchone=True)
        if not row:
            return None
        usuario = Usuario(
            id_usuario=row["id_usuario"],
            nome_completo=row["nome_completo"],
            login=row["login"],
            senha=row["senha"],
            perfil=row["perfil"],
            ativo=row["ativo"],
        )
        usuario.permissoes = Usuario.buscar_permissoes(usuario.id_usuario)
        return usuario

    @staticmethod
    def buscar_permissoes(id_usuario):
        db = Connection()
        query = "SELECT * FROM permissoes WHERE id_usuario = %s"
        row = db.execute(query, (id_usuario,), fetchone=True)
        if not row:
            return {}
        return {
            "cadastrar": bool(row["cadastrar"]),
            "alterar": bool(row["alterar"]),
            "excluir": bool(row["excluir"]),
            "emprestimo": bool(row["emprestimo"]),
            "gerenciar_localizacao": bool(row["gerenciar_localizacao"]),
            "gerenciar_usuarios": bool(row["gerenciar_usuarios"]),
        }

    @staticmethod
    def listar_todos():
        """RF-006: Listagem de usuários cadastrados."""
        db = Connection()
        query = "SELECT * FROM usuarios ORDER BY nome_completo"
        usuarios = db.execute(query, fetch=True)
        for u in usuarios:
            u["permissoes"] = Usuario.buscar_permissoes(u["id_usuario"])
        return usuarios

    @staticmethod
    def buscar_por_login(login):
        db = Connection()
        query = "SELECT * FROM usuarios WHERE login = %s"
        return db.execute(query, (login,), fetchone=True)

    @staticmethod
    def salvar(dados):
        """
        RF-006: Criar novo usuário. RN-007/RN-008 validadas no Controller.
        Correção: o id_usuario retornado pelo INSERT é validado antes
        de ser usado para inserir as permissões, evitando gravação
        de permissões "órfãs" caso o INSERT do usuário falhe silenciosamente.
        """
        db = Connection()
        query = """
            INSERT INTO usuarios (nome_completo, login, senha, perfil, ativo)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (dados["nome_completo"], dados["login"], dados["senha"],
                   dados["perfil"], dados["ativo"])
        id_usuario = db.execute(query, params)

        if not id_usuario:
            raise Exception("Não foi possível obter o ID do novo usuário após o INSERT.")

        Usuario._salvar_permissoes(id_usuario, dados.get("permissoes", {}))
        return id_usuario

    @staticmethod
    def atualizar(id_usuario, dados):
        """RF-008: Alterar dados de usuário existente."""
        db = Connection()
        query = """
            UPDATE usuarios
            SET nome_completo=%s, login=%s, senha=%s, perfil=%s, ativo=%s
            WHERE id_usuario=%s
        """
        params = (dados["nome_completo"], dados["login"], dados["senha"],
                   dados["perfil"], dados["ativo"], id_usuario)
        db.execute(query, params)

        db.execute("DELETE FROM permissoes WHERE id_usuario=%s", (id_usuario,))
        Usuario._salvar_permissoes(id_usuario, dados.get("permissoes", {}))

    @staticmethod
    def _salvar_permissoes(id_usuario, permissoes):
        db = Connection()
        query = """
            INSERT INTO permissoes
            (id_usuario, cadastrar, alterar, excluir, emprestimo, gerenciar_localizacao, gerenciar_usuarios)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            id_usuario,
            bool(permissoes.get("cadastrar", False)),
            bool(permissoes.get("alterar", False)),
            bool(permissoes.get("excluir", False)),
            bool(permissoes.get("emprestimo", False)),
            bool(permissoes.get("gerenciar_localizacao", False)),
            bool(permissoes.get("gerenciar_usuarios", False)),
        )
        db.execute(query, params)

    @staticmethod
    def excluir(id_usuario):
        """RF-009: Excluir usuário do sistema."""
        db = Connection()
        db.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))