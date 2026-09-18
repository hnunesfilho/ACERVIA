# views/livros_view.py — arquivo completo, com Obra/Exemplar/Múltiplos Autores

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from controllers.livro_controller import LivroController
from controllers.exemplar_controller import ExemplarController
from controllers.localizacao_controller import LocalizacaoController
from config import COLORS
from utils.gerenciador_fotos import salvar_foto, caminho_completo_foto, remover_foto
from utils.gerenciador_fotos import caminho_completo_foto

from utils.gerenciador_fotos import remover_foto

GENEROS = ["Ficção", "Romance", "Naturalismo", "Poesia", "Biografia",
           "Técnico", "Infantil", "Histórico", "Fantasia", "Suspense"]

STATUS_LABELS = {"disponivel": "Disponível", "em_uso": "Em uso", "emprestado": "Emprestado"}
STATUS_CORES = {"disponivel": "#15803d", "em_uso": "#c2410c", "emprestado": "#b91c1c"}
STATUS_FUNDOS = {"disponivel": "#dcfce7", "em_uso": "#fff7ed", "emprestado": "#fee2e2"}


class LivrosView(tk.Frame):
    """
    UC-002/003/004/005: Cadastrar, Consultar, Alterar e Excluir OBRAS.
    Cada card representa um título (obra), exibindo quantos exemplares
    existem e quantos estão disponíveis no momento.
    """

    def __init__(self, master, usuario, usuario_controller):
        super().__init__(master, bg=COLORS["background"])
        self.usuario = usuario
        self.usuario_controller = usuario_controller
        self.livro_controller = LivroController()
        self.exemplar_controller = ExemplarController()
        self.loc_controller = LocalizacaoController()
        self.imagens_cache = []
        self._montar_interface()
        self._carregar_livros()

    def _montar_interface(self):
        header = tk.Frame(self, bg=COLORS["background"])
        header.pack(fill="x", padx=20, pady=15)

        info = tk.Frame(header, bg=COLORS["background"])
        info.pack(side="left")
        tk.Label(info, text="Acervo de Livros", font=("Segoe UI", 14, "bold"),
                  bg=COLORS["background"], fg=COLORS["text_dark"]).pack(anchor="w")
        self.label_total = tk.Label(info, font=("Segoe UI", 9),
                  bg=COLORS["background"], fg=COLORS["text_gray"])
        self.label_total.pack(anchor="w")

        if self.usuario_controller.tem_permissao("cadastrar"):
            tk.Button(
                header, text="+ Novo Livro", font=("Segoe UI", 10, "bold"),
                bg=COLORS["primary"], fg="white", relief="flat", padx=15, pady=6,
                cursor="hand2", command=self._abrir_form_novo
            ).pack(side="right")

        busca = tk.Frame(self, bg=COLORS["background"])
        busca.pack(fill="x", padx=20)
        self.entry_busca = tk.Entry(busca, font=("Segoe UI", 10))
        self.entry_busca.pack(fill="x", ipady=4)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar_livros())

        container = tk.Frame(self, bg=COLORS["background"])
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.frame_cards = tk.Frame(self.canvas, bg=COLORS["background"])

        self.janela_cards = self.canvas.create_window((0, 0), window=self.frame_cards, anchor="nw")
        self.frame_cards.bind("<Configure>", self._atualizar_scrollregion)
        self.canvas.bind("<Configure>", self._ajustar_largura_cards)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _atualizar_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_largura_cards(self, event):
        self.canvas.itemconfig(self.janela_cards, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _carregar_livros(self):
        filtro = self.entry_busca.get()
        livros = self.livro_controller.listar_livros(filtro)

        for widget in self.frame_cards.winfo_children():
            widget.destroy()
        self.imagens_cache.clear()

        colunas_por_linha = 4
        for indice, livro in enumerate(livros):
            linha = indice // colunas_por_linha
            coluna = indice % colunas_por_linha
            self._criar_card(livro, linha, coluna)

        self.frame_cards.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        contagem = self.livro_controller.contar_por_status()
        total_titulos = len(livros)
        self.label_total.config(
            text=f"{total_titulos} títulos · {contagem['disponivel']} exemplares disponíveis · "
                 f"{contagem['em_uso']} em uso · {contagem['emprestado']} emprestados"
        )

    def _carregar_primeira_foto(self, id_livro, largura=140, altura=180):
        """Usa a foto do primeiro exemplar cadastrado, apenas para representar o card da obra."""
        try:
            exemplares = self.exemplar_controller.listar_por_livro(id_livro)
            for ex in exemplares:
                if ex.get("foto_path"):
                    img = Image.open(ex["foto_path"])
                    img = img.resize((largura, altura))
                    foto_tk = ImageTk.PhotoImage(img)
                    self.imagens_cache.append(foto_tk)
                    return foto_tk
        except Exception:
            pass
        return None

    def _criar_card(self, livro, linha, coluna):
        card = tk.Frame(self.frame_cards, bg="white", bd=1, relief="solid", width=170, height=300)
        card.grid(row=linha, column=coluna, padx=8, pady=8, sticky="n")
        card.grid_propagate(False)

        frame_capa = tk.Frame(card, bg="#e2e8f0", width=170, height=170)
        frame_capa.pack(fill="x")
        frame_capa.pack_propagate(False)

        foto_tk = self._carregar_primeira_foto(livro["id_livro"])
        if foto_tk:
            tk.Label(frame_capa, image=foto_tk, bg="#e2e8f0").pack(fill="both", expand=True)
        else:
            tk.Label(frame_capa, text="📖", font=("Segoe UI", 32),
                      bg="#1c3f4a", fg="white").pack(fill="both", expand=True)

        total = livro["total_exemplares"] or 0
        disponiveis = livro["exemplares_disponiveis"] or 0
        tk.Label(
            card, text=f"{disponiveis}/{total} disponíveis", font=("Segoe UI", 7, "bold"),
            bg="#dcfce7" if disponiveis > 0 else "#fee2e2",
            fg="#15803d" if disponiveis > 0 else "#b91c1c",
            padx=5, pady=1
        ).pack(anchor="w", padx=6, pady=(4, 0))

        tk.Label(card, text=livro["titulo"], font=("Segoe UI", 9, "bold"),
                  bg="white", wraplength=155, justify="left").pack(anchor="w", padx=6, pady=(2, 0))

        autores_texto = livro.get("autores") or "Autor não informado"
        tk.Label(card, text=autores_texto, font=("Segoe UI", 8),
                  bg="white", fg=COLORS["text_gray"], wraplength=155, justify="left"
                  ).pack(anchor="w", padx=6)

        tk.Label(card, text=livro["isbn"] or "-", font=("Segoe UI", 7),
                  bg="white", fg="#94a3b8").pack(anchor="w", padx=6, pady=(2, 4))

        frame_acoes = tk.Frame(card, bg="white")
        frame_acoes.pack(fill="x", padx=6, pady=(0, 6), side="bottom")

        tk.Button(frame_acoes, text="Exemplares", font=("Segoe UI", 7),
                   bg="#e0f2fe", fg="#0369a1", relief="flat", cursor="hand2",
                   command=lambda l=livro: self._abrir_exemplares(l)
                   ).pack(side="left", fill="x", expand=True, padx=(0, 2))

        if self.usuario_controller.tem_permissao("alterar"):
            tk.Button(frame_acoes, text="Editar", font=("Segoe UI", 7),
                       bg="#e8f5f2", fg=COLORS["primary"], relief="flat", cursor="hand2",
                       command=lambda l=livro: self._abrir_form_editar(l["id_livro"])
                       ).pack(side="left", fill="x", expand=True, padx=(2, 2))

        if self.usuario_controller.tem_permissao("excluir"):
            tk.Button(frame_acoes, text="Excluir", font=("Segoe UI", 7),
                       bg="#fee2e2", fg="#b91c1c", relief="flat", cursor="hand2",
                       command=lambda l=livro: self._excluir(l["id_livro"], l["titulo"])
                       ).pack(side="left", fill="x", expand=True, padx=(2, 0))

    def _abrir_form_novo(self):
        FormLivro(self, self.livro_controller, self.usuario.id_usuario, on_salvar=self._carregar_livros)

    def _abrir_form_editar(self, id_livro):
        FormLivro(self, self.livro_controller, self.usuario.id_usuario,
                   id_livro=id_livro, on_salvar=self._carregar_livros)

    def _abrir_exemplares(self, livro):
        JanelaExemplares(self, livro, self.exemplar_controller, self.loc_controller,
                           self.usuario_controller, on_atualizar=self._carregar_livros)

    def _excluir(self, id_livro, titulo):
        if messagebox.askyesno(
            "Confirmar exclusão",
            f'Deseja excluir "{titulo}"?\nTodos os exemplares desta obra também serão removidos.'
        ):
            self.livro_controller.excluir_livro(id_livro)
            self._carregar_livros()

    # views/livros_view.py — trecho ajustado dentro da classe LivrosView

    def _excluir(self, id_livro, titulo):
        if messagebox.askyesno(
            "Confirmar exclusão",
            f'Deseja excluir "{titulo}"?\nTodos os exemplares desta obra também serão removidos.'
        ):
            sucesso, erro = self.livro_controller.excluir_livro(id_livro)
            if not sucesso:
                messagebox.showerror("Exclusão não permitida", erro)
                return
            self._carregar_livros()

    def _carregar_primeira_foto(self, id_livro, largura=140, altura=180):
        """
        Usa a foto do primeiro exemplar cadastrado, apenas para representar
        o card da obra. Monta o caminho completo a partir do nome do arquivo
        salvo na pasta interna do projeto.
        """
        try:
            exemplares = self.exemplar_controller.listar_por_livro(id_livro)
            for ex in exemplares:
                if ex.get("foto_path"):
                    caminho = caminho_completo_foto(ex["foto_path"])
                    img = Image.open(caminho)
                    img = img.resize((largura, altura))
                    foto_tk = ImageTk.PhotoImage(img)
                    self.imagens_cache.append(foto_tk)
                    return foto_tk
        except Exception:
            pass
        return None


class FormLivro(tk.Toplevel):
    """
    UC-002/UC-004: Formulário de Cadastro/Alteração da OBRA (dados bibliográficos).
    Suporta múltiplos autores através de uma lista editável.
    """

    def __init__(self, master, livro_controller, id_usuario, id_livro=None, on_salvar=None):
        super().__init__(master)
        self.title("Editar Livro" if id_livro else "Novo Livro")
        self.geometry("440x560")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.livro_controller = livro_controller
        self.id_usuario = id_usuario
        self.id_livro = id_livro
        self.on_salvar = on_salvar
        self.lista_autores = []  # lista de nomes de autores adicionados

        self.frame_rodape = tk.Frame(self, bg="white")
        self.frame_rodape.pack(fill="x", side="bottom")
        tk.Frame(self.frame_rodape, height=1, bg="#e2e8f0").pack(fill="x", side="top")
        botoes_container = tk.Frame(self.frame_rodape, bg="white")
        botoes_container.pack(fill="x", padx=15, pady=12)

        tk.Button(botoes_container, text="Cancelar", command=self.destroy,
                   bg="#f1f5f9", relief="flat", padx=15, pady=6).pack(side="left")
        tk.Button(botoes_container, text="Salvar", command=self._salvar,
                   bg=COLORS["primary"], fg="white", relief="flat", padx=15, pady=6,
                   cursor="hand2").pack(side="right")

        container_corpo = tk.Frame(self)
        container_corpo.pack(fill="both", expand=True, side="top")

        self.canvas = tk.Canvas(container_corpo, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_corpo, orient="vertical", command=self.canvas.yview)
        self.frame_corpo = tk.Frame(self.canvas)

        self.janela_corpo = self.canvas.create_window((0, 0), window=self.frame_corpo, anchor="nw")
        self.frame_corpo.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.janela_corpo, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._montar_form()
        if id_livro:
            self._carregar_dados(id_livro)

    def _montar_form(self):
        self.entry_titulo = self._campo("Título *")
        self.entry_isbn = self._campo("ISBN")
        self.entry_ano = self._campo("Ano de Publicação")

        tk.Label(self.frame_corpo, text="Gênero", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.combo_genero = ttk.Combobox(self.frame_corpo, values=GENEROS, state="readonly")
        self.combo_genero.set(GENEROS[0])
        self.combo_genero.pack(fill="x", padx=15, pady=(0, 10))

        # ── Seção de Autores (múltiplos) ────────────────────────────────
        tk.Label(self.frame_corpo, text="Autores *", font=("Segoe UI", 8, "bold")
                  ).pack(anchor="w", padx=15, pady=(0, 3))

        frame_add_autor = tk.Frame(self.frame_corpo)
        frame_add_autor.pack(fill="x", padx=15, pady=(0, 5))

        self.entry_novo_autor = tk.Entry(frame_add_autor, font=("Segoe UI", 9))
        self.entry_novo_autor.pack(side="left", fill="x", expand=True, ipady=3)
        self.entry_novo_autor.bind("<Return>", lambda e: self._adicionar_autor())

        tk.Button(frame_add_autor, text="+ Adicionar", command=self._adicionar_autor,
                   bg="#e8f5f2", fg=COLORS["primary"], relief="flat", cursor="hand2"
                   ).pack(side="left", padx=(5, 0))

        self.frame_lista_autores = tk.Frame(self.frame_corpo, bg="#f8fafc", bd=1, relief="solid")
        self.frame_lista_autores.pack(fill="x", padx=15, pady=(0, 10))

        self.label_sem_autor = tk.Label(
            self.frame_lista_autores, text="Nenhum autor adicionado ainda",
            font=("Segoe UI", 8), fg=COLORS["text_gray"], bg="#f8fafc"
        )
        self.label_sem_autor.pack(pady=8)

    def _campo(self, label):
        tk.Label(self.frame_corpo, text=label, font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        entry = tk.Entry(self.frame_corpo, font=("Segoe UI", 10))
        entry.pack(fill="x", padx=15, pady=(0, 8), ipady=3)
        return entry

    def _adicionar_autor(self):
        nome = self.entry_novo_autor.get().strip()
        if not nome:
            return
        if nome in self.lista_autores:
            messagebox.showwarning("Atenção", "Este autor já foi adicionado.")
            return
        self.lista_autores.append(nome)
        self.entry_novo_autor.delete(0, "end")
        self._atualizar_lista_autores()

    def _remover_autor(self, nome):
        self.lista_autores.remove(nome)
        self._atualizar_lista_autores()

    def _atualizar_lista_autores(self):
        for widget in self.frame_lista_autores.winfo_children():
            widget.destroy()

        if not self.lista_autores:
            self.label_sem_autor = tk.Label(
                self.frame_lista_autores, text="Nenhum autor adicionado ainda",
                font=("Segoe UI", 8), fg=COLORS["text_gray"], bg="#f8fafc"
            )
            self.label_sem_autor.pack(pady=8)
            return

        for nome in self.lista_autores:
            linha = tk.Frame(self.frame_lista_autores, bg="#f8fafc")
            linha.pack(fill="x", padx=8, pady=3)
            tk.Label(linha, text=f"• {nome}", font=("Segoe UI", 9),
                      bg="#f8fafc", anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(linha, text="✕", font=("Segoe UI", 8), fg="#b91c1c",
                       bg="#f8fafc", relief="flat", cursor="hand2", bd=0,
                       command=lambda n=nome: self._remover_autor(n)
                       ).pack(side="right")

    def _carregar_dados(self, id_livro):
        livro = self.livro_controller.buscar_livro(id_livro)
        if not livro:
            return
        self.entry_titulo.insert(0, livro["titulo"])
        self.entry_isbn.insert(0, livro["isbn"] or "")
        self.entry_ano.insert(0, str(livro["ano_publicacao"] or ""))
        self.combo_genero.set(livro["genero"] or GENEROS[0])

        self.lista_autores = [a["nome_autor"] for a in livro.get("autores", [])]
        self._atualizar_lista_autores()

    def _salvar(self):
        dados = {
            "titulo": self.entry_titulo.get().strip(),
            "isbn": self.entry_isbn.get().strip(),
            "ano_publicacao": self.entry_ano.get().strip() or None,
            "genero": self.combo_genero.get(),
            "autores": self.lista_autores,
        }

        sucesso, erro, id_livro_salvo = self.livro_controller.salvar_livro(
            dados, self.id_usuario, id_livro=self.id_livro)

        if not sucesso:
            messagebox.showerror("Erro de validação", erro)
            return

        messagebox.showinfo("Sucesso", "Livro salvo com sucesso!\nAgora adicione ao menos um exemplar.")
        if self.on_salvar:
            self.on_salvar()
        self.destroy()


class JanelaExemplares(tk.Toplevel):
    """
    Nova tela: gerencia os EXEMPLARES (cópias físicas) de uma obra específica.
    Resolve o cenário de "mais de uma cópia do mesmo livro".
    """

    def __init__(self, master, livro, exemplar_controller, loc_controller,
                 usuario_controller, on_atualizar=None):
        super().__init__(master)
        self.title(f"Exemplares — {livro['titulo']}")
        self.geometry("560x480")
        self.transient(master)
        self.grab_set()
        self.livro = livro
        self.exemplar_controller = exemplar_controller
        self.loc_controller = loc_controller
        self.usuario_controller = usuario_controller
        self.on_atualizar = on_atualizar

        self._montar_interface()
        self._carregar()

    def _montar_interface(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=15, pady=15)
        tk.Label(header, text=self.livro["titulo"], font=("Segoe UI", 12, "bold")
                  ).pack(anchor="w")
        tk.Label(header, text=self.livro.get("autores") or "Autor não informado",
                  font=("Segoe UI", 9), fg=COLORS["text_gray"]).pack(anchor="w")

        if self.usuario_controller.tem_permissao("cadastrar"):
            tk.Button(header, text="+ Novo Exemplar", command=self._novo_exemplar,
                       bg=COLORS["primary"], fg="white", relief="flat", padx=12, pady=5,
                       cursor="hand2").pack(anchor="e", pady=(8, 0))

        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        colunas = ("codigo", "local", "status", "observacao")
        self.tree = ttk.Treeview(container, columns=colunas, show="headings", height=12)
        for c, t, w in [("codigo", "Código", 100), ("local", "Localização", 150),
                          ("status", "Status", 100), ("observacao", "Observações", 180)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True)

        acoes = tk.Frame(self)
        acoes.pack(fill="x", padx=15, pady=(0, 15))
        tk.Button(acoes, text="Editar", command=self._editar_exemplar).pack(side="left", padx=(0, 5))
        tk.Button(acoes, text="Excluir", command=self._excluir_exemplar).pack(side="left")

    def _carregar(self):
        self.tree.delete(*self.tree.get_children())
        exemplares = self.exemplar_controller.listar_por_livro(self.livro["id_livro"])
        for ex in exemplares:
            local = f"{ex.get('nome_prateleira') or '-'} / {ex.get('nome_estante') or '-'}"
            self.tree.insert("", "end", iid=ex["id_exemplar"], values=(
                ex["codigo_tombo"] or "-", local,
                STATUS_LABELS.get(ex["status"], ex["status"]), ex["observacao"] or "-"
            ))

    def _novo_exemplar(self):
        FormExemplar(self, self.livro, self.exemplar_controller, self.loc_controller,
                      on_salvar=self._on_salvo)

    def _editar_exemplar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um exemplar.")
            return
        FormExemplar(self, self.livro, self.exemplar_controller, self.loc_controller,
                      id_exemplar=int(sel[0]), on_salvar=self._on_salvo)

    def _excluir_exemplar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um exemplar.")
            return
        codigo = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f'Excluir o exemplar "{codigo}"?'):
            self.exemplar_controller.excluir_exemplar(int(sel[0]))
            self._on_salvo()

    def _on_salvo(self):
        self._carregar()
        if self.on_atualizar:
            self.on_atualizar()

  

# views/livros_view.py — versão final e mais simples deste trecho

    def _excluir_exemplar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um exemplar.")
            return
        codigo = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f'Excluir o exemplar "{codigo}"?'):
            sucesso, erro = self.exemplar_controller.excluir_exemplar(int(sel[0]))
            if not sucesso:
                messagebox.showerror("Exclusão não permitida", erro)
                return
            self._on_salvo()


class FormExemplar(tk.Toplevel):
    """Formulário de Cadastro/Alteração de um EXEMPLAR (cópia física) de um livro."""

    def __init__(self, master, livro, exemplar_controller, loc_controller,
                 id_exemplar=None, on_salvar=None):
        super().__init__(master)
        self.title("Editar Exemplar" if id_exemplar else "Novo Exemplar")
        self.geometry("400x600")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.livro = livro
        self.exemplar_controller = exemplar_controller
        self.loc_controller = loc_controller
        self.id_exemplar = id_exemplar
        self.on_salvar = on_salvar
        self.foto_path = None          # nome do arquivo salvo (o que vai para o banco)
        self.foto_path_antigo = None   # guarda o nome anterior, para remover se for trocada
        self.foto_preview_tk = None

        self.frame_rodape = tk.Frame(self, bg="white")
        self.frame_rodape.pack(fill="x", side="bottom")
        tk.Frame(self.frame_rodape, height=1, bg="#e2e8f0").pack(fill="x", side="top")
        botoes_container = tk.Frame(self.frame_rodape, bg="white")
        botoes_container.pack(fill="x", padx=15, pady=12)
        tk.Button(botoes_container, text="Cancelar", command=self.destroy,
                   bg="#f1f5f9", relief="flat", padx=15, pady=6).pack(side="left")
        tk.Button(botoes_container, text="Salvar", command=self._salvar,
                   bg=COLORS["primary"], fg="white", relief="flat", padx=15, pady=6,
                   cursor="hand2").pack(side="right")

        self.frame_corpo = tk.Frame(self)
        self.frame_corpo.pack(fill="both", expand=True)

        self._montar_form()
        if id_exemplar:
            self._carregar_dados(id_exemplar)
        else:
            sugestao = self.exemplar_controller.sugerir_codigo(self.livro["id_livro"])
            self.entry_codigo.insert(0, sugestao)

    def _montar_form(self):
        tk.Label(self.frame_corpo, text="Código do Exemplar", font=("Segoe UI", 8)
                  ).pack(anchor="w", padx=15, pady=(15, 0))
        self.entry_codigo = tk.Entry(self.frame_corpo, font=("Segoe UI", 10))
        self.entry_codigo.pack(fill="x", padx=15, pady=(0, 8), ipady=3)

        tk.Label(self.frame_corpo, text="Status", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.combo_status = ttk.Combobox(
            self.frame_corpo, values=list(STATUS_LABELS.values()), state="readonly")
        self.combo_status.set("Disponível")
        self.combo_status.pack(fill="x", padx=15, pady=(0, 8))

        prateleiras = self.loc_controller.listar_prateleiras()
        self.mapa_prateleiras = {f"{p['nome_prateleira']} ({p['nome_estante']})": p["id_prateleira"]
                                   for p in prateleiras}
        tk.Label(self.frame_corpo, text="Localização (Prateleira)", font=("Segoe UI", 8)
                  ).pack(anchor="w", padx=15)
        self.combo_local = ttk.Combobox(
            self.frame_corpo, values=list(self.mapa_prateleiras.keys()), state="readonly")
        self.combo_local.pack(fill="x", padx=15, pady=(0, 8))

        tk.Label(self.frame_corpo, text="Observações", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.text_obs = tk.Text(self.frame_corpo, height=3, font=("Segoe UI", 9))
        self.text_obs.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(self.frame_corpo, text="Foto do Exemplar", font=("Segoe UI", 8, "bold")
                  ).pack(anchor="w", padx=15, pady=(0, 5))

        frame_foto = tk.Frame(self.frame_corpo, bg="#f8fafc", bd=1, relief="solid")
        frame_foto.pack(fill="x", padx=15, pady=(0, 10))

        self.frame_preview = tk.Frame(frame_foto, bg="#e2e8f0", width=110, height=140)
        self.frame_preview.pack(side="left", padx=12, pady=12)
        self.frame_preview.pack_propagate(False)

        self.label_preview = tk.Label(self.frame_preview, text="📷", font=("Segoe UI", 24),
                                        bg="#e2e8f0", fg="#94a3b8")
        self.label_preview.pack(fill="both", expand=True)

        frame_lateral = tk.Frame(frame_foto, bg="#f8fafc")
        frame_lateral.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=12)

        tk.Button(frame_lateral, text="📁 Escolher foto", command=self._escolher_foto,
                   bg="white", relief="solid", bd=1, pady=6, cursor="hand2").pack(fill="x")

        self.label_status_foto = tk.Label(
            frame_lateral, text="Nenhuma foto selecionada", font=("Segoe UI", 8),
            bg="#f8fafc", fg=COLORS["text_gray"], wraplength=180, justify="left")
        self.label_status_foto.pack(anchor="w", pady=(8, 0))

    def _escolher_foto(self):
        """
        Ao escolher a foto, copia imediatamente o arquivo para a pasta interna
        do projeto (fotos_exemplares) e passa a trabalhar apenas com o nome
        gerado, garantindo que a imagem viaje junto com o projeto/banco de dados.
        """
        caminho_original = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if not caminho_original:
            return

        try:
            nome_arquivo_salvo = salvar_foto(caminho_original)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar a foto para o projeto: {e}")
            return

        self.foto_path = nome_arquivo_salvo
        self._atualizar_preview(caminho_completo_foto(nome_arquivo_salvo))

    def _atualizar_preview(self, caminho_completo):
        try:
            img = Image.open(caminho_completo)
            img = img.resize((110, 140))
            self.foto_preview_tk = ImageTk.PhotoImage(img)
            self.label_preview.config(image=self.foto_preview_tk, text="", bg="white")
            self.label_status_foto.config(text="✓ Foto carregada", fg="#15803d")
        except Exception as e:
            self.label_preview.config(image="", text="⚠", bg="#fee2e2", fg="#b91c1c")
            self.label_status_foto.config(text=f"Erro ao carregar a imagem: {e}", fg="#b91c1c")
            self.foto_path = None

    def _carregar_dados(self, id_exemplar):
        exemplares = self.exemplar_controller.listar_por_livro(self.livro["id_livro"])
        ex = next((e for e in exemplares if e["id_exemplar"] == id_exemplar), None)
        if not ex:
            return
        self.entry_codigo.insert(0, ex["codigo_tombo"] or "")
        self.combo_status.set(STATUS_LABELS.get(ex["status"], "Disponível"))
        self.text_obs.insert("1.0", ex["observacao"] or "")

        # foto_path armazenado no banco já é apenas o NOME do arquivo
        self.foto_path = ex["foto_path"]
        self.foto_path_antigo = ex["foto_path"]

        if self.foto_path:
            caminho = caminho_completo_foto(self.foto_path)
            if caminho:
                self._atualizar_preview(caminho)

        if ex.get("nome_prateleira"):
            chave = f"{ex['nome_prateleira']} ({ex['nome_estante']})"
            self.combo_local.set(chave)

    def _salvar(self):
        status_invertido = {v: k for k, v in STATUS_LABELS.items()}
        local_selecionado = self.combo_local.get()

        dados = {
            "codigo_tombo": self.entry_codigo.get().strip(),
            "status": status_invertido.get(self.combo_status.get(), "disponivel"),
            "observacao": self.text_obs.get("1.0", "end").strip(),
            "id_prateleira": self.mapa_prateleiras.get(local_selecionado),
            "foto_path": self.foto_path,  # apenas o nome do arquivo, não o caminho completo
        }

        sucesso, erro = self.exemplar_controller.salvar_exemplar(
            self.livro["id_livro"], dados, id_exemplar=self.id_exemplar)

        if not sucesso:
            messagebox.showerror("Erro de validação", erro)
            return

        # Se a foto foi trocada (havia uma foto antiga diferente da nova),
        # remove o arquivo antigo da pasta para não acumular fotos órfãs.
        if self.foto_path_antigo and self.foto_path_antigo != self.foto_path:
            remover_foto(self.foto_path_antigo)

        messagebox.showinfo("Sucesso", "Exemplar salvo com sucesso!")
        if self.on_salvar:
            self.on_salvar()
        self.destroy()