# views/emprestimos_view.py — atualizado com colunas de rastreabilidade

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.exemplar_controller import ExemplarController
from controllers.emprestimo_controller import EmprestimoController
from config import COLORS

STATUS_LABELS = {"disponivel": "Disponível", "em_uso": "Em uso", "emprestado": "Emprestado"}


class EmprestimosView(tk.Frame):
    """
    UC-012/013: Alterar status de um EXEMPLAR e registrar empréstimos,
    exibindo quem alterou, quando e a observação da alteração.
    """

    def __init__(self, master, usuario):
        super().__init__(master, bg=COLORS["background"])
        self.usuario = usuario
        self.exemplar_controller = ExemplarController()
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

        # Colunas solicitadas: Código, Título, Localização, Status,
        # Alterado por, Data da alteração e Observações
        colunas = ("codigo", "titulo", "local", "status", "usuario", "data", "observacoes")
        self.tree = ttk.Treeview(container, columns=colunas, show="headings", height=15)

        configuracao_colunas = [
            ("codigo", "Código", 80),
            ("titulo", "Título", 160),
            ("local", "Localização", 130),
            ("status", "Status", 90),
            ("usuario", "Alterado por", 120),
            ("data", "Data da Alteração", 130),
            ("observacoes", "Observações", 200),
        ]
        for col, texto, largura in configuracao_colunas:
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=largura)

        scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        tk.Button(self, text="Alterar status do exemplar selecionado",
                   command=self._alterar_status, bg=COLORS["primary"], fg="white",
                   relief="flat", padx=15, pady=8, cursor="hand2"
                   ).pack(padx=20, pady=(0, 15), anchor="w")

    def _carregar(self):
        filtro = self.entry_busca.get()
        exemplares = self.exemplar_controller.listar_todos(filtro)
        self.tree.delete(*self.tree.get_children())

        for ex in exemplares:
            local = f"{ex.get('nome_prateleira') or '-'} / {ex.get('nome_estante') or '-'}"

            data_alteracao = ex.get("data_ultima_alteracao")
            data_formatada = data_alteracao.strftime("%d/%m/%Y %H:%M") if data_alteracao else "-"

            usuario_alteracao = ex.get("usuario_ultima_alteracao") or "-"
            observacao_alteracao = ex.get("ultima_observacao") or "-"

            self.tree.insert("", "end", iid=ex["id_exemplar"], values=(
                ex["codigo_tombo"] or "-",
                ex["titulo"],
                local,
                STATUS_LABELS.get(ex["status"], ex["status"]),
                usuario_alteracao,
                data_formatada,
                observacao_alteracao,
            ))

    def _alterar_status(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um exemplar.")
            return
        id_exemplar = int(sel[0])
        JanelaAlterarStatus(self, id_exemplar, self.emprestimo_controller,
                              self.usuario.id_usuario, self._carregar)


class JanelaAlterarStatus(tk.Toplevel):
    """UC-012: Modal 'Alterar Status do Exemplar', com registro de usuário responsável."""

    def __init__(self, master, id_exemplar, controller, id_usuario_logado, on_salvar):
        super().__init__(master)
        self.title("Alterar Status do Exemplar")
        self.geometry("380x340")
        self.id_exemplar = id_exemplar
        self.controller = controller
        self.id_usuario_logado = id_usuario_logado
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
            self.text_obs.config(state="normal")
        else:
            self.text_obs.config(state="normal")

    def _confirmar(self):
        status = self.status_selecionado.get()
        observacao = self.text_obs.get("1.0", "end").strip()

        sucesso, erro = self.controller.alterar_status(
            self.id_exemplar, status, observacao, self.id_usuario_logado)

        if not sucesso:
            messagebox.showerror("Erro de validação", erro)
            return

        messagebox.showinfo("Sucesso", "Status atualizado com sucesso!")
        self.on_salvar()
        self.destroy()