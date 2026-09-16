# models/exemplar_model.py

from database.connection import Connection


class Exemplar:
    """
    Model da entidade EXEMPLARES.
    Representa cada cópia física de um livro (obra), com sua própria
    localização, foto, status de circulação e código de identificação.
    """

    @staticmethod
    def listar_por_livro(id_livro):
        db = Connection()
        query = """
            SELECT ex.*, p.nome_prateleira, e.nome_estante
            FROM exemplares ex
            LEFT JOIN prateleiras p ON ex.id_prateleira = p.id_prateleira
            LEFT JOIN estantes e ON p.id_estante = e.id_estante
            WHERE ex.id_livro = %s
            ORDER BY ex.codigo_tombo
        """
        return db.execute(query, (id_livro,), fetch=True)

    @staticmethod
    def listar_todos(filtro=""):
        """
        Lista todos os exemplares do acervo, com dados da obra (título, autores)
        já unidos — usado na tela de Empréstimos, que opera por exemplar.
        """
        db = Connection()
        query = """
            SELECT
                ex.id_exemplar, ex.codigo_tombo, ex.status, ex.observacao, ex.foto_path,
                l.id_livro, l.titulo, l.isbn,
                p.nome_prateleira, e.nome_estante,
                GROUP_CONCAT(DISTINCT a.nome_autor ORDER BY a.nome_autor SEPARATOR ', ') AS autores
            FROM exemplares ex
            JOIN livros l ON l.id_livro = ex.id_livro
            LEFT JOIN livro_autores la ON la.id_livro = l.id_livro
            LEFT JOIN autores a ON a.id_autor = la.id_autor
            LEFT JOIN prateleiras p ON ex.id_prateleira = p.id_prateleira
            LEFT JOIN estantes e ON p.id_estante = e.id_estante
            WHERE l.titulo LIKE %s OR a.nome_autor LIKE %s OR l.isbn LIKE %s
            GROUP BY ex.id_exemplar
            ORDER BY l.titulo, ex.codigo_tombo
        """
        termo = f"%{filtro}%"
        return db.execute(query, (termo, termo, termo), fetch=True)

    @staticmethod
    def buscar_por_id(id_exemplar):
        db = Connection()
        query = "SELECT * FROM exemplares WHERE id_exemplar = %s"
        return db.execute(query, (id_exemplar,), fetchone=True)

    @staticmethod
    def codigo_tombo_existe(codigo, ignorar_id=None):
        """RN: o código de identificação do exemplar deve ser único."""
        if not codigo:
            return False
        db = Connection()
        if ignorar_id:
            query = "SELECT id_exemplar FROM exemplares WHERE codigo_tombo = %s AND id_exemplar != %s"
            row = db.execute(query, (codigo, ignorar_id), fetchone=True)
        else:
            query = "SELECT id_exemplar FROM exemplares WHERE codigo_tombo = %s"
            row = db.execute(query, (codigo,), fetchone=True)
        return row is not None

    @staticmethod
    def proximo_codigo_sugerido(id_livro):
        """Gera automaticamente um código de tombo sugerido (ex: LIV-3-002)."""
        db = Connection()
        query = "SELECT COUNT(*) as total FROM exemplares WHERE id_livro = %s"
        row = db.execute(query, (id_livro,), fetchone=True)
        proximo_numero = (row["total"] if row else 0) + 1
        return f"LIV-{id_livro}-{proximo_numero:03d}"

    @staticmethod
    def salvar(id_livro, dados):
        """Cadastra um novo exemplar (cópia física) vinculado a uma obra existente."""
        db = Connection()
        query = """
            INSERT INTO exemplares
            (id_livro, codigo_tombo, id_prateleira, foto_path, status, observacao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            id_livro, dados.get("codigo_tombo"), dados.get("id_prateleira"),
            dados.get("foto_path"), dados.get("status", "disponivel"),
            dados.get("observacao", ""),
        )
        return db.execute(query, params)

    @staticmethod
    def atualizar(id_exemplar, dados):
        db = Connection()
        query = """
            UPDATE exemplares
            SET codigo_tombo=%s, id_prateleira=%s, foto_path=%s, status=%s, observacao=%s
            WHERE id_exemplar=%s
        """
        params = (
            dados.get("codigo_tombo"), dados.get("id_prateleira"),
            dados.get("foto_path"), dados.get("status", "disponivel"),
            dados.get("observacao", ""), id_exemplar,
        )
        db.execute(query, params)

    @staticmethod
    def atualizar_status(id_exemplar, status, observacao):
        """RF-015: Alterar status de circulação de um exemplar específico."""
        db = Connection()
        query = "UPDATE exemplares SET status=%s, observacao=%s WHERE id_exemplar=%s"
        db.execute(query, (status, observacao, id_exemplar))

    @staticmethod
    def excluir(id_exemplar):
        db = Connection()
        db.execute("DELETE FROM exemplares WHERE id_exemplar=%s", (id_exemplar,))