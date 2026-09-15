# models/autor_model.py

from database.connection import Connection


class Autor:
    """
    Model da entidade AUTORES.
    Um autor pode estar vinculado a vários livros (relação N:N via LIVRO_AUTORES).
    """

    @staticmethod
    def listar_todos():
        db = Connection()
        return db.execute("SELECT * FROM autores ORDER BY nome_autor", fetch=True)

    @staticmethod
    def buscar_por_nome(nome):
        db = Connection()
        query = "SELECT * FROM autores WHERE nome_autor = %s"
        return db.execute(query, (nome,), fetchone=True)

    @staticmethod
    def obter_ou_criar(nome):
        """
        Retorna o id_autor existente, ou cria um novo autor caso o nome
        ainda não esteja cadastrado. Evita duplicidade de nomes.
        """
        nome = nome.strip()
        existente = Autor.buscar_por_nome(nome)
        if existente:
            return existente["id_autor"]

        db = Connection()
        return db.execute("INSERT INTO autores (nome_autor) VALUES (%s)", (nome,))

    @staticmethod
    def listar_por_livro(id_livro):
        db = Connection()
        query = """
            SELECT a.* FROM autores a
            JOIN livro_autores la ON la.id_autor = a.id_autor
            WHERE la.id_livro = %s
            ORDER BY a.nome_autor
        """
        return db.execute(query, (id_livro,), fetch=True)

    @staticmethod
    def vincular_ao_livro(id_livro, lista_nomes_autores):
        """
        Recebe uma lista de nomes de autores (strings), garante que cada um
        exista na tabela AUTORES, e vincula todos ao livro informado.
        RN: um livro deve ter pelo menos um autor (validado no Controller).
        """
        db = Connection()
        db.execute("DELETE FROM livro_autores WHERE id_livro = %s", (id_livro,))

        for nome in lista_nomes_autores:
            nome = nome.strip()
            if not nome:
                continue
            id_autor = Autor.obter_ou_criar(nome)
            db.execute(
                "INSERT INTO livro_autores (id_livro, id_autor) VALUES (%s, %s)",
                (id_livro, id_autor),
            )