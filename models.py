from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()
bcrypt = Bcrypt()

# Modelo do Usuário
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    favoritos = db.relationship('Favoritos', back_populates='usuario', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

    def verificar_senha(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, senha)

# Modelo do Artigo
class Artigos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False, unique=True)
    imagem = db.Column(db.String(255), nullable=True)
    fonte = db.Column(db.String(255), nullable=False)
    favoritos = db.relationship('Favoritos', back_populates='artigo', lazy=True)

    def __repr__(self):
        return f"<Artigo {self.titulo}>"

# Modelo da relação de favoritos
class Favoritos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    artigo_id = db.Column(db.Integer, db.ForeignKey('artigos.id'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='favoritos')
    artigo = db.relationship('Artigos', back_populates='favoritos')


