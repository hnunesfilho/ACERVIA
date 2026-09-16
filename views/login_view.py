# views/login_view.py

import tkinter as tk
from tkinter import Image, messagebox
from PIL import Image, ImageTk
from controllers.usuario_controller import UsuarioController
from config import APP_NAME, COLORS


class LoginView(tk.Frame):
    """
    UC-001: Fazer Login.
    Réplica funcional da tela de login criada no Figma.
    """

    def __init__(self, master, on_login_success):
        super().__init__(master, bg="#B4E9EF")
        self.master = master
        self.on_login_success = on_login_success
        self.usuario_controller = UsuarioController()
        self._montar_interface()

    def _montar_interface(self):

        # Impedir redimensionamento da janela
        self.master.resizable(False, False)

        # Container principal
        main = tk.Frame(self, bg="#B4E9EF")
        main.pack(fill="both", expand=True)

        # Painel esquerdo (logo)
        left_frame = tk.Frame(main, bg="#B4E9EF")
        left_frame.pack(side="left", fill="both", expand=True)

        # Painel direito (branco)
        right_frame = tk.Frame(main, bg="#1c3f4a", width=450)
        right_frame.pack(side="right", fill="y")

        # ========= LOGO =========
        img = Image.open("assets/acervia2.jpg")
        img = img.resize((450, 400))

        self.logo_img = ImageTk.PhotoImage(img)

        tk.Label(
            left_frame,
            image=self.logo_img,
            bg="#B4E9EF"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ========= CARD LOGIN =========
        card = tk.Frame(right_frame, bg="#1c3f4a")
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="Acesso ao sistema",
            font=("Segoe UI", 14, "bold"),
            bg="#1c3f4a",
            fg="white"
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(
            card,
            text="LOGIN",
            bg="#1c3f4a",
            fg="white"
        ).pack(anchor="w")

        self.entry_login = tk.Entry(card, width=30)
        self.entry_login.pack(pady=(0, 15))

        tk.Label(
            card,
            text="SENHA",
            bg="#1c3f4a",
            fg="white"
        ).pack(anchor="w")

        self.entry_senha = tk.Entry(card, show="*", width=30)
        self.entry_senha.pack(pady=(0, 20))

        tk.Button(
            card,
            text="Entrar no sistema",
            bg="#2D8AA6",
            fg="white",
            width=25,
            command=self._fazer_login
        ).pack()

        tk.Label(
            card, 
            text="admin / admin123", 
            font=("Segoe UI", 8),
            bg="#1c3f4a", 
            fg="#94a3b8"
        ).pack(pady=(10, 0))

        self.entry_login.focus()

    def _fazer_login(self):
        login = self.entry_login.get().strip()
        senha = self.entry_senha.get().strip()

        usuario, erro = self.usuario_controller.login(login, senha)
        if erro:
            messagebox.showerror("Erro de autenticação", erro)
            return

        self.on_login_success(usuario, self.usuario_controller)