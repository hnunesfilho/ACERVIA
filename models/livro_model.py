# models/livro_model.py

from database.connection import Connection


class Livro:
    """
    Model responsável pelo acesso e persistência de dados de livros.
    Corresponde à entidade LIVROS do DER.
    """

    @staticmethod
    def listar_todos(filtro=""):
        """RF-002: Consultar/buscar livros por título, autor ou ISBN."""
        db = Connection()
        query = """
            SELECT l.*, p.nome_prateleira, e.nome_estante
            FROM livros l
            LEFT JOIN prateleiras p ON l.id_prateleira = p.id_prateleira
            LEFT JOIN estantes e ON p.id_estante = e.id_estante
            WHERE l.titulo LIKE %s OR l.autor LIKE %s OR l.isbn LIKE %s
            ORDER BY l.titulo
        """
        termo = f"%{filtro}%"
        return db.execute(query, (termo, termo, termo), fetch=True)

    @staticmethod
    def buscar_por_id(id_livro):
        db = Connection()
        query = "SELECT * FROM livros WHERE id_livro = %s"
        return db.execute(query, (id_livro,), fetchone=True)

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
        """RF-001/RF-003: Catalogar e incluir novo livro."""
        db = Connection()
        query = """
            INSERT INTO livros
            (titulo, autor, isbn, ano_publicacao, genero, id_prateleira,
             foto_path, status, observacao, id_usuario_cadastro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dados["titulo"], dados["autor"], dados.get("isbn") or None,
            dados.get("ano_publicacao"), dados.get("genero"),
            dados.get("id_prateleira"), dados.get("foto_path"),
            dados.get("status", "disponivel"), dados.get("observacao", ""),
            id_usuario_cadastro,
        )
        return db.execute(query, params)

    @staticmethod
    def atualizar(id_livro, dados):
        """RF-004: Alterar dados de livro já cadastrado."""
        db = Connection()
        query = """
            UPDATE livros
            SET titulo=%s, autor=%s, isbn=%s, ano_publicacao=%s, genero=%s,
                id_prateleira=%s, foto_path=%s, status=%s, observacao=%s
            WHERE id_livro=%s
        """
        params = (
            dados["titulo"], dados["autor"], dados.get("isbn") or None,
            dados.get("ano_publicacao"), dados.get("genero"),
            dados.get("id_prateleira"), dados.get("foto_path"),
            dados.get("status", "disponivel"), dados.get("observacao", ""),
            id_livro,
        )
        db.execute(query, params)

    @staticmethod
    def atualizar_status(id_livro, status, observacao):
        """RF-015: Alterar status do livro (Disponível, Em uso, Emprestado)."""
        db = Connection()
        query = "UPDATE livros SET status=%s, observacao=%s WHERE id_livro=%s"
        db.execute(query, (status, observacao, id_livro))

    @staticmethod
    def excluir(id_livro):
        """RF-005: Excluir registro de livro do acervo."""
        db = Connection()
        db.execute("DELETE FROM livros WHERE id_livro=%s", (id_livro,))

    @staticmethod
    def contar_por_status():
        db = Connection()
        query = "SELECT status, COUNT(*) as total FROM livros GROUP BY status"
        rows = db.execute(query, fetch=True)
        contagem = {"disponivel": 0, "em_uso": 0, "emprestado": 0}
        for r in rows:
            contagem[r["status"]] = r["total"]
        return contagem