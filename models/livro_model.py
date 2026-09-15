# models/livro_model.py

from database.connection import Connection
from models.autor_model import Autor


class Livro:
    """
    Model da entidade LIVROS.
    Representa a OBRA (dados bibliográficos), não a cópia física.
    Cada livro pode ter vários exemplares e vários autores.
    """

    @staticmethod
    def listar_todos(filtro=""):
        """
        RF-002: Consultar/buscar livros por título, autor ou ISBN.
        Retorna a lista de obras já com os nomes de autores concatenados
        e a contagem de exemplares (total e disponíveis).
        """
        db = Connection()
        query = """
            SELECT
                l.id_livro, l.titulo, l.isbn, l.ano_publicacao, l.genero,
                GROUP_CONCAT(DISTINCT a.nome_autor ORDER BY a.nome_autor SEPARATOR ', ') AS autores,
                COUNT(DISTINCT ex.id_exemplar) AS total_exemplares,
                SUM(CASE WHEN ex.status = 'disponivel' THEN 1 ELSE 0 END) AS exemplares_disponiveis
            FROM livros l
            LEFT JOIN livro_autores la ON la.id_livro = l.id_livro
            LEFT JOIN autores a ON a.id_autor = la.id_autor
            LEFT JOIN exemplares ex ON ex.id_livro = l.id_livro
            WHERE l.titulo LIKE %s OR a.nome_autor LIKE %s OR l.isbn LIKE %s
            GROUP BY l.id_livro
            ORDER BY l.titulo
        """
        termo = f"%{filtro}%"
        return db.execute(query, (termo, termo, termo), fetch=True)

    @staticmethod
    def buscar_por_id(id_livro):
        db = Connection()
        query = "SELECT * FROM livros WHERE id_livro = %s"
        livro = db.execute(query, (id_livro,), fetchone=True)
        if livro:
            livro["autores"] = Autor.listar_por_livro(id_livro)
        return livro

    @staticmethod
    def buscar_por_titulo_isbn(titulo, isbn):
        """Ajuda a evitar cadastro de obra duplicada."""
        db = Connection()
        if isbn:
            query = "SELECT * FROM livros WHERE isbn = %s"
            return db.execute(query, (isbn,), fetchone=True)
        query = "SELECT * FROM livros WHERE titulo = %s"
        return db.execute(query, (titulo,), fetchone=True)

    @staticmethod
    def isbn_existe(isbn, ignorar_id=None):
        """RN-006: O ISBN, se informado, deve ser único no sistema."""
        if not isbn:
            return False
        db = Connection()
        if ignorar_id:
            query = "SELECT id_livro FROM livros WHERE isbn = %s AND id_livro != %s"
            row = db.execute(query, (isbn, ignorar_id), fetchone=True)
        else:
            query = "SELECT id_livro FROM livros WHERE isbn = %s"
            row = db.execute(query, (isbn,), fetchone=True)
        return row is not None

    @staticmethod
    def salvar(dados, id_usuario_cadastro):
        """
        RF-001/RF-003: Catalogar e incluir nova obra.
        Agora salva apenas os dados bibliográficos; autores são vinculados
        separadamente via Autor.vincular_ao_livro().
        """
        db = Connection()
        query = """
            INSERT INTO livros (titulo, isbn, ano_publicacao, genero, id_usuario_cadastro)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            dados["titulo"], dados.get("isbn") or None,
            dados.get("ano_publicacao"), dados.get("genero"),
            id_usuario_cadastro,
        )
        id_livro = db.execute(query, params)

        Autor.vincular_ao_livro(id_livro, dados.get("autores", []))
        return id_livro

    @staticmethod
    def atualizar(id_livro, dados):
        """RF-004: Alterar dados bibliográficos da obra."""
        db = Connection()
        query = """
            UPDATE livros
            SET titulo=%s, isbn=%s, ano_publicacao=%s, genero=%s
            WHERE id_livro=%s
        """
        params = (
            dados["titulo"], dados.get("isbn") or None,
            dados.get("ano_publicacao"), dados.get("genero"),
            id_livro,
        )
        db.execute(query, params)
        Autor.vincular_ao_livro(id_livro, dados.get("autores", []))

    @staticmethod
    def excluir(id_livro):
        """
        RF-005: Excluir a obra do acervo.
        Os exemplares associados são removidos em cascata pelo banco de dados.
        """
        db = Connection()
        db.execute("DELETE FROM livros WHERE id_livro=%s", (id_livro,))

    @staticmethod
    def contar_por_status():
        """Contagem de exemplares (cópias físicas) por status, para o dashboard do Acervo."""
        db = Connection()
        query = "SELECT status, COUNT(*) as total FROM exemplares GROUP BY status"
        rows = db.execute(query, fetch=True)
        contagem = {"disponivel": 0, "em_uso": 0, "emprestado": 0}
        for r in rows:
            contagem[r["status"]] = r["total"]
        return contagem