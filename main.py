# main.py

import tkinter as tk
from views.login_view import LoginView
from views.main_view import MainView
from config import APP_NAME


class AcerviaApp(tk.Tk):
    """
    Classe raiz da aplicação Acervia.
    Gerencia a troca entre a tela de Login e a tela Principal.
    """

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x650")
        self.minsize(900, 600)
        self._exibir_login()

    def _exibir_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        LoginView(self, self._on_login_success).pack(fill="both", expand=True)

    def _on_login_success(self, usuario, usuario_controller):
        for widget in self.winfo_children():
            widget.destroy()
        MainView(self, usuario, usuario_controller, self._exibir_login).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = AcerviaApp()
    app.mainloop()