# views/usuarios_view.py — arquivo completo corrigido

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.usuario_controller import UsuarioController
from config import COLORS

PERMISSOES_LABELS = {
    "cadastrar": "Cadastrar livros",
    "alterar": "Alterar livros",
    "excluir": "Excluir livros",
    "emprestimo": "Empréstimos",
    "gerenciar_localizacao": "Gerenciar localizações",
    "gerenciar_usuarios": "Gerenciar usuários",
}


class UsuariosView(tk.Frame):
    """
    UC-006/007/008: Gerenciar usuários do sistema (apenas administradores).
    Esta é a tela de LISTAGEM exibida ao clicar em "Usuários" no menu lateral.
    """

    def __init__(self, master, usuario_logado):
        super().__init__(master, bg=COLORS["background"])
        self.usuario_logado = usuario_logado
        self.controller = UsuarioController()
        self.controller.usuario_logado = usuario_logado
        self._montar_interface()
        self._carregar()

    def _montar_interface(self):
        header = tk.Frame(self, bg=COLORS["background"])
        header.pack(fill="x", padx=20, pady=15)
        tk.Label(header, text="Usuários do Sistema", font=("Segoe UI", 14, "bold"),
                  bg=COLORS["background"]).pack(side="left")
        tk.Button(header, text="+ Novo Usuário", command=self._novo_usuario,
                   bg=COLORS["primary"], fg="white", relief="flat", padx=15, pady=6,
                   cursor="hand2").pack(side="right")

        container = tk.Frame(self, bg=COLORS["background"])
        container.pack(fill="both", expand=True, padx=20)

        colunas = ("nome", "login", "perfil", "status")
        self.tree = ttk.Treeview(container, columns=colunas, show="headings", height=15)
        for c, t in [("nome", "Usuário"), ("login", "Login"),
                     ("perfil", "Perfil"), ("status", "Status")]:
            self.tree.heading(c, text=t)
        self.tree.pack(fill="both", expand=True)

        acoes = tk.Frame(self, bg=COLORS["background"])
        acoes.pack(fill="x", padx=20, pady=15)
        tk.Button(acoes, text="Editar", command=self._editar_usuario).pack(side="left", padx=(0, 5))
        tk.Button(acoes, text="Excluir", command=self._excluir_usuario).pack(side="left")

    def _carregar(self):
        self.tree.delete(*self.tree.get_children())
        for u in self.controller.listar_usuarios():
            self.tree.insert("", "end", iid=u["id_usuario"], values=(
                u["nome_completo"], u["login"],
                "Administrador" if u["perfil"] == "admin" else "Operador",
                "Ativo" if u["ativo"] else "Inativo",
            ))

    def _novo_usuario(self):
        FormUsuario(self, self.controller, on_salvar=self._carregar)

    def _editar_usuario(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um usuário.")
            return
        FormUsuario(self, self.controller, id_usuario=int(sel[0]), on_salvar=self._carregar)

    def _excluir_usuario(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um usuário.")
            return
        id_usuario = int(sel[0])
        nome = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f'Excluir usuário "{nome}"?'):
            sucesso, erro = self.controller.excluir_usuario(id_usuario, self.usuario_logado.id_usuario)
            if not sucesso:
                messagebox.showerror("Erro", erro)
            self._carregar()


class FormUsuario(tk.Toplevel):
    """UC-006/UC-007: Formulário de Criar/Alterar Usuário (janela separada, modal)."""

    def __init__(self, master, controller, id_usuario=None, on_salvar=None):
        super().__init__(master)
        self.title("Editar Usuário" if id_usuario else "Novo Usuário")
        self.geometry("420x560")
        self.resizable(False, False)
        self.transient(master)   # mantém o formulário sempre à frente da tela principal
        self.grab_set()          # bloqueia interação com a tela principal até fechar o formulário
        self.controller = controller
        self.id_usuario = id_usuario
        self.on_salvar = on_salvar
        self.checks_permissoes = {}

        # Container principal dividido em: corpo com campos + rodapé fixo com botões
        self.frame_corpo = tk.Frame(self)
        self.frame_corpo.pack(fill="both", expand=True, padx=15, pady=(15, 0))

        self.frame_rodape = tk.Frame(self)
        self.frame_rodape.pack(fill="x", side="bottom", padx=15, pady=15)

        self._montar_form()
        if id_usuario:
            self._carregar_dados(id_usuario)

    def _montar_form(self):
        self.entry_nome = self._campo(self.frame_corpo, "Nome Completo *")
        self.entry_login = self._campo(self.frame_corpo, "Login *")
        self.entry_senha = self._campo(self.frame_corpo, "Senha *", show="•")

        tk.Label(self.frame_corpo, text="Perfil", font=("Segoe UI", 8)).pack(anchor="w")
        self.combo_perfil = ttk.Combobox(self.frame_corpo, values=["Administrador", "Operador"], state="readonly")
        self.combo_perfil.set("Operador")
        self.combo_perfil.pack(fill="x", pady=(0, 10))
        self.combo_perfil.bind("<<ComboboxSelected>>", lambda e: self._atualizar_visibilidade_permissoes())

        tk.Label(self.frame_corpo, text="Permissões", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.frame_perm = tk.Frame(self.frame_corpo)
        self.frame_perm.pack(fill="x", pady=5)
        for chave, label in PERMISSOES_LABELS.items():
            var = tk.BooleanVar()
            tk.Checkbutton(self.frame_perm, text=label, variable=var).pack(anchor="w")
            self.checks_permissoes[chave] = var

        self.label_admin_info = tk.Label(
            self.frame_corpo, text="Administradores têm acesso total ao sistema.",
            font=("Segoe UI", 8), fg=COLORS["text_gray"]
        )

        self.var_ativo = tk.BooleanVar(value=True)
        tk.Checkbutton(self.frame_corpo, text="Usuário ativo", variable=self.var_ativo).pack(anchor="w", pady=10)

        # Botões fixos no rodapé — sempre visíveis, independente do tamanho do formulário
        tk.Button(self.frame_rodape, text="Cancelar", command=self.destroy,
                   bg="#f1f5f9", relief="flat", padx=15, pady=6).pack(side="left")
        tk.Button(self.frame_rodape, text="Salvar", command=self._salvar,
                   bg=COLORS["primary"], fg="white", relief="flat", padx=15, pady=6,
                   cursor="hand2").pack(side="right")

        self._atualizar_visibilidade_permissoes()

    def _atualizar_visibilidade_permissoes(self):
        """Esconde os checkboxes de permissão quando o perfil é Administrador."""
        if self.combo_perfil.get() == "Administrador":
            self.frame_perm.pack_forget()
            self.label_admin_info.pack(anchor="w", pady=5)
        else:
            self.label_admin_info.pack_forget()
            self.frame_perm.pack(fill="x", pady=5)

    def _campo(self, parent, label, show=None):
        tk.Label(parent, text=label, font=("Segoe UI", 8)).pack(anchor="w")
        entry = tk.Entry(parent, font=("Segoe UI", 10), show=show)
        entry.pack(fill="x", pady=(0, 8), ipady=3)
        return entry

    def _carregar_dados(self, id_usuario):
        usuarios = self.controller.listar_usuarios()
        usuario = next((u for u in usuarios if u["id_usuario"] == id_usuario), None)
        if not usuario:
            return
        self.entry_nome.insert(0, usuario["nome_completo"])
        self.entry_login.insert(0, usuario["login"])
        self.entry_senha.insert(0, usuario["senha"])
        self.combo_perfil.set("Administrador" if usuario["perfil"] == "admin" else "Operador")
        self.var_ativo.set(bool(usuario["ativo"]))
        for chave, var in self.checks_permissoes.items():
            var.set(usuario["permissoes"].get(chave, False))
        self._atualizar_visibilidade_permissoes()

    def _salvar(self):
        dados = {
            "nome_completo": self.entry_nome.get().strip(),
            "login": self.entry_login.get().strip(),
            "senha": self.entry_senha.get().strip(),
            "perfil": "admin" if self.combo_perfil.get() == "Administrador" else "operador",
            "ativo": self.var_ativo.get(),
            "permissoes": {chave: var.get() for chave, var in self.checks_permissoes.items()},
        }

        sucesso, erro = self.controller.salvar_usuario(dados, id_usuario=self.id_usuario)
        if not sucesso:
            messagebox.showerror("Erro de validação", erro)
            return

        messagebox.showinfo("Sucesso", "Usuário salvo com sucesso!")
        if self.on_salvar:
            self.on_salvar()
        self.destroy()