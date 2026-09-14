# views/emprestimos_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.livro_controller import LivroController
from controllers.emprestimo_controller import EmprestimoController
from config import COLORS

STATUS_LABELS = {"disponivel": "Disponível", "em_uso": "Em uso", "emprestado": "Emprestado"}


class EmprestimosView(tk.Frame):
    """UC-012/013: Alterar status do livro e registrar empréstimos."""

    def __init__(self, master):
        super().__init__(master, bg=COLORS["background"])
        self.livro_controller = LivroController()
        self.emprestimo_controller = EmprestimoController()
        self._montar_interface()
        self._carregar()

    def _montar_interface(self):
        tk.Label(self, text="Empréstimos", font=("Segoe UI", 14, "bold"),
                  bg=COLORS["background"]).pack(anchor="w", padx=20, pady=15)

        busca = tk.Frame(self, bg=COLORS["background"])
        busca.pack(fill="x", padx=20)
        self.entry_busca = tk.Entry(busca, font=("Segoe UI", 10))
        self.entry_busca.pack(fill="x", ipady=4)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar())

        container = tk.Frame(self, bg=COLORS["background"])
        container.pack(fill="both", expand=True, padx=20, pady=10)

        colunas = ("titulo", "autor", "isbn", "local", "status")
        self.tree = ttk.Treeview(container, columns=colunas, show="headings", height=15)
        for col, texto, largura in [
            ("titulo", "Título", 200), ("autor", "Autor", 150),
            ("isbn", "ISBN", 130), ("local", "Localização", 150),
            ("status", "Status", 100),
        ]:
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=largura)
        self.tree.pack(fill="both", expand=True)

        tk.Button(self, text="Alterar status do livro selecionado",
                   command=self._alterar_status, bg=COLORS["primary"], fg="white",
                   relief="flat", padx=15, pady=8, cursor="hand2"
                   ).pack(padx=20, pady=(0, 15), anchor="w")

    def _carregar(self):
        filtro = self.entry_busca.get()
        livros = self.livro_controller.listar_livros(filtro)
        self.tree.delete(*self.tree.get_children())
        for l in livros:
            local = f"{l.get('nome_prateleira') or '-'} / {l.get('nome_estante') or '-'}"
            self.tree.insert("", "end", iid=l["id_livro"], values=(
                l["titulo"], l["autor"], l["isbn"] or "-", local,
                STATUS_LABELS.get(l["status"], l["status"])
            ))

    def _alterar_status(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um livro.")
            return
        id_livro = int(sel[0])
        JanelaAlterarStatus(self, id_livro, self.emprestimo_controller, self._carregar)


class JanelaAlterarStatus(tk.Toplevel):
    """UC-012: Modal 'Alterar Status do Livro' (réplica do Figma)."""

    def __init__(self, master, id_livro, controller, on_salvar):
        super().__init__(master)
        self.title("Alterar Status do Livro")
        self.geometry("380x340")
        self.id_livro = id_livro
        self.controller = controller
        self.on_salvar = on_salvar
        self.status_selecionado = tk.StringVar(value="disponivel")

        tk.Label(self, text="Status *", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(15, 5))

        frame_status = tk.Frame(self)
        frame_status.pack(fill="x", padx=15)
        for valor, label in STATUS_LABELS.items():
            tk.Radiobutton(frame_status, text=label, variable=self.status_selecionado,
                            value=valor, command=self._atualizar_obs_estado
                            ).pack(side="left", padx=5)

        tk.Label(self, text="Observações", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.text_obs = tk.Text(self, height=5, font=("Segoe UI", 9))
        self.text_obs.pack(fill="x", padx=15)

        botoes = tk.Frame(self)
        botoes.pack(fill="x", padx=15, pady=20)
        tk.Button(botoes, text="Cancelar", command=self.destroy,
                   bg="#f1f5f9", relief="flat", padx=15, pady=6).pack(side="left")
        tk.Button(botoes, text="Confirmar", command=self._confirmar,
                   bg=COLORS["primary"], fg="white", relief="flat", padx=15, pady=6,
                   cursor="hand2").pack(side="right")

        self._atualizar_obs_estado()

    def _atualizar_obs_estado(self):
        if self.status_selecionado.get() == "disponivel":
            self.text_obs.delete("1.0", "end")
            self.text_obs.config(state="disabled")
        else:
            self.text_obs.config(state="normal")

    def _confirmar(self):
        status = self.status_selecionado.get()
        observacao = self.text_obs.get("1.0", "end").strip()

        sucesso, erro = self.controller.alterar_status(self.id_livro, status, observacao)
        if not sucesso:
            messagebox.showerror("Erro de validação", erro)
            return

        messagebox.showinfo("Sucesso", "Status atualizado com sucesso!")
        self.on_salvar()
        self.destroy()