from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.utils import secure_filename
import random
import os

from livros import catalogo, Livro

app = Flask(__name__)
app.secret_key = "inkanddreams"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "inkdreams61@gmail.com"
app.config["MAIL_PASSWORD"] = "bajedtwwtsvrifmh"

mail = Mail(app)

def enviar_ebook(email, titulo, arquivo_pdf):

    msg = Message(
        subject=f"Seu ebook: {titulo}",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.body = f"""
Olá!

Obrigado pela compra 😊

Segue seu ebook: {titulo}

Boa leitura!
"""

    with app.open_resource(arquivo_pdf) as pdf:
        msg.attach(
            f"{titulo}.pdf",
            "application/pdf",
            pdf.read()
        )

    mail.send(msg)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    senha = db.Column(db.String(200))

    profile_pic = db.Column(db.String(200), default="default.png")

    favoritos_json = db.Column(db.PickleType, default=list)
    carrinho_json = db.Column(db.PickleType, default=list)

    is_admin = db.Column(db.Boolean, default=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.context_processor
def inject_user():
    usuario = None

    if "email" in session:
        usuario = Usuario.query.filter_by(email=session["email"]).first()

    return dict(usuario=usuario)

@app.context_processor
def inject_user():
    usuario = None

    if "email" in session:
        usuario = Usuario.query.filter_by(email=session["email"]).first()

    return dict(usuario=usuario)

@app.route("/admin")
def admin():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario.is_admin:
        return redirect("/catalogo")

    return render_template("admin.html")

@app.route("/adicionar_livro", methods=["POST"])
def adicionar_livro():

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario.is_admin:
        return redirect("/catalogo")

    titulo = request.form["titulo"]
    autor = request.form["autor"]
    genero = request.form["genero"]
    preco = float(request.form["preco"])

    file = request.files["imagem"]

    if file:
        filename = secure_filename(file.filename)

        path = os.path.join(
            "static",
            "livros",
            filename
        )

        file.save(path)
    else:
        filename = "sem-capa.png"

    livro = Livro(
        titulo,
        autor,
        genero,
        preco,
        filename 
    )

    catalogo.append(livro)

    return redirect("/catalogo")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        codigo = random.randint(100000,999999)

        session["codigo"] = str(codigo)
        session["nome"] = nome
        session["email_temp"] = email
        session["senha_temp"] = senha

        msg = Message(
            "Código de verificação - Ink & Dreams",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )

        msg.body = f"""
Olá {nome}!

Seu código de verificação é:

{codigo}

Digite esse código para finalizar o cadastro.
"""

        mail.send(msg)
        return redirect("/verificar")
    return render_template("cadastro.html")

@app.route("/verificar", methods=["GET", "POST"])
def verificar():

    if request.method == "POST":
        codigo_digitado = request.form["codigo"]

        if codigo_digitado == session["codigo"]:

            usuario = Usuario(
                nome=session["nome"],
                email=session["email_temp"],
                senha=session["senha_temp"]
            )

            existe = Usuario.query.filter_by(email=usuario.email).first()

            if existe:
                return "Esse email já está cadastrado"

            if usuario.email == "inkdreams61@gmail.com":
                usuario.is_admin = True

            db.session.add(usuario)
            db.session.commit()

            session["email"] = usuario.email
            return redirect("/catalogo")

        return "Código inválido"

    return render_template("verificar.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.senha == senha:
            session["email"] = usuario.email
            return redirect("/catalogo")

        return "Login inválido"

    return render_template("login.html")

@app.route("/catalogo")
def catalogo_livros():

    if "email" not in session:
        return redirect("/cadastro")

    return render_template(
        "catalogo.html",
        livros=catalogo
    )

@app.route("/favoritar/<titulo>")
def favoritar(titulo):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    for livro in catalogo:
        if livro.titulo == titulo:

            if livro.titulo not in usuario.favoritos_json:
                favoritos = usuario.favoritos_json.copy()
                favoritos.append(livro.titulo)
                usuario.favoritos_json = favoritos
                db.session.commit()

            break

    return redirect("/favoritos")

@app.route("/remover_favorito/<titulo>")
def remover_favorito(titulo):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    usuario.favoritos_json = [
        f for f in usuario.favoritos_json
        if f != titulo
    ]

    db.session.commit()

    return redirect("/favoritos")

@app.route("/pesquisa")
def pesquisa():
    termo = request.args.get("livro", "").strip()
    resultados = []
    if termo:
        termo = termo.lower()
        for livro in catalogo:
            if termo in livro.titulo.lower():
                resultados.append(livro)

    else:
        resultados = catalogo

    return render_template(
        "catalogo.html",
        livros=resultados
    )

@app.route("/genero/<genero>")
def genero(genero):

    resultados = []

    for livro in catalogo:
        if livro.genero.lower() == genero.lower():
            resultados.append(livro)

    return render_template(
        "catalogo.html",
        livros=resultados
    )

@app.route("/recomendacao")
def recomendacao():

    livro = random.choice(catalogo)

    return render_template(
        "recomendacao.html",
        livro=livro
    )

@app.route("/quantidade")
def quantidade():

    total = len(catalogo)

    return f"Temos {total} livros cadastrados."

@app.route("/favoritos")
def favoritos():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    print("Favoritos:", usuario.favoritos_json)

    livros_favoritos = [
        livro for livro in catalogo
        if livro.titulo in usuario.favoritos_json
    ]

    print("Encontrados:", [livro.titulo for livro in livros_favoritos])

    return render_template(
        "favoritos.html",
        favoritos=livros_favoritos
    )

@app.route("/carrinho")
def carrinho():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    itens = usuario.carrinho_json

    total = sum(
        item["preco"]
        for item in itens
    )

    return render_template(
        "carrinho.html",
        carrinho=itens,
        total=total
    )

@app.route("/adicionar_carrinho/<titulo>")
def adicionar_carrinho(titulo):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/cadastro")

    formato = request.args.get(
        "formato",
        "capa_comum"
    )

    for livro in catalogo:

        if livro.titulo == titulo:

            carrinho = usuario.carrinho_json.copy()

            carrinho.append({
                "titulo": livro.titulo,
                "autor": livro.autor,
                "preco": livro.preco,
                "imagem": livro.imagem,
                "formato": formato
            })

            usuario.carrinho_json = carrinho

            db.session.commit()

            break

    return redirect("/catalogo")

@app.route("/remover_carrinho/<titulo>")
def remover_carrinho(titulo):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    usuario.carrinho_json = [
        item for item in usuario.carrinho_json
        if item["titulo"] != titulo
    ]

    db.session.commit()

    return redirect("/carrinho")

@app.route("/finalizar")
def finalizar():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    usuario.carrinho_json = []
    db.session.commit()

    return redirect("/catalogo")

@app.route("/checkout")
def checkout():

    if "email" not in session:
        return redirect("/cadastro")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if usuario is None:
        return redirect("/cadastro")

    total = sum(
        item["preco"]
        for item in usuario.carrinho_json
    )

    return render_template(
        "checkout.html",
        carrinho=usuario.carrinho_json,
        total=total
    )

@app.route("/confirmar_compra")
def confirmar_compra():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    itens_comprados = usuario.carrinho_json.copy()

    for item in itens_comprados:

        if item["formato"] == "ebook":

            titulo = item["titulo"]
            pdf_path = f"static/ebooks/{titulo}.pdf"

            try:
                enviar_ebook(usuario.email, titulo, pdf_path)
            except:
                print("Erro ao enviar ebook:", titulo)

    usuario.carrinho_json = []
    db.session.commit()

    return render_template(
        "sucesso.html",
        usuario=usuario,
        itens=itens_comprados
    )

@app.route("/pagar")
def pagar():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/cadastro")

    total = sum(
        item["preco"]
        for item in usuario.carrinho_json
    )

    return render_template(
        "pagamento.html",
        total=total
    )
    
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/conta")
def conta():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    return render_template("conta.html", usuario=usuario)

@app.route("/editar_nome", methods=["POST"])
def editar_nome():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    novo_nome = request.form["nome"]

    usuario.nome = novo_nome
    db.session.commit()

    return redirect("/conta")

@app.route("/alterar_senha", methods=["POST"])
def alterar_senha():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    senha_atual = request.form["senha_atual"]
    nova_senha = request.form["nova_senha"]

    if usuario.senha != senha_atual:
        return "Senha atual incorreta"

    usuario.senha = nova_senha
    db.session.commit()

    return redirect("/conta")

@app.route("/upload_foto", methods=["POST"])
def upload_foto():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario:
        return redirect("/cadastro")

    file = request.files["foto"]

    if file:
        filename = secure_filename(file.filename)

        path = os.path.join(
            "static",
            "profiles",
            filename
        )

        file.save(path)

        usuario.profile_pic = filename
        db.session.commit()

    return redirect("/conta")

with app.app_context():
    db.create_all()

    admin = Usuario.query.filter_by(email="inkdreams61@gmail.com").first()

    if not admin:
        admin = Usuario(
            nome="Admin",
            email="inkdreams61@gmail.com",
            senha="123",
            is_admin=True
        )
        db.session.add(admin)

    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)