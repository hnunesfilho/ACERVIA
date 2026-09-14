# views/livros_view.py — arquivo completo corrigido

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from controllers.livro_controller import LivroController
from controllers.localizacao_controller import LocalizacaoController
from config import COLORS

GENEROS = ["Ficção", "Romance", "Naturalismo", "Poesia", "Biografia",
           "Técnico", "Infantil", "Histórico", "Fantasia", "Suspense"]

STATUS_LABELS = {"disponivel": "Disponível", "em_uso": "Em uso", "emprestado": "Emprestado"}
STATUS_CORES = {"disponivel": "#15803d", "em_uso": "#c2410c", "emprestado": "#b91c1c"}
STATUS_FUNDOS = {"disponivel": "#dcfce7", "em_uso": "#fff7ed", "emprestado": "#fee2e2"}


class LivrosView(tk.Frame):
    """
    UC-002/003/004/005: Cadastrar, Consultar, Alterar e Excluir livros.
    Réplica funcional da tela "Acervo de Livros" do Figma, com cards e fotos.
    """

    def __init__(self, master, usuario, usuario_controller):
        super().__init__(master, bg=COLORS["background"])
        self.usuario = usuario
        self.usuario_controller = usuario_controller
        self.livro_controller = LivroController()
        self.loc_controller = LocalizacaoController()
        self.imagens_cache = []  # evita que o Python descarte as imagens (garbage collector)
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

        # Área de rolagem para os cards
        container = tk.Frame(self, bg=COLORS["background"])
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.frame_cards = tk.Frame(self.canvas, bg=COLORS["background"])

        # Guarda o ID da janela criada dentro do canvas para poder ajustar sua largura depois
        self.janela_cards = self.canvas.create_window((0, 0), window=self.frame_cards, anchor="nw")

        self.frame_cards.bind("<Configure>", self._atualizar_scrollregion)
        self.canvas.bind("<Configure>", self._ajustar_largura_cards)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Permite rolar com a roda do mouse sobre a área de cards
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _atualizar_scrollregion(self, event=None):
        """Recalcula a região de rolagem sempre que o conteúdo dos cards mudar."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_largura_cards(self, event):
        """
        Garante que o frame interno de cards sempre ocupe a largura total do canvas,
        evitando que os cards fiquem posicionados fora da área visível.
        """
        self.canvas.itemconfig(self.janela_cards, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _carregar_livros(self):
        filtro = self.entry_busca.get()
        livros = self.livro_controller.listar_livros(filtro)

        # limpa cards antigos
        for widget in self.frame_cards.winfo_children():
            widget.destroy()
        self.imagens_cache.clear()

        colunas_por_linha = 4
        for indice, livro in enumerate(livros):
            linha = indice // colunas_por_linha
            coluna = indice % colunas_por_linha
            self._criar_card(livro, linha, coluna)

        # Garante que a scrollregion seja recalculada mesmo quando há poucos itens
        self.frame_cards.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        contagem = self.livro_controller.contar_por_status()
        total = sum(contagem.values())
        self.label_total.config(
            text=f"{total} livros · {contagem['disponivel']} disponíveis · "
                 f"{contagem['em_uso']} em uso · {contagem['emprestado']} emprestados"
        )

    def _carregar_foto(self, foto_path, largura=140, altura=180):
        """Carrega a foto do disco e retorna um objeto PhotoImage compatível com Tkinter."""
        try:
            if foto_path:
                img = Image.open(foto_path)
                img = img.resize((largura, altura))
                foto_tk = ImageTk.PhotoImage(img)
                self.imagens_cache.append(foto_tk)  # mantém referência viva
                return foto_tk
        except Exception:
            pass
        return None

    def _criar_card(self, livro, linha, coluna):
        card = tk.Frame(self.frame_cards, bg="white", bd=1, relief="solid", width=170, height=290)
        card.grid(row=linha, column=coluna, padx=8, pady=8, sticky="n")
        card.grid_propagate(False)

        # Área da capa
        frame_capa = tk.Frame(card, bg="#e2e8f0", width=170, height=180)
        frame_capa.pack(fill="x")
        frame_capa.pack_propagate(False)

        foto_tk = self._carregar_foto(livro.get("foto_path"))
        if foto_tk:
            tk.Label(frame_capa, image=foto_tk, bg="#e2e8f0").pack(fill="both", expand=True)
        else:
            tk.Label(frame_capa, text="📖", font=("Segoe UI", 32),
                      bg="#1c3f4a", fg="white").pack(fill="both", expand=True)

        status = livro["status"]
        tk.Label(
            card, text=STATUS_LABELS.get(status, status), font=("Segoe UI", 7, "bold"),
            bg=STATUS_FUNDOS.get(status, "#eee"), fg=STATUS_CORES.get(status, "#333"),
            padx=5, pady=1
        ).pack(anchor="w", padx=6, pady=(4, 0))

        tk.Label(card, text=livro["titulo"], font=("Segoe UI", 9, "bold"),
                  bg="white", wraplength=155, justify="left").pack(anchor="w", padx=6, pady=(2, 0))
        tk.Label(card, text=livro["autor"], font=("Segoe UI", 8),
                  bg="white", fg=COLORS["text_gray"]).pack(anchor="w", padx=6)

        local = f"{livro.get('nome_prateleira') or '-'} / {livro.get('nome_estante') or '-'}"
        tk.Label(card, text=local, font=("Segoe UI", 7),
                  bg="white", fg=COLORS["primary"]).pack(anchor="w", padx=6, pady=(2, 0))

        tk.Label(card, text=livro["isbn"] or "-", font=("Segoe UI", 7),
                  bg="white", fg="#94a3b8").pack(anchor="w", padx=6, pady=(0, 4))

        frame_acoes = tk.Frame(card, bg="white")
        frame_acoes.pack(fill="x", padx=6, pady=(0, 6), side="bottom")

        if self.usuario_controller.tem_permissao("alterar"):
            tk.Button(frame_acoes, text="Editar", font=("Segoe UI", 7),
                       bg="#e8f5f2", fg=COLORS["primary"], relief="flat", cursor="hand2",
                       command=lambda l=livro: self._abrir_form_editar(l["id_livro"])
                       ).pack(side="left", fill="x", expand=True, padx=(0, 2))

        if self.usuario_controller.tem_permissao("excluir"):
            tk.Button(frame_acoes, text="Excluir", font=("Segoe UI", 7),
                       bg="#fee2e2", fg="#b91c1c", relief="flat", cursor="hand2",
                       command=lambda l=livro: self._excluir(l["id_livro"], l["titulo"])
                       ).pack(side="left", fill="x", expand=True, padx=(2, 0))

    def _abrir_form_novo(self):
        FormLivro(self, self.livro_controller, self.loc_controller,
                   self.usuario.id_usuario, on_salvar=self._carregar_livros)

    def _abrir_form_editar(self, id_livro):
        FormLivro(self, self.livro_controller, self.loc_controller,
                   self.usuario.id_usuario, id_livro=id_livro, on_salvar=self._carregar_livros)

    def _excluir(self, id_livro, titulo):
        if messagebox.askyesno("Confirmar exclusão", f'Deseja excluir "{titulo}"?'):
            self.livro_controller.excluir_livro(id_livro)
            self._carregar_livros()


class FormLivro(tk.Toplevel):
    """UC-002/UC-004: Formulário de Cadastro/Alteração de Livro."""

    def __init__(self, master, livro_controller, loc_controller, id_usuario,
                 id_livro=None, on_salvar=None):
        super().__init__(master)
        self.title("Editar Livro" if id_livro else "Novo Livro")
        self.geometry("440x650")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.livro_controller = livro_controller
        self.loc_controller = loc_controller
        self.id_usuario = id_usuario
        self.id_livro = id_livro
        self.on_salvar = on_salvar
        self.foto_path = None
        self.foto_preview_tk = None

        # Rodapé com os botões é criado e fixado PRIMEIRO, garantindo que
        # nunca seja empurrado para fora da janela, independente do
        # tamanho do conteúdo do formulário.
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

        # Área central com rolagem, para que o formulário caiba em qualquer
        # altura de tela sem esconder os botões do rodapé
        container_corpo = tk.Frame(self)
        container_corpo.pack(fill="both", expand=True, side="top")

        self.canvas = tk.Canvas(container_corpo, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_corpo, orient="vertical", command=self.canvas.yview)
        self.frame_corpo = tk.Frame(self.canvas)

        self.janela_corpo = self.canvas.create_window((0, 0), window=self.frame_corpo, anchor="nw")

        self.frame_corpo.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
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
        self.entry_autor = self._campo("Autor *")
        self.entry_isbn = self._campo("ISBN")
        self.entry_ano = self._campo("Ano de Publicação")

        tk.Label(self.frame_corpo, text="Gênero", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.combo_genero = ttk.Combobox(self.frame_corpo, values=GENEROS, state="readonly")
        self.combo_genero.set(GENEROS[0])
        self.combo_genero.pack(fill="x", padx=15, pady=(0, 8))

        tk.Label(self.frame_corpo, text="Status", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.combo_status = ttk.Combobox(
            self.frame_corpo, values=list(STATUS_LABELS.values()), state="readonly")
        self.combo_status.set("Disponível")
        self.combo_status.pack(fill="x", padx=15, pady=(0, 8))

        prateleiras = self.loc_controller.listar_prateleiras()
        self.mapa_prateleiras = {f"{p['nome_prateleira']} ({p['nome_estante']})": p["id_prateleira"]
                                   for p in prateleiras}
        tk.Label(self.frame_corpo, text="Localização (Prateleira)", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.combo_local = ttk.Combobox(
            self.frame_corpo, values=list(self.mapa_prateleiras.keys()), state="readonly")
        self.combo_local.pack(fill="x", padx=15, pady=(0, 8))

        tk.Label(self.frame_corpo, text="Observações", font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        self.text_obs = tk.Text(self.frame_corpo, height=3, font=("Segoe UI", 9))
        self.text_obs.pack(fill="x", padx=15, pady=(0, 10))

        # ── Seção de Foto do Livro (com preview visível) ────────────────────
        tk.Label(self.frame_corpo, text="Foto do Livro", font=("Segoe UI", 8, "bold")
                  ).pack(anchor="w", padx=15, pady=(0, 5))

        frame_foto = tk.Frame(self.frame_corpo, bg="#f8fafc", bd=1, relief="solid")
        frame_foto.pack(fill="x", padx=15, pady=(0, 15))

        self.frame_preview = tk.Frame(frame_foto, bg="#e2e8f0", width=110, height=140)
        self.frame_preview.pack(side="left", padx=12, pady=12)
        self.frame_preview.pack_propagate(False)

        self.label_preview = tk.Label(self.frame_preview, text="📷", font=("Segoe UI", 24),
                                        bg="#e2e8f0", fg="#94a3b8")
        self.label_preview.pack(fill="both", expand=True)

        frame_lateral = tk.Frame(frame_foto, bg="#f8fafc")
        frame_lateral.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=12)

        tk.Button(frame_lateral, text="📁 Escolher foto do livro", command=self._escolher_foto,
                   bg="white", relief="solid", bd=1, pady=6, cursor="hand2"
                   ).pack(fill="x")

        self.label_status_foto = tk.Label(
            frame_lateral, text="Nenhuma foto selecionada", font=("Segoe UI", 8),
            bg="#f8fafc", fg=COLORS["text_gray"], wraplength=180, justify="left"
        )
        self.label_status_foto.pack(anchor="w", pady=(8, 0))

        self.btn_remover_foto = tk.Button(
            frame_lateral, text="Remover foto", font=("Segoe UI", 8),
            bg="#f8fafc", fg="#b91c1c", relief="flat", cursor="hand2",
            command=self._remover_foto
        )

    def _campo(self, label):
        tk.Label(self.frame_corpo, text=label, font=("Segoe UI", 8)).pack(anchor="w", padx=15)
        entry = tk.Entry(self.frame_corpo, font=("Segoe UI", 10))
        entry.pack(fill="x", padx=15, pady=(0, 8), ipady=3)
        return entry

    def _escolher_foto(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if caminho:
            self.foto_path = caminho
            self._atualizar_preview(caminho)

    def _atualizar_preview(self, caminho):
        """
        Carrega a imagem escolhida e exibe a miniatura real dentro da
        caixa de preview, confirmando visualmente que o arquivo foi lido
        corretamente antes do usuário clicar em Salvar.
        """
        try:
            img = Image.open(caminho)
            img = img.resize((110, 140))
            self.foto_preview_tk = ImageTk.PhotoImage(img)
            self.label_preview.config(image=self.foto_preview_tk, text="", bg="white")

            nome_arquivo = caminho.split("/")[-1].split("\\")[-1]
            self.label_status_foto.config(
                text=f"✓ Foto carregada:\n{nome_arquivo}", fg="#15803d"
            )
            self.btn_remover_foto.pack(anchor="w", pady=(4, 0))
        except Exception as e:
            self.label_preview.config(image="", text="⚠", bg="#fee2e2", fg="#b91c1c")
            self.label_status_foto.config(
                text=f"Erro ao carregar a imagem: {e}", fg="#b91c1c"
            )
            self.foto_path = None

    def _remover_foto(self):
        """Permite ao usuário descartar a foto escolhida antes de salvar."""
        self.foto_path = None
        self.foto_preview_tk = None
        self.label_preview.config(image="", text="📷", bg="#e2e8f0", fg="#94a3b8")
        self.label_status_foto.config(text="Nenhuma foto selecionada", fg=COLORS["text_gray"])
        self.btn_remover_foto.pack_forget()

    def _carregar_dados(self, id_livro):
        livros = self.livro_controller.listar_livros("")
        livro = next((l for l in livros if l["id_livro"] == id_livro), None)
        if not livro:
            return
        self.entry_titulo.insert(0, livro["titulo"])
        self.entry_autor.insert(0, livro["autor"])
        self.entry_isbn.insert(0, livro["isbn"] or "")
        self.entry_ano.insert(0, str(livro["ano_publicacao"] or ""))
        self.combo_genero.set(livro["genero"] or GENEROS[0])
        self.combo_status.set(STATUS_LABELS.get(livro["status"], "Disponível"))
        self.text_obs.insert("1.0", livro["observacao"] or "")
        self.foto_path = livro["foto_path"]
        if self.foto_path:
            self._atualizar_preview(self.foto_path)

    def _salvar(self):
        status_invertido = {v: k for k, v in STATUS_LABELS.items()}
        local_selecionado = self.combo_local.get()

        dados = {
            "titulo": self.entry_titulo.get().strip(),
            "autor": self.entry_autor.get().strip(),
            "isbn": self.entry_isbn.get().strip(),
            "ano_publicacao": self.entry_ano.get().strip() or None,
            "genero": self.combo_genero.get(),
            "status": status_invertido.get(self.combo_status.get(), "disponivel"),
            "observacao": self.text_obs.get("1.0", "end").strip(),
            "id_prateleira": self.mapa_prateleiras.get(local_selecionado),
            "foto_path": self.foto_path,
        }

        sucesso, erro = self.livro_controller.salvar_livro(
            dados, self.id_usuario, id_livro=self.id_livro)

        if not sucesso:
            messagebox.showerror("Erro de validação", erro)
            return

        messagebox.showinfo("Sucesso", "Livro salvo com sucesso!")
        if self.on_salvar:
            self.on_salvar()
        self.destroy()