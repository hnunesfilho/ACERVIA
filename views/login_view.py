# views/login_view.py

import tkinter as tk
from tkinter import messagebox
from controllers.usuario_controller import UsuarioController
from config import APP_NAME, COLORS


class LoginView(tk.Frame):
    """
    UC-001: Fazer Login.
    Réplica funcional da tela de login criada no Figma.
    """

    def __init__(self, master, on_login_success):
        super().__init__(master, bg=COLORS["sidebar"])
        self.master = master
        self.on_login_success = on_login_success
        self.usuario_controller = UsuarioController()
        self._montar_interface()

    def _montar_interface(self):
        container = tk.Frame(self, bg=COLORS["sidebar"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / título
        tk.Label(
            container, text="📚", font=("Segoe UI", 40),
            bg="#c5e8e0", width=4, height=2
        ).pack(pady=(0, 10))

        tk.Label(
            container, text=APP_NAME, font=("Segoe UI", 16, "bold"),
            bg=COLORS["sidebar"], fg="white"
        ).pack()

        tk.Label(
            container, text="ORGANIZE SEU MUNDO LITERÁRIO",
            font=("Segoe UI", 9), bg=COLORS["sidebar"], fg="#a8d4c8"
        ).pack(pady=(0, 20))

        # Card branco de login
        card = tk.Frame(container, bg="white", padx=30, pady=25)
        card.pack()

        tk.Label(
            card, text="Acesso ao sistema", font=("Segoe UI", 11, "bold"),
            bg="white", fg=COLORS["text_dark"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        tk.Label(card, text="LOGIN", font=("Segoe UI", 8), bg="white",
                 fg=COLORS["text_gray"]).grid(row=1, column=0, sticky="w")
        self.entry_login = tk.Entry(card, font=("Segoe UI", 10), width=30)
        self.entry_login.grid(row=2, column=0, pady=(2, 10))

        tk.Label(card, text="SENHA", font=("Segoe UI", 8), bg="white",
                 fg=COLORS["text_gray"]).grid(row=3, column=0, sticky="w")
        self.entry_senha = tk.Entry(card, font=("Segoe UI", 10), width=30, show="•")
        self.entry_senha.grid(row=4, column=0, pady=(2, 15))
        self.entry_senha.bind("<Return>", lambda e: self._fazer_login())

        btn_entrar = tk.Button(
            card, text="Entrar no sistema", font=("Segoe UI", 10, "bold"),
            bg=COLORS["primary"], fg="white", relief="flat", pady=8,
            activebackground=COLORS["primary_dark"], cursor="hand2",
            command=self._fazer_login
        )
        btn_entrar.grid(row=5, column=0, sticky="ew")

        tk.Label(
            card, text="admin / admin123", font=("Segoe UI", 8),
            bg="white", fg="#94a3b8"
        ).grid(row=6, column=0, pady=(10, 0))

        self.entry_login.focus()

    def _fazer_login(self):
        login = self.entry_login.get().strip()
        senha = self.entry_senha.get().strip()

        usuario, erro = self.usuario_controller.login(login, senha)
        if erro:
            messagebox.showerror("Erro de autenticação", erro)
            return

        self.on_login_success(usuario, self.usuario_controller)