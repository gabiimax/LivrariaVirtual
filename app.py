from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import random
import os
print(os.path.abspath("site.db"))

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

Obrigado pela compra, espero que goste.😊

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

class LivroDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False, unique=True)
    autor = db.Column(db.String(150), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200), nullable=False)
    capa_comum = db.Column(db.Boolean, default=True)
    capa_dura = db.Column(db.Boolean, default=False)
    ebook = db.Column(db.Boolean, default=True)

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    livro_titulo = db.Column(db.String(200), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=False)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    livro_titulo = db.Column(db.String(200), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

class RespostaQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    genero = db.Column(db.String(100), nullable=False)
    romance = db.Column(db.String(100), nullable=False)
    clima = db.Column(db.String(100), nullable=False)
    ritmo = db.Column(db.String(100), nullable=False)
    foco = db.Column(db.String(100), nullable=False)
    tipo_historia = db.Column(db.String(100), nullable=False)
    final_leitura = db.Column(db.String(100), nullable=False)
    livro_favorito = db.Column(db.String(200), nullable=False)

class Conquista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    recompensa = db.Column(db.String(200), nullable=False)
    desbloqueada = db.Column(db.Boolean, default=False)

class Cupom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    desconto = db.Column(db.Float, nullable=False)
    usado = db.Column(db.Boolean, default=False)

def carregar_livros_no_banco():

    for livro in catalogo:

        livro_existente = LivroDB.query.filter_by(
            titulo=livro.titulo
        ).first()

        if not livro_existente:

            novo_livro = LivroDB(
                titulo=livro.titulo,
                autor=livro.autor,
                genero=livro.genero,
                preco=livro.preco,
                imagem=livro.imagem,
                capa_comum=livro.capa_comum,
                capa_dura=livro.capa_dura,
                ebook=livro.ebook
            )

            db.session.add(novo_livro)

    db.session.commit()

def atualizar_conquistas(usuario):

    quantidade_favoritos = len(usuario.favoritos_json or [])

    quantidade_compras = Venda.query.filter_by(
        usuario_id=usuario.id
    ).count()

    quantidade_avaliacoes = Avaliacao.query.filter_by(
        usuario_id=usuario.id
    ).count()

    conquistas = [
        {
            "nome": "Primeira leitura",
            "descricao": "Adicione seu primeiro livro aos favoritos.",
            "recompensa": "🌱 Leitor iniciante",
            "condicao": quantidade_favoritos >= 1
        },

        {
            "nome": "Colecionador",
            "descricao": "Adicione 5 livros aos favoritos.",
            "recompensa": "❤️ Colecionador de histórias",
            "condicao": quantidade_favoritos >= 5
        },

        {
            "nome": "Primeira compra",
            "descricao": "Realize sua primeira compra.",
            "recompensa": "🛍️ Primeira compra",
            "condicao": quantidade_compras >= 1
        },

        {
            "nome": "Leitor voraz",
            "descricao": "Compre 5 livros.",
            "recompensa": "📚 Leitor voraz",
            "condicao": quantidade_compras >= 5
        },

        {
            "nome": "Crítico literário",
            "descricao": "Faça sua primeira avaliação.",
            "recompensa": "⭐ Crítico literário",
            "condicao": quantidade_avaliacoes >= 1
        },

        {
            "nome": "Leitor curioso",
            "descricao": "Complete o quiz literário.",
            "recompensa": "🧠 Descobridor de histórias",
            "condicao": RespostaQuiz.query.count() >= 1
        }
    ]

    for dados in conquistas:

        conquista = Conquista.query.filter_by(
            usuario_id=usuario.id,
            nome=dados["nome"]
        ).first()

        if not conquista:

            conquista = Conquista(
                usuario_id=usuario.id,
                nome=dados["nome"],
                descricao=dados["descricao"],
                recompensa=dados["recompensa"],
                desbloqueada=False
            )

            db.session.add(conquista)

        conquista.desbloqueada = dados["condicao"]

    db.session.commit()

@app.route("/conquistas")
def conquistas():
    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/login")

    atualizar_conquistas(usuario)

    lista_conquistas = Conquista.query.filter_by(
        usuario_id=usuario.id
    ).all()

    total = len(lista_conquistas)

    desbloqueadas = sum(
        1 for conquista in lista_conquistas
        if conquista.desbloqueada
    )

    return render_template(
        "conquistas.html",
        conquistas=lista_conquistas,
        total=total,
        desbloqueadas=desbloqueadas
    )

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/debug_users")
def debug_users():
    usuarios = Usuario.query.all()
    return "<br>".join([f"{u.email} - {u.senha}" for u in usuarios])

@app.context_processor
def inject_user():
    usuario = None

    if "email" in session:
        usuario = Usuario.query.filter_by(email=session["email"]).first()

    return dict(usuario=usuario)

@app.route("/endereco", methods=["GET", "POST"])
def endereco():
    if request.method == "POST":
        endereco = {
            "nome": request.form["nome"],
            "cep": request.form["cep"],
            "rua": request.form["rua"],
            "numero": request.form["numero"],
            "complemento": request.form["complemento"],
            "bairro": request.form["bairro"],
            "cidade": request.form["cidade"],
            "estado": request.form["estado"]
        }

        session["endereco"] = endereco

        return redirect(url_for("pagamento"))

    return render_template("endereco.html")

@app.route("/admin")
def admin():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario or not usuario.is_admin:
        return redirect("/catalogo")

    # =========================
    # DADOS DAS VENDAS
    # =========================

    vendas = Venda.query.all()

    total_vendas = len(vendas)

    faturamento = sum(
        venda.preco
        for venda in vendas
    )

    # =========================
    # LIVROS MAIS VENDIDOS
    # =========================

    vendas_por_livro = {}

    for venda in vendas:

        titulo = venda.livro_titulo

        if titulo not in vendas_por_livro:
            vendas_por_livro[titulo] = 0

        vendas_por_livro[titulo] += 1

    livros_mais_vendidos = sorted(
        vendas_por_livro.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    vendas_por_genero = {}

    for venda in vendas:

        genero = venda.genero

        if genero not in vendas_por_genero:
            vendas_por_genero[genero] = 0

        vendas_por_genero[genero] += 1

    generos_mais_vendidos = sorted(
        vendas_por_genero.items(),
        key=lambda x: x[1],
        reverse=True
    )


    avaliacoes = Avaliacao.query.all()

    total_avaliacoes = len(avaliacoes)

    if avaliacoes:
        media_geral = sum(
            avaliacao.nota
            for avaliacao in avaliacoes
        ) / len(avaliacoes)
    else:
        media_geral = 0

    notas_por_livro = {}

    for avaliacao in avaliacoes:

        titulo = avaliacao.livro_titulo

        if titulo not in notas_por_livro:
            notas_por_livro[titulo] = []

        notas_por_livro[titulo].append(
            avaliacao.nota
        )

    livros_bem_avaliados = []

    for titulo, notas in notas_por_livro.items():

        media = sum(notas) / len(notas)

        livros_bem_avaliados.append(
            (titulo, round(media, 1))
        )

    livros_bem_avaliados.sort(
        key=lambda x: x[1],
        reverse=True
    )

    livros_bem_avaliados = livros_bem_avaliados[:5]

    return render_template(
        "admin.html",
        catalogo=catalogo,
        total_vendas=total_vendas,
        faturamento=faturamento,
        total_avaliacoes=total_avaliacoes,
        media_geral=round(media_geral, 1),
        livros_mais_vendidos=livros_mais_vendidos,
        generos_mais_vendidos=generos_mais_vendidos,
        livros_bem_avaliados=livros_bem_avaliados
    )

resenhas_livros = {
    "A Hipotese do Amor":
        "Uma comédia romântica divertida sobre dois pesquisadores que acabam envolvidos em um relacionamento de mentira que começa a ficar mais complicado do que esperavam.",

    "Amor, Teoricamente":
        "Uma história de romance e descobertas que acompanha uma protagonista dividida entre diferentes lados da vida acadêmica e um relacionamento que não sai exatamente como planejado.",

    "Assistente do Vilão":
        "Uma fantasia romântica cheia de humor, situações inesperadas e personagens que descobrem que trabalhar para um vilão pode ser muito mais complicado do que parece.",

    "Caraval":
        "Uma fantasia envolvente em que um jogo misterioso transforma a realidade em um grande espetáculo. Entre segredos, ilusões e desafios, nada é exatamente o que parece.",

    "Era Uma Vez um Coração Partido":
        "Uma fantasia romântica repleta de magia, promessas e escolhas difíceis, acompanhando uma jovem que acaba entrando em um acordo perigoso com uma figura misteriosa.",

    "Powerless":
        "Uma fantasia intensa sobre sobrevivência, poder e escolhas. Em um mundo onde possuir habilidades determina o destino das pessoas, uma jovem precisa esconder quem realmente é.",

    "Fearless":
        "Uma continuação marcada por desafios, conflitos e descobertas, levando os personagens ainda mais fundo em um mundo de poder, perigos e sentimentos complicados.",

    "Quarta Asa":
        "Uma fantasia repleta de dragões, treinamento e desafios, acompanhando uma jovem que precisa provar sua força em um ambiente extremamente perigoso.",

    "Estilhaça-me":
        "Uma distopia intensa sobre uma jovem que vive isolada por possuir uma habilidade considerada perigosa. Entre conflitos, descobertas e relações complicadas, sua visão do mundo começa a mudar.",

    "Divinos Rivais":
        "Uma fantasia romântica que mistura cartas, rivalidade e magia. Dois jornalistas começam como concorrentes, mas uma troca inesperada de mensagens muda completamente a relação entre eles.",

    "Melhor do Que Nos Filmes":
        "Um romance divertido que brinca com os clichês das comédias românticas enquanto acompanha personagens tentando transformar suas próprias vidas em uma história digna de filme.",

    "Não é Como Nos Filmes":
        "Uma história sobre reencontros, sentimentos antigos e a diferença entre aquilo que imaginamos que vai acontecer e o que realmente acontece."
}

PERGUNTAS_QUIZ = [

    {
        "categoria": "genero",
        "pergunta": "Qual gênero você mais gosta?",
        "opcoes": [
            {"valor": "Romance", "texto": "Romance"},
            {"valor": "Fantasia", "texto": "Fantasia"},
            {"valor": "Romance e Fantasia", "texto": "Romance e fantasia"},
            {"valor": "Distópia e Romance", "texto": "Distopia e romance"}
        ]
    },

    {
        "categoria": "genero",
        "pergunta": "Se pudesse escolher uma estante agora, qual seria?",
        "opcoes": [
            {"valor": "Romance", "texto": "Romances"},
            {"valor": "Fantasia", "texto": "Fantasia e mundos mágicos"},
            {"valor": "Romance e Fantasia", "texto": "Romance com fantasia"},
            {"valor": "Distópia e Romance", "texto": "Distopias e romances intensos"}
        ]
    },

    {
        "categoria": "genero",
        "pergunta": "Qual dessas histórias mais combina com você?",
        "opcoes": [
            {"valor": "Romance", "texto": "Uma história de amor"},
            {"valor": "Fantasia", "texto": "Uma aventura fantástica"},
            {"valor": "Romance e Fantasia", "texto": "Amor em um mundo mágico"},
            {"valor": "Distópia e Romance", "texto": "Uma história intensa em um mundo diferente"}
        ]
    },


    {
        "categoria": "romance",
        "pergunta": "Qual tipo de romance você prefere?",
        "opcoes": [
            {"valor": "Enemies to lovers", "texto": "Inimigos que acabam se apaixonando"},
            {"valor": "Friends to lovers", "texto": "Amigos que se apaixonam"},
            {"valor": "Slow burn", "texto": "Um romance que acontece aos poucos"},
            {"valor": "Romance proibido", "texto": "Um amor que não deveria acontecer"}
        ]
    },

    {
        "categoria": "romance",
        "pergunta": "Qual dinâmica de casal mais chama sua atenção?",
        "opcoes": [
            {"valor": "Enemies to lovers", "texto": "Duas pessoas que vivem se provocando"},
            {"valor": "Friends to lovers", "texto": "Uma amizade que vira amor"},
            {"valor": "Slow burn", "texto": "Sentimentos que crescem lentamente"},
            {"valor": "Romance proibido", "texto": "Um amor cheio de obstáculos"}
        ]
    },

    {
        "categoria": "romance",
        "pergunta": "Escolha o tipo de romance que você leria primeiro.",
        "opcoes": [
            {"valor": "Enemies to lovers", "texto": "Rivais que não conseguem se ignorar"},
            {"valor": "Friends to lovers", "texto": "Melhores amigos que percebem seus sentimentos"},
            {"valor": "Slow burn", "texto": "Uma paixão construída aos poucos"},
            {"valor": "Romance proibido", "texto": "Um relacionamento impossível"}
        ]
    },


    {
        "categoria": "clima",
        "pergunta": "Que tipo de história chama mais sua atenção?",
        "opcoes": [
            {"valor": "Leve", "texto": "Uma história divertida e leve"},
            {"valor": "Magica", "texto": "Uma aventura cheia de magia"},
            {"valor": "Misteriosa", "texto": "Uma história cheia de mistérios"},
            {"valor": "Emocionante", "texto": "Uma história emocionante"}
        ]
    },

    {
        "categoria": "clima",
        "pergunta": "Qual atmosfera você escolheria para sua próxima leitura?",
        "opcoes": [
            {"valor": "Leve", "texto": "Divertida e descontraída"},
            {"valor": "Magica", "texto": "Mágica e encantadora"},
            {"valor": "Misteriosa", "texto": "Sombria e misteriosa"},
            {"valor": "Emocionante", "texto": "Intensa e emocionante"}
        ]
    },

    {
        "categoria": "clima",
        "pergunta": "Que sensação você quer encontrar nas páginas?",
        "opcoes": [
            {"valor": "Leve", "texto": "Quero me divertir"},
            {"valor": "Magica", "texto": "Quero me perder em outro mundo"},
            {"valor": "Misteriosa", "texto": "Quero tentar descobrir os segredos"},
            {"valor": "Emocionante", "texto": "Quero sentir tudo intensamente"}
        ]
    },


    {
        "categoria": "ritmo",
        "pergunta": "Qual ritmo você prefere?",
        "opcoes": [
            {"valor": "Rapido", "texto": "Uma leitura rápida e divertida"},
            {"valor": "Lento", "texto": "Um desenvolvimento mais tranquilo"},
            {"valor": "Acao", "texto": "Muita ação e acontecimentos"},
            {"valor": "Emocional", "texto": "Uma história mais emocional"}
        ]
    },

    {
        "categoria": "ritmo",
        "pergunta": "O que faz você não querer largar um livro?",
        "opcoes": [
            {"valor": "Rapido", "texto": "Capítulos que passam voando"},
            {"valor": "Lento", "texto": "Uma história construída aos poucos"},
            {"valor": "Acao", "texto": "Acontecimentos a todo momento"},
            {"valor": "Emocional", "texto": "Personagens e sentimentos intensos"}
        ]
    },

    {
        "categoria": "ritmo",
        "pergunta": "Escolha o ritmo perfeito para sua próxima leitura.",
        "opcoes": [
            {"valor": "Rapido", "texto": "Rápido e envolvente"},
            {"valor": "Lento", "texto": "Calmo e desenvolvido aos poucos"},
            {"valor": "Acao", "texto": "Cheio de ação"},
            {"valor": "Emocional", "texto": "Focado nas emoções"}
        ]
    },


    {
        "categoria": "foco",
        "pergunta": "O que você mais procura em um livro?",
        "opcoes": [
            {"valor": "Romance", "texto": "Um romance inesquecível"},
            {"valor": "Personagens", "texto": "Personagens marcantes"},
            {"valor": "Suspense", "texto": "Mistérios e descobertas"},
            {"valor": "Fantasia", "texto": "Fantasia e magia"}
        ]
    },

    {
        "categoria": "foco",
        "pergunta": "O que mais prende sua atenção em uma história?",
        "opcoes": [
            {"valor": "Romance", "texto": "A relação entre os personagens"},
            {"valor": "Personagens", "texto": "Personagens complexos"},
            {"valor": "Suspense", "texto": "Segredos e reviravoltas"},
            {"valor": "Fantasia", "texto": "Um universo fantástico"}
        ]
    },

    {
        "categoria": "foco",
        "pergunta": "Se tivesse que escolher apenas um elemento, qual seria?",
        "opcoes": [
            {"valor": "Romance", "texto": "Uma grande história de amor"},
            {"valor": "Personagens", "texto": "Personagens inesquecíveis"},
            {"valor": "Suspense", "texto": "Um mistério para resolver"},
            {"valor": "Fantasia", "texto": "Um mundo completamente novo"}
        ]
    },


    {
        "categoria": "tipo_historia",
        "pergunta": "Que tipo de história você escolheria primeiro?",
        "opcoes": [
            {"valor": "Romantica", "texto": "Uma história de amor"},
            {"valor": "Fantastica", "texto": "Um mundo fantástico"},
            {"valor": "Misteriosa", "texto": "Um grande mistério"},
            {"valor": "Intensa", "texto": "Uma história intensa e emocionante"}
        ]
    },

    {
        "categoria": "tipo_historia",
        "pergunta": "Qual dessas ideias faria você pegar um livro imediatamente?",
        "opcoes": [
            {"valor": "Romantica", "texto": "Um romance cheio de sentimentos"},
            {"valor": "Fantastica", "texto": "Uma aventura em outro universo"},
            {"valor": "Misteriosa", "texto": "Um segredo que precisa ser descoberto"},
            {"valor": "Intensa", "texto": "Uma história cheia de tensão"}
        ]
    },

    {
        "categoria": "tipo_historia",
        "pergunta": "Escolha a história que mais desperta sua curiosidade.",
        "opcoes": [
            {"valor": "Romantica", "texto": "Duas pessoas destinadas a se encontrar"},
            {"valor": "Fantastica", "texto": "Um reino cheio de magia"},
            {"valor": "Misteriosa", "texto": "Um caso que ninguém conseguiu solucionar"},
            {"valor": "Intensa", "texto": "Uma história cheia de conflitos"}
        ]
    },


    {
        "categoria": "final_leitura",
        "pergunta": "Como você quer terminar a leitura?",
        "opcoes": [
            {"valor": "Sorrindo", "texto": "Sorrindo"},
            {"valor": "Apaixonada", "texto": "Apaixonada pela história"},
            {"valor": "Chocada", "texto": "Chocada com o final"},
            {"valor": "Pensando", "texto": "Pensando sobre a história"}
        ]
    },

    {
        "categoria": "final_leitura",
        "pergunta": "Qual sensação você gostaria de ter ao fechar o livro?",
        "opcoes": [
            {"valor": "Sorrindo", "texto": "Um sorriso no rosto"},
            {"valor": "Apaixonada", "texto": "Completamente apaixonada pela história"},
            {"valor": "Chocada", "texto": "Sem acreditar no que aconteceu"},
            {"valor": "Pensando", "texto": "Pensando sobre tudo que li"}
        ]
    },

    {
        "categoria": "final_leitura",
        "pergunta": "Que tipo de final combina mais com você?",
        "opcoes": [
            {"valor": "Sorrindo", "texto": "Um final feliz"},
            {"valor": "Apaixonada", "texto": "Um final romântico"},
            {"valor": "Chocada", "texto": "Um final surpreendente"},
            {"valor": "Pensando", "texto": "Um final que deixa perguntas"}
        ]
    },


    {
        "categoria": "livro_favorito",
        "pergunta": "Qual desses livros você escolheria?",
        "opcoes": [
            {"valor": "Assistente do Vilão", "texto": "Assistente do Vilão"},
            {"valor": "Fearless", "texto": "Fearless"},
            {"valor": "Quarta Asa", "texto": "Quarta Asa"},
            {"valor": "Outro", "texto": "Outro"}
        ]
    },

    {
        "categoria": "livro_favorito",
        "pergunta": "Qual desses títulos mais chama sua atenção?",
        "opcoes": [
            {"valor": "Assistente do Vilão", "texto": "Assistente do Vilão"},
            {"valor": "Fearless", "texto": "Fearless"},
            {"valor": "Caraval", "texto": "Caraval"},
            {"valor": "Outro", "texto": "Outro"}
        ]
    },

    {
        "categoria": "livro_favorito",
        "pergunta": "Qual desses livros você colocaria na sua lista de leitura?",
        "opcoes": [
            {"valor": "Assistente do Vilão", "texto": "Assistente do Vilão"},
            {"valor": "Fearless", "texto": "Fearless"},
            {"valor": "Quarta Asa", "texto": "Quarta Asa"},
            {"valor": "Outro", "texto": "Outro"}
        ]
    }

]

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if request.method == "GET":

        perguntas = []

        categorias = [
            "genero",
            "romance",
            "clima",
            "ritmo",
            "foco",
            "tipo_historia",
            "final_leitura",
            "livro_favorito"
        ]

        for categoria in categorias:

            perguntas_categoria = [
                pergunta
                for pergunta in PERGUNTAS_QUIZ
                if pergunta["categoria"] == categoria
            ]

            pergunta_escolhida = random.choice(perguntas_categoria)

            perguntas.append(pergunta_escolhida)

        random.shuffle(perguntas)

        return render_template(
            "quiz.html",
            perguntas=perguntas
        )

    respostas = {
        "genero": request.form.get("genero"),
        "romance": request.form.get("romance"),
        "clima": request.form.get("clima"),
        "ritmo": request.form.get("ritmo"),
        "foco": request.form.get("foco"),
        "tipo_historia": request.form.get("tipo_historia"),
        "final_leitura": request.form.get("final_leitura"),
        "livro_favorito": request.form.get("livro_favorito")
    }

    nova_resposta = RespostaQuiz(
        genero=respostas["genero"],
        romance=respostas["romance"],
        clima=respostas["clima"],
        ritmo=respostas["ritmo"],
        foco=respostas["foco"],
        tipo_historia=respostas["tipo_historia"],
        final_leitura=respostas["final_leitura"],
        livro_favorito=respostas["livro_favorito"]
    )

    db.session.add(nova_resposta)
    db.session.commit()

    if "email" in session:

        usuario = Usuario.query.filter_by(
            email=session["email"]
        ).first()

        if usuario:
            atualizar_conquistas(usuario)

    return redirect("/resultado_quiz")

@app.route("/adicionar_livro", methods=["POST"])
def adicionar_livro():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(email=session["email"]).first()

    if not usuario or not usuario.is_admin:
        return redirect("/catalogo")

    titulo = request.form["titulo"]
    autor = request.form["autor"]
    genero = request.form["genero"]
    preco = float(request.form["preco"].strip().replace(",", "."))

    file = request.files["imagem"]

    if file:
        filename = secure_filename(file.filename)

        path = os.path.join(
            "static",
            "imagens",
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

@app.route("/resultado_quiz")
def resultado_quiz():

    if "email" not in session:
        return redirect("/login")

    resposta = RespostaQuiz.query.order_by(
        RespostaQuiz.id.desc()
    ).first()

    if not resposta:
        return redirect("/quiz")

    # Primeiro tenta usar o livro escolhido na pergunta do quiz
    if resposta.livro_favorito and resposta.livro_favorito != "Outro":

        livro = LivroDB.query.filter_by(
            titulo=resposta.livro_favorito
        ).first()

        if livro:
            return render_template(
                "resultado_quiz.html",
                livro=livro
            )

    # Se não encontrou, procura pelo gênero escolhido
    livros = LivroDB.query.filter_by(
        genero=resposta.genero
    ).all()

    # Se não houver livros exatamente nesse gênero,
    # procura por livros que tenham parte do gênero
    if not livros:

        todos_livros = LivroDB.query.all()

        livros = [
            livro
            for livro in todos_livros
            if resposta.genero.lower() in livro.genero.lower()
            or livro.genero.lower() in resposta.genero.lower()
        ]

    # Se ainda não encontrou, pega qualquer livro do banco
    if not livros:
        livros = LivroDB.query.all()

    if not livros:
        return "Nenhum livro cadastrado no banco de dados.", 404

    livro = random.choice(livros)

    return render_template(
        "resultado_quiz.html",
        livro=livro
    )

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
        session["senha_temp"] = generate_password_hash(senha)

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
        codigo_session = session.get("codigo")
        print("DIGITADO:", codigo_digitado)
        print("SESSION:", codigo_session)

        if not codigo_session:
            return "Sessão expirada, volte ao cadastro"

        if str(codigo_digitado).strip() != str(codigo_session).strip():
            return "Código inválido"

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

    return render_template("verificar.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario and check_password_hash(
            usuario.senha,
            senha
        ):
            session["email"] = usuario.email
            return redirect("/catalogo")

        return "Login inválido"

    return render_template("login.html")

@app.route("/catalogo")
def catalogo_livros():

    if "email" not in session:
        return redirect("/cadastro")

    livros = LivroDB.query.all()

    return render_template(
        "catalogo.html",
        livros=livros
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
                atualizar_conquistas(usuario)

            break

    return redirect("/favoritos")

@app.route("/livro/<titulo>")
def pagina_livro(titulo):
    livro_encontrado = None

    for livro in catalogo:
        if livro.titulo == titulo:
            livro_encontrado = livro
            break

    if livro_encontrado is None:
        return "Livro não encontrado", 404

    relacionados = []

    for livro in catalogo:
        if (
            livro.genero.lower() == livro_encontrado.genero.lower()
            and livro.titulo != livro_encontrado.titulo
        ):
            relacionados.append(livro)

    relacionados = relacionados[:4]

    avaliacoes = Avaliacao.query.filter_by(
        livro_titulo=livro_encontrado.titulo
    ).all()

    if avaliacoes:
        media = sum(
            avaliacao.nota
            for avaliacao in avaliacoes
        ) / len(avaliacoes)
    else:
        media = 0

    avaliacoes_com_usuarios = []

    for avaliacao in avaliacoes:
        usuario_avaliacao = Usuario.query.get(
            avaliacao.usuario_id
        )

        avaliacoes_com_usuarios.append({
            "avaliacao": avaliacao,
            "usuario": usuario_avaliacao
        })

    return render_template(
        "livro.html",
        livro=livro_encontrado,
        relacionados=relacionados,
        avaliacoes=avaliacoes_com_usuarios,
        media=media
    )

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

@app.route("/generos")
def generos():
    generos_disponiveis = []

    for livro in catalogo:
        if livro.genero not in generos_disponiveis:
            generos_disponiveis.append(livro.genero)

    return render_template(
        "generos.html",
        generos=generos_disponiveis
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

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/cadastro")

    itens = usuario.carrinho_json or []

    total = sum(
        item["preco"] * item.get("quantidade", 1)
        for item in itens
    )

    quantidade_total = sum(
        item.get("quantidade", 1)
        for item in itens
    )

    return render_template(
        "carrinho.html",
        itens=itens,
        total=total,
        quantidade_total=quantidade_total
    )

@app.route("/alterar_quantidade/<int:indice>/<acao>")
def alterar_quantidade(indice, acao):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/login")

    carrinho = (usuario.carrinho_json or []).copy()

    if indice < 0 or indice >= len(carrinho):
        return redirect("/carrinho")

    quantidade_atual = int(
        carrinho[indice].get("quantidade", 1)
    )

    if acao == "aumentar":
        quantidade_atual += 1

    elif acao == "diminuir":
        quantidade_atual -= 1

    if quantidade_atual <= 0:
        carrinho.pop(indice)
    else:
        carrinho[indice]["quantidade"] = quantidade_atual

    usuario.carrinho_json = carrinho

    db.session.commit()

    return redirect("/carrinho")

@app.route("/adicionar_carrinho/<path:titulo>")
def adicionar_carrinho(titulo):

    print("================================")
    print("LIVRO RECEBIDO:", titulo)
    print("================================")

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

    carrinho = (usuario.carrinho_json or []).copy()

    # Verifica se o livro já está no carrinho
    for item in carrinho:

        if (
            item["titulo"] == titulo
            and item["formato"] == formato
        ):

            item["quantidade"] = (
                item.get("quantidade", 1) + 1
            )

            usuario.carrinho_json = carrinho

            db.session.commit()

            return redirect("/carrinho")

    # Se ainda não estiver no carrinho
    for livro in catalogo:

        if livro.titulo == titulo:

            carrinho.append({
                "titulo": livro.titulo,
                "autor": livro.autor,
                "preco": livro.preco,
                "imagem": livro.imagem,
                "formato": formato,
                "quantidade": 1
            })

            usuario.carrinho_json = carrinho

            db.session.commit()

            print("LIVRO ADICIONADO:", livro.titulo)

            return redirect("/carrinho")

    print("LIVRO NÃO ENCONTRADO:", titulo)

    return "Livro não encontrado", 404

@app.route("/remover_carrinho/<int:indice>")
def remover_carrinho(indice):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/login")

    carrinho = (usuario.carrinho_json or []).copy()

    if 0 <= indice < len(carrinho):
        carrinho.pop(indice)

    usuario.carrinho_json = carrinho

    db.session.commit()

    return redirect("/carrinho")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/login")

    carrinho = usuario.carrinho_json or []

    total = sum(
        item["preco"] * item.get("quantidade", 1)
        for item in carrinho
    )

    if request.method == "POST":

        endereco = {
            "nome": request.form["nome"],
            "cep": request.form["cep"],
            "rua": request.form["rua"],
            "numero": request.form["numero"],
            "complemento": request.form["complemento"],
            "bairro": request.form["bairro"],
            "cidade": request.form["cidade"],
            "estado": request.form["estado"]
        }

        session["endereco"] = endereco

        return redirect("/pagar")

    return render_template(
        "checkout.html",
        carrinho=carrinho,
        total=total
    )

@app.route("/confirmar_compra")
def confirmar_compra():
    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/cadastro")

    itens_comprados = usuario.carrinho_json.copy()

    for item in itens_comprados:

        livro_encontrado = None

        for livro in catalogo:
            if livro.titulo == item["titulo"]:
                livro_encontrado = livro
                break

        if livro_encontrado:

            quantidade = item.get("quantidade", 1)

            for _ in range(quantidade):

                venda = Venda(
                    usuario_id=usuario.id,
                    livro_titulo=livro_encontrado.titulo,
                    genero=livro_encontrado.genero,
                    preco=item["preco"]
                )

                db.session.add(venda)

        if item["formato"] == "ebook":

            titulo = item["titulo"]
            pdf_path = f"static/ebooks/{titulo}.pdf"

            try:
                enviar_ebook(
                    usuario.email,
                    titulo,
                    pdf_path
                )

            except:
                print(
                    "Erro ao enviar ebook:",
                    titulo
                )

    usuario.carrinho_json = []

    db.session.commit()

    atualizar_conquistas(usuario)

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
        item["preco"] * item.get("quantidade", 1)
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

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/cadastro")

    senha_atual = request.form["senha_atual"]
    nova_senha = request.form["nova_senha"]

    if not check_password_hash(
        usuario.senha,
        senha_atual
    ):
        return "Senha atual incorreta"

    usuario.senha = generate_password_hash(nova_senha)

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

@app.route("/avaliar/<titulo>", methods=["POST"])
def avaliar(titulo):

    if "email" not in session:
        return redirect("/login")

    usuario = Usuario.query.filter_by(
        email=session["email"]
    ).first()

    if not usuario:
        return redirect("/login")

    nota = int(request.form["nota"])
    comentario = request.form["comentario"].strip()

    if nota < 1 or nota > 5:
        return "Nota inválida"

    if not comentario:
        return "Escreva um comentário"

    avaliacao_existente = Avaliacao.query.filter_by(
        usuario_id=usuario.id,
        livro_titulo=titulo
    ).first()

    if avaliacao_existente:
        avaliacao_existente.nota = nota
        avaliacao_existente.comentario = comentario
    else:
        avaliacao = Avaliacao(
            usuario_id=usuario.id,
            livro_titulo=titulo,
            nota=nota,
            comentario=comentario
        )

        db.session.add(avaliacao)

    db.session.commit()
    atualizar_conquistas(usuario)

    return redirect("/livro/" + titulo)

with app.app_context():

    db.create_all()

    admin = Usuario.query.filter_by(
        email="inkdreams61@gmail.com"
    ).first()

    if not admin:
        admin = Usuario(
            nome="Admin",
            email="inkdreams61@gmail.com",
            senha=generate_password_hash("123"),
            is_admin=True
        )

        db.session.add(admin)

    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        carregar_livros_no_banco()

    app.run(debug=True)