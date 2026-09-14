# views/localizacoes_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controllers.localizacao_controller import LocalizacaoController
from config import COLORS


class LocalizacoesView(tk.Frame):
    """UC-006/007/008/009/010/011: Gerenciar estantes e prateleiras."""

    def __init__(self, master):
        super().__init__(master, bg=COLORS["background"])
        self.controller = LocalizacaoController()
        self._montar_interface()
        self._carregar()

    def _montar_interface(self):
        header = tk.Frame(self, bg=COLORS["background"])
        header.pack(fill="x", padx=20, pady=15)
        tk.Label(header, text="Localizações", font=("Segoe UI", 14, "bold"),
                  bg=COLORS["background"]).pack(side="left")

        corpo = tk.Frame(self, bg=COLORS["background"])
        corpo.pack(fill="both", expand=True, padx=20)

        # Coluna Prateleiras
        col_prat = tk.Frame(corpo, bg=COLORS["background"])
        col_prat.pack(side="left", fill="both", expand=True, padx=(0, 10))
        top_prat = tk.Frame(col_prat, bg=COLORS["background"])
        top_prat.pack(fill="x")
        tk.Label(top_prat, text="PRATELEIRAS", font=("Segoe UI", 9, "bold"),
                  bg=COLORS["background"]).pack(side="left")
        tk.Button(top_prat, text="+ Nova prateleira", command=self._nova_prateleira,
                   bg="#e8f5f2", fg=COLORS["primary"], relief="flat", cursor="hand2"
                   ).pack(side="right")
        self.lista_prateleiras = ttk.Treeview(
            col_prat, columns=("nome", "estante", "livros"), show="headings", height=12)
        for c, t in [("nome", "Prateleira"), ("estante", "Estante"), ("livros", "Livros")]:
            self.lista_prateleiras.heading(c, text=t)
        self.lista_prateleiras.pack(fill="both", expand=True, pady=5)

        acoes_prat = tk.Frame(col_prat, bg=COLORS["background"])
        acoes_prat.pack(fill="x")
        tk.Button(acoes_prat, text="Editar", command=self._editar_prateleira).pack(side="left", padx=2)
        tk.Button(acoes_prat, text="Excluir", command=self._excluir_prateleira).pack(side="left", padx=2)

        # Coluna Estantes
        col_est = tk.Frame(corpo, bg=COLORS["background"])
        col_est.pack(side="left", fill="both", expand=True, padx=(10, 0))
        top_est = tk.Frame(col_est, bg=COLORS["background"])
        top_est.pack(fill="x")
        tk.Label(top_est, text="ESTANTES", font=("Segoe UI", 9, "bold"),
                  bg=COLORS["background"]).pack(side="left")
        tk.Button(top_est, text="+ Nova estante", command=self._nova_estante,
                   bg="#e8f5f2", fg=COLORS["primary"], relief="flat", cursor="hand2"
                   ).pack(side="right")
        self.lista_estantes = ttk.Treeview(
            col_est, columns=("nome", "livros"), show="headings", height=12)
        for c, t in [("nome", "Estante"), ("livros", "Livros")]:
            self.lista_estantes.heading(c, text=t)
        self.lista_estantes.pack(fill="both", expand=True, pady=5)

        acoes_est = tk.Frame(col_est, bg=COLORS["background"])
        acoes_est.pack(fill="x")
        tk.Button(acoes_est, text="Editar", command=self._editar_estante).pack(side="left", padx=2)
        tk.Button(acoes_est, text="Excluir", command=self._excluir_estante).pack(side="left", padx=2)

    def _carregar(self):
        self.lista_prateleiras.delete(*self.lista_prateleiras.get_children())
        for p in self.controller.listar_prateleiras():
            self.lista_prateleiras.insert("", "end", iid=p["id_prateleira"], values=(
                p["nome_prateleira"], p["nome_estante"], p["total_livros"]))

        self.lista_estantes.delete(*self.lista_estantes.get_children())
        for e in self.controller.listar_estantes():
            self.lista_estantes.insert("", "end", iid=e["id_estante"], values=(
                e["nome_estante"], e["total_livros"]))

    def _nova_estante(self):
        nome = simpledialog.askstring("Nova Estante", "Nome da estante:")
        if nome:
            sucesso, erro = self.controller.salvar_estante(nome)
            if not sucesso:
                messagebox.showerror("Erro", erro)
            self._carregar()

    def _editar_estante(self):
        sel = self.lista_estantes.selection()
        if not sel:
            return
        id_estante = int(sel[0])
        atual = self.lista_estantes.item(sel[0])["values"][0]
        nome = simpledialog.askstring("Editar Estante", "Novo nome:", initialvalue=atual)
        if nome:
            sucesso, erro = self.controller.salvar_estante(nome, id_estante=id_estante)
            if not sucesso:
                messagebox.showerror("Erro", erro)
            self._carregar()

    def _excluir_estante(self):
        sel = self.lista_estantes.selection()
        if not sel:
            return
        nome = self.lista_estantes.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f'Excluir estante "{nome}"?'):
            self.controller.excluir_estante(int(sel[0]))
            self._carregar()

    def _nova_prateleira(self):
        estantes = self.controller.listar_estantes()
        if not estantes:
            messagebox.showwarning("Atenção", "Cadastre uma estante primeiro.")
            return
        nomes = [e["nome_estante"] for e in estantes]
        nome_estante = simpledialog.askstring(
            "Nova Prateleira", f"Escolha a estante ({', '.join(nomes)}):")
        estante_obj = next((e for e in estantes if e["nome_estante"] == nome_estante), None)
        if not estante_obj:
            messagebox.showerror("Erro", "Estante não encontrada.")
            return
        nome_prat = simpledialog.askstring("Nova Prateleira", "Nome da prateleira:")
        if nome_prat:
            sucesso, erro = self.controller.salvar_prateleira(estante_obj["id_estante"], nome_prat)
            if not sucesso:
                messagebox.showerror("Erro", erro)
            self._carregar()

    def _editar_prateleira(self):
        sel = self.lista_prateleiras.selection()
        if not sel:
            return
        id_prat = int(sel[0])
        atual = self.lista_prateleiras.item(sel[0])["values"][0]
        nome = simpledialog.askstring("Editar Prateleira", "Novo nome:", initialvalue=atual)
        if nome:
            estante_nome = self.lista_prateleiras.item(sel[0])["values"][1]
            estante_obj = next((e for e in self.controller.listar_estantes()
                                  if e["nome_estante"] == estante_nome), None)
            sucesso, erro = self.controller.salvar_prateleira(
                estante_obj["id_estante"], nome, id_prateleira=id_prat)
            if not sucesso:
                messagebox.showerror("Erro", erro)
            self._carregar()

    def _excluir_prateleira(self):
        sel = self.lista_prateleiras.selection()
        if not sel:
            return
        nome = self.lista_prateleiras.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f'Excluir prateleira "{nome}"?'):
            self.controller.excluir_prateleira(int(sel[0]))
            self._carregar()