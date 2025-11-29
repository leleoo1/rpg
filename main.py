import tkinter as tk
from tkinter import messagebox
import sqlite3
import random

# --------------------------------------------
# BANCO DE DADOS
# --------------------------------------------

def criar_bd():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        tipo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        mensagem TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    # cria um admin padrão caso não exista
    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
                       ("admin", "admin", "adm"))
    conn.commit()
    conn.close()

criar_bd()

# --------------------------------------------
# FUNÇÕES GERAIS
# --------------------------------------------

def cadastrar_usuario(usuario, senha, tipo):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
                       (usuario, senha, tipo))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def validar_login(usuario, senha):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    dados = cursor.fetchone()
    conn.close()
    return dados  # retorna (id, tipo)

# --------------------------------------------
# JANELAS DO SISTEMA
# --------------------------------------------

# ------------------------- CADASTRO -------------------------
def janela_cadastro():
    cad = tk.Toplevel()
    cad.title("Cadastro")
    cad.geometry("330x300")

    tk.Label(cad, text="Cadastrar novo usuário", font=("Arial", 16)).pack(pady=10)

    tk.Label(cad, text="Usuário:").pack()
    e_user = tk.Entry(cad)
    e_user.pack()

    tk.Label(cad, text="Senha:").pack()
    e_pass = tk.Entry(cad, show="*")
    e_pass.pack()

    tk.Label(cad, text="Tipo de conta:").pack()
    var_tipo = tk.StringVar(value="normal")
    tk.Radiobutton(cad, text="Usuário normal", variable=var_tipo, value="normal").pack()
    tk.Radiobutton(cad, text="Administrador", variable=var_tipo, value="adm").pack()

    def cadastrar():
        if cadastrar_usuario(e_user.get(), e_pass.get(), var_tipo.get()):
            messagebox.showinfo("OK", "Usuário cadastrado!")
            cad.destroy()
        else:
            messagebox.showerror("Erro", "Usuário já existe!")

    tk.Button(cad, text="Cadastrar", command=cadastrar).pack(pady=10)

# ------------------------- ROLO DE DADOS -------------------------
def janela_dados():
    win = tk.Toplevel()
    win.title("Rolar Dados")
    win.geometry("300x250")

    resultado = tk.Label(win, text="Resultado:", font=("Arial", 16))
    resultado.pack(pady=20)

    def rolar_d20():
        resultado.config(text=f"D20 → {random.randint(1,20)}")

    def rolar_d6():
        resultado.config(text=f"D6 → {random.randint(1,6)}")

    tk.Button(win, text="Rolar D20", width=15, command=rolar_d20).pack(pady=5)
    tk.Button(win, text="Rolar D6", width=15, command=rolar_d6).pack(pady=5)

# ------------------------- SALVAR MENSAGENS -------------------------
def janela_mensagens(usuario_id):
    win = tk.Toplevel()
    win.title("Salvar Mensagem")
    win.geometry("400x350")

    tk.Label(win, text="Escreva sua mensagem (máx 400 palavras):", font=("Arial", 12)).pack()

    texto = tk.Text(win, height=10, width=40)
    texto.pack(pady=10)

    def salvar():
        conteudo = texto.get("1.0", tk.END).strip()
        palavras = len(conteudo.split())

        if palavras > 400:
            messagebox.showerror("Erro", f"Você escreveu {palavras} palavras. Limite: 400.")
            return

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mensagens (usuario_id, mensagem) VALUES (?, ?)", (usuario_id, conteudo))
        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Mensagem salva!")
        texto.delete("1.0", tk.END)

    tk.Button(win, text="Salvar", width=15, command=salvar).pack()

# ------------------------- PERFIL -------------------------
def janela_perfil(usuario_id):
    win = tk.Toplevel()
    win.title("Seu Perfil")
    win.geometry("350x250")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, tipo FROM usuarios WHERE id=?", (usuario_id,))
    nome, tipo = cursor.fetchone()
    conn.close()

    tk.Label(win, text="Perfil do Usuário", font=("Arial", 18)).pack(pady=10)
    tk.Label(win, text=f"Usuário: {nome}", font=("Arial", 14)).pack(pady=5)
    tk.Label(win, text=f"Tipo: {tipo}", font=("Arial", 14)).pack(pady=5)

# ------------------------- TELA PRINCIPAL -------------------------
def janela_principal(usuario_id, tipo):
    win = tk.Toplevel()
    win.title("Menu Principal")
    win.geometry("400x350")

    tk.Label(win, text="Menu Principal", font=("Arial", 22)).pack(pady=20)

    tk.Button(win, text="Rolar Dados", width=20, command=janela_dados).pack(pady=10)
    tk.Button(win, text="Salvar Mensagens", width=20, command=lambda: janela_mensagens(usuario_id)).pack(pady=10)
    tk.Button(win, text="Meu Perfil", width=20, command=lambda: janela_perfil(usuario_id)).pack(pady=10)

    # admin pode cadastrar usuários
    if tipo == "adm":
        tk.Button(win, text="Cadastrar Usuário (ADM)", width=20, command=janela_cadastro).pack(pady=10)

# ------------------------- LOGIN -------------------------
def tela_login():
    root = tk.Tk()
    root.title("Login")
    root.geometry("330x250")

    tk.Label(root, text="Login do Sistema", font=("Arial", 18)).pack(pady=15)

    tk.Label(root, text="Usuário:").pack()
    e_user = tk.Entry(root)
    e_user.pack()

    tk.Label(root, text="Senha:").pack()
    e_pass = tk.Entry(root, show="*")
    e_pass.pack()

    def entrar():
        dados = validar_login(e_user.get(), e_pass.get())
        if dados:
            usuario_id, tipo = dados
            root.destroy()
            janela_principal(usuario_id, tipo)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    tk.Button(root, text="Entrar", width=12, command=entrar).pack(pady=10)

    root.mainloop()

tela_login()
