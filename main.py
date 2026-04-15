from flask import Flask, request, redirect, session, render_template_string
import sqlite3
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "segredo_super_forte"

def get_db():
    return sqlite3.connect("equipe.db")

def criar_tabela():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id TEXT PRIMARY KEY,
        senha TEXT,
        cargo TEXT,
        primeiro_login INTEGER
    )
    """)
    db.commit()

criar_tabela()

def criar_admin():
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id='admin'").fetchone()
    if not user:
        senha = bcrypt.hashpw("admin".encode(), bcrypt.gensalt())
        db.execute("INSERT INTO usuarios VALUES (?,?,?,?)",
                   ("admin", senha, "ADM", 1))
        db.commit()

criar_admin()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        id = request.form["id"]
        senha = request.form["senha"].encode()

        db = get_db()
        user = db.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()

        if user and bcrypt.checkpw(senha, user[1]):
            session["user"] = id
            if user[3] == 1:
                return redirect("/trocar-senha")
            return redirect("/dashboard")

    return render_template_string("""
    <body style="background:black;color:white;text-align:center">
    <h1 style="color:gold">Equipe Cane</h1>
    <form method="post">
    <input name="id" placeholder="ID"><br><br>
    <input name="senha" type="password" placeholder="Senha"><br><br>
    <button style="background:gold">Entrar</button>
    </form>
    </body>
    """)

@app.route("/trocar-senha", methods=["GET","POST"])
def trocar():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        nova = request.form["senha"].encode()
        senha_hash = bcrypt.hashpw(nova, bcrypt.gensalt())

        db = get_db()
        db.execute("UPDATE usuarios SET senha=?, primeiro_login=0 WHERE id=?",
                   (senha_hash, session["user"]))
        db.commit()

        return redirect("/dashboard")

    return render_template_string("""
    <body style="background:black;color:white;text-align:center">
    <h2>Troque sua senha</h2>
    <form method="post">
    <input name="senha" type="password"><br><br>
    <button style="background:gold">Salvar</button>
    </form>
    </body>
    """)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template_string("""
    <body style="background:black;color:white;text-align:center">
    <h1 style="color:gold">Dashboard</h1>
    <p>Bem-vindo {{user}}</p>
    <a href="/logout">Sair</a>
    </body>
    """, user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
