from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from models import db, Usuario, bcrypt, Artigos,Favoritos
from config import DATABASE_URL, SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, NEWS_API_KEY, BASE_URL
from dotenv import load_dotenv
import requests
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL:", DATABASE_URL)  # Adiciona esta linha para depuração

# Converte postgres:// para postgresql:// se necessário
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL



# Configuração do Banco de Dados
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SECRET_KEY"] = SECRET_KEY

db.init_app(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Configuração do OAuth
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    client_kwargs={
        'scope': 'openid email profile',
        'token_endpoint_auth_method': 'client_secret_post',
        'userinfo_endpoint': 'https://openidconnect.googleapis.com/v1/userinfo',
    },
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'  # Adicione esta linha!
)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rota para a página inicial
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login/google")
def login_google():
    return google.authorize_redirect(
        url_for('google_authorized', _external=True, _scheme='https'), 
        prompt="consent"
    )



# Rota de callback após o login com o Google
@app.route("/login/google/callback")
def google_authorized():
    token = google.authorize_access_token()
    if not token:
        return jsonify({"erro": "Falha no login com o Google."}), 400

    session['google_token'] = token  # Salva o token na sessão
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

    # Verifica se o usuário já existe no banco de dados pelo e-mail
    usuario = Usuario.query.filter_by(email=user_info['email']).first()

    if not usuario:
        # Caso o usuário não exista, cria um novo usuário
        usuario = Usuario(
            nome=user_info['name'],
            email=user_info['email']
        )
        db.session.add(usuario)
        db.session.commit()

    login_user(usuario)
    return redirect(url_for('noticias'))  # Redireciona para a página de notícias
    

# Rota para cadastrar um novo usuário
@app.route("/cadastro", methods=["POST"])
def cadastrar_usuario():
    dados = request.json
    if not dados or not dados.get("nome") or not dados.get("email") or not dados.get("senha"):
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    if Usuario.query.filter_by(email=dados["email"]).first():
        return jsonify({"erro": "E-mail já cadastrado"}), 400

    novo_usuario = Usuario(nome=dados["nome"], email=dados["email"])
    novo_usuario.set_senha(dados["senha"])

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201

# Rota para login
@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    usuario = Usuario.query.filter_by(email=dados["email"]).first()

    if usuario and usuario.verificar_senha(dados["senha"]):
        login_user(usuario)
        return jsonify({"mensagem": f"Bem-vindo, {usuario.nome}!"})

    return jsonify({"erro": "Credenciais inválidas"}), 401

# Rota protegida (somente logado)
@app.route("/perfil", methods=["GET"])
@login_required
def perfil():
    return jsonify({"nome": current_user.nome, "email": current_user.email})

# Rota para logout
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"mensagem": "Logout realizado com sucesso!"})

@app.route('/noticias')
def noticias():
    return render_template('noticias.html')

# Rota para buscar as notícias em tempo real
@app.route('/api/noticias')
def api_noticias():
    categoria = request.args.get('categoria', 'general')  # Padrão: general
    url = f"{BASE_URL}?category={categoria}&apiKey={NEWS_API_KEY}"

    resposta = requests.get(url)
    dados = resposta.json()

    if resposta.status_code == 200 and dados.get('articles'):
        return jsonify(dados['articles'])
    else:
        return jsonify({"erro": "Não foi possível obter as notícias"}), 500

# Rota para buscar os favoritos no banco
@app.route('/favoritos', methods=['GET'])
@login_required
def listar_favoritos():
    favoritos = Favoritos.query.filter_by(usuario_id=current_user.id).all()
    
    lista_artigos = [{
        "id": favorito.artigo.id,
        "titulo": favorito.artigo.titulo,
        "descricao": favorito.artigo.descricao,
        "url": favorito.artigo.url,
        "imagem": favorito.artigo.imagem,
        "fonte": favorito.artigo.fonte
    } for favorito in favoritos]

    return jsonify(lista_artigos)


# Rota para favoritar uma notícia
@app.route('/favoritar', methods=['POST'])
@login_required
def favoritar():
    dados = request.json
    artigo = Artigos.query.filter_by(url=dados.get('url')).first()

    if not artigo:
        artigo = Artigos(
            titulo=dados.get('titulo'),
            descricao=dados.get('descricao'),
            url=dados.get('url'),
            imagem=dados.get('imagem'),
            fonte=dados.get('fonte')
        )
        db.session.add(artigo)
        db.session.commit()

    # Verifica se o usuário já favoritou esse artigo
    favorito_existente = Favoritos.query.filter_by(usuario_id=current_user.id, artigo_id=artigo.id).first()

    if favorito_existente:
        return jsonify({"erro": "Artigo já favoritado"}), 400

    # Relaciona o artigo ao usuário
    novo_favorito = Favoritos(usuario_id=current_user.id, artigo_id=artigo.id)
    db.session.add(novo_favorito)
    db.session.commit()

    return jsonify({"mensagem": "Notícia favoritada com sucesso!"})




if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Criar tabelas no banco de dados
    app.run(debug=True)
