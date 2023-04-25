from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, api, db
import jwt
from datetime import datetime, timedelta
from functools import wraps

# comentario
# definindo solicitacão de token para rotas

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # verificando se o token foi passado:
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        # verificando se o token não foi passado:
        if not token:
            return jsonify({'mensagem': 'token não identificado.'}, 403)
        
        # verificando se o usuário está no banco de dados:
        try:
            resultado = jwt.decode(token, api.config['SECRET_KEY'], algorithms=['HS256'])

            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()

        except:
            return jsonify({'mensagem': 'token inválido'}, 403)
        
        return f(autor, *args, **kwargs)
    
    return decorated


# definindo rota de login:

@api.route('/login')
def login():

    # extraindo informacões de autenticacão:
    auth = request.authorization

    # verificando se autenticacão foi feita corretamente:
    if not auth or not auth.username or not auth.password:
        # retornando tela de login para usuário caso autenticacão não tenha sido feita:
        return make_response('Usuário não identificado', 401, {'WWW-Authenticate': 'Basic realm="Login inválido!"'})
    
    # verificando se o login está no banco de dados:
    usuario = Autor.query.filter_by(nome=auth.username).first()

    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login inválido!"'})
    
    # verificando se a senha está no banco de dados:
    if auth.password == usuario.senha:
        # gerando token:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                            api.config['SECRET_KEY'])
        
        # retornando token caso senha esteja correta:
        return jsonify({'token': token})
    
    return make_response('Senha inválida', 401, {'WWW-Authenticate': 'Basic realm="Login inválido!"'})


# GET - extraindo e exibindo recursos da api

@api.route('/postagens')
@token_obrigatorio
def exibir_postagens(autor):

    postagens = Postagem.query.all()

    lista_postagens = []

    for postagem in postagens:

        postagem_atual = {}

        postagem_atual['id_postagem'] = postagem.id_postagem
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor

        lista_postagens.append(postagem_atual)

    return jsonify({'postagens': lista_postagens})


# GET ID - extraindo postagem especifica

@api.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_endpoint_id(autor, id_postagem):
    
    try:
        postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

        postagem_atual = {}

        postagem_atual['id_postagem'] = postagem.id_postagem
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor

        return jsonify({'postagem': postagem_atual}, 200)
    except:

        return jsonify({"mensagem": 'não foi possivel encontrar a postagem'}, 403)



# POST - inserindo novo recurso na api

@api.route('/postagens', methods=['POST'])
@token_obrigatorio
def post_recurso(autor):
    nova_postagem = request.get_json()

    postagem = Postagem(titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)

    db.session.commit()

    return jsonify({'mensagem': 'nova postagem adicionada.'}, 200)


# PUT - alterando um recurso da api

@api.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    
    postagem_edit = request.get_json()

    try:
        postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    except:
        return jsonify('postagem não encontrada.', 403)

    try:
        postagem.titulo = postagem_edit['titulo']
    except:
        pass

    db.session.commit()

    return jsonify({'mensagem': 'postagem alterada com sucesso.'}, 201)

    
# DELETE - excluindo recursos da api

@api.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def deletar_recurso(autor, id_postagem):
    
    try:
        postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

        db.session.delete(postagem)

        db.session.commit()

        return jsonify({'mensagem': f'postagem {postagem} excluida com sucesso'}, 201)
    
    except:
        return jsonify({'mensagem': 'postagem não encontrada'}, 403)
    
    
    


# exibindo autores

@api.route('/autores')
@token_obrigatorio
def exibir_autores(autor):
    autores = Autor.query.all()
    lista_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        
        lista_autores.append(autor_atual)

    return jsonify({'autores': lista_autores})


# exibindo autor pelo id

@api.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def exibir_autor(autor, id_autor):
    try:
        autor = Autor.query.filter_by(id_autor=id_autor).first()

        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email

        return jsonify({'autor': autor_atual}, 200)
    
    except:
        return jsonify('autor não encontrado.', 403)


# adicionando novo autor

@api.route('/autores', methods=['POST'])
@token_obrigatorio
def adicionar_autor(autor):
    novo_autor = request.get_json()

    autor = Autor(nome=novo_autor['nome'], email=novo_autor['email'], senha=novo_autor['senha'])

    db.session.add(autor)

    db.session.commit()

    return jsonify('novo autor adicionado com sucesso!', 200)



# editando autores já existentes

@api.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def editar_autor(autor, id_autor):
    autor_edit = request.get_json()

    try:
        autor = Autor.query.filter_by(id_autor=id_autor).first()
    except:
        return jsonify({"mensagem": "autor não encontrado."}, 403)
    
    try:
        autor.nome = autor_edit['nome']

    except:
        pass

    try:
        autor.nemail = autor_edit['email']

    except:
        pass

    try:
        autor.senha = autor_edit['senha']
        
    except:
        pass


    db.session.commit()

    return jsonify({"mensagem": "autor alterado com sucesso."}, 200)


# excluindo autor

@api.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    try:
        autor = Autor.query.filter_by(id_autor=id_autor).first()

        db.session.delete(autor)

        db.session.commit()

        return jsonify({"mensagem": f"autor {autor} excluido."}, 200)  

    except:
        return jsonify({"mensagem": "não foi possível excluir o autor indicado."}, 403)


# rodando/inicializando a api

api.run(port=5000, host='localhost', debug=True)
