# views/main_view.py

import tkinter as tk
from config import APP_NAME, APP_VERSION, COLORS
from views.livros_view import LivrosView
from views.usuarios_view import UsuariosView
from views.localizacoes_view import LocalizacoesView
from views.emprestimos_view import EmprestimosView


class MainView(tk.Frame):
    """
    Menu principal (shell) com navegação lateral,
    réplica da estrutura de sidebar vista no Figma.
    """

    def __init__(self, master, usuario, usuario_controller, on_logout):
        super().__init__(master, bg=COLORS["background"])
        self.master = master
        self.usuario = usuario
        self.usuario_controller = usuario_controller
        self.on_logout = on_logout

        self.frame_conteudo = None
        self._montar_sidebar()
        self._montar_topbar()
        self._montar_area_conteudo()
        self.exibir_acervo()

    # ── Sidebar ──────────────────────────────────────────────────────
    def _montar_sidebar(self):
        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        header = tk.Frame(sidebar, bg=COLORS["sidebar"])
        header.pack(fill="x", pady=15, padx=15)
        tk.Label(header, text="📚", font=("Segoe UI", 16), bg="#c5e8e0", width=2).pack(side="left")
        info = tk.Frame(header, bg=COLORS["sidebar"])
        info.pack(side="left", padx=8)
        tk.Label(info, text=APP_NAME, font=("Segoe UI", 11, "bold"),
                  bg=COLORS["sidebar"], fg="white").pack(anchor="w")
        tk.Label(info, text=APP_VERSION, font=("Segoe UI", 8),
                  bg=COLORS["sidebar"], fg=COLORS["sidebar_text"]).pack(anchor="w")

        tk.Label(sidebar, text="MÓDULOS", font=("Segoe UI", 8, "bold"),
                  bg=COLORS["sidebar"], fg="#5a8d88").pack(anchor="w", padx=18, pady=(10, 5))

        self._botao_menu(sidebar, "📖  Acervo", self.exibir_acervo)

        if self.usuario_controller.tem_permissao("emprestimo"):
            self._botao_menu(sidebar, "🤝  Empréstimos", self.exibir_emprestimos)

        if self.usuario_controller.tem_permissao("gerenciar_localizacao"):
            self._botao_menu(sidebar, "📍  Localizações", self.exibir_localizacoes)

        if self.usuario_controller.tem_permissao("gerenciar_usuarios"):
            self._botao_menu(sidebar, "👥  Usuários", self.exibir_usuarios)

        # Rodapé com usuário logado
        rodape = tk.Frame(sidebar, bg=COLORS["sidebar"])
        rodape.pack(side="bottom", fill="x", pady=15, padx=15)
        tk.Label(rodape, text=self.usuario.nome_completo, font=("Segoe UI", 9, "bold"),
                  bg=COLORS["sidebar"], fg="#cce8e2").pack(anchor="w")
        tk.Label(rodape, text="Administrador" if self.usuario.perfil == "admin" else "Operador",
                  font=("Segoe UI", 8), bg=COLORS["sidebar"], fg="#5a8d88").pack(anchor="w")
        tk.Button(rodape, text="⏻  Sair do sistema", font=("Segoe UI", 8),
                   bg=COLORS["sidebar"], fg="#5a8d88", relief="flat", cursor="hand2",
                   anchor="w", command=self.on_logout).pack(fill="x", pady=(8, 0))

    def _botao_menu(self, parent, texto, comando):
        btn = tk.Button(
            parent, text=texto, font=("Segoe UI", 10), anchor="w",
            bg=COLORS["sidebar"], fg=COLORS["sidebar_text"], relief="flat",
            activebackground=COLORS["sidebar_hover"], cursor="hand2",
            padx=15, pady=8, command=comando
        )
        btn.pack(fill="x", padx=8, pady=1)
        return btn

    # ── Barra superior ───────────────────────────────────────────────
    def _montar_topbar(self):
        self.topbar = tk.Frame(self, bg="white", height=40)
        self.topbar.pack(side="top", fill="x")
        self.label_breadcrumb = tk.Label(
            self.topbar, text="Acervia › Acervo de Livros",
            font=("Segoe UI", 9), bg="white", fg=COLORS["text_gray"]
        )
        self.label_breadcrumb.pack(side="left", padx=20, pady=10)

        tk.Label(
            self.topbar, text="● Banco de dados: Conectado (MySQL)",
            font=("Segoe UI", 8), bg="white", fg="#15803d"
        ).pack(side="right", padx=20)

    # ── Área de conteúdo ─────────────────────────────────────────────
    def _montar_area_conteudo(self):
        self.area = tk.Frame(self, bg=COLORS["background"])
        self.area.pack(side="left", fill="both", expand=True)

    def _limpar_area(self):
        for widget in self.area.winfo_children():
            widget.destroy()

    def exibir_acervo(self):
        self._limpar_area()
        self.label_breadcrumb.config(text="Acervia › Acervo de Livros")
        LivrosView(self.area, self.usuario, self.usuario_controller).pack(fill="both", expand=True)

    def exibir_usuarios(self):
        self._limpar_area()
        self.label_breadcrumb.config(text="Acervia › Usuários do Sistema")
        UsuariosView(self.area, self.usuario).pack(fill="both", expand=True)

    def exibir_localizacoes(self):
        self._limpar_area()
        self.label_breadcrumb.config(text="Acervia › Localizações")
        LocalizacoesView(self.area).pack(fill="both", expand=True)

    

    # views/main_view.py — trecho a ajustar na chamada de EmprestimosView

    def exibir_emprestimos(self):
        self._limpar_area()
        EmprestimosView(self.area, self.usuario).pack(fill="both", expand=True)