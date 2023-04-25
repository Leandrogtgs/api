from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# definindo api

api = Flask(__name__)


# configurando api/banco de dados

api.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

api.config['SECRET_KEY'] = 'SENHASECRETA123'



# definindo intancia SQLAlchemy

db = SQLAlchemy(api)

db:SQLAlchemy


# definindo estrutura da tabela de Postagem

class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


# definindo estrutura da tabela de autor

class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')


# inicializando banco de dados
def inicializar_banco():
    with api.app_context():
        # excluindo estrururas existentes
        db.drop_all()
 
        # criando nova estrutura definida
        db.create_all()

        # adicionando autor adimin

        autor = Autor(nome = 'leandro', email='autor1@gmail.com', senha='12345', admin=True)

        db.session.add(autor)

        db.session.commit()

if __name__ == "__main__":
    inicializar_banco()
