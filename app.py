# Importa o necessário do Flask
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Cria a aplicação Flask
app = Flask(__name__)

# Chave secreta necessária para usar sessão e flash messages
app.secret_key = 'devlog_secret_2024'

# ─────────────────────────────────────────
# Dados simulados (sem banco de dados ainda)
# ─────────────────────────────────────────

usuarios = [
    {'id': 1, 'nome': 'Rian Silva',     'email': 'rian@email.com',    'senha': '1234'},
    {'id': 2, 'nome': 'Lucas Mendes',   'email': 'lucas@email.com',   'senha': '1234'},
    {'id': 3, 'nome': 'Ana Souza',      'email': 'ana@email.com',     'senha': '1234'},
    {'id': 4, 'nome': 'Pedro Alves',    'email': 'pedro@email.com',   'senha': '1234'},
    {'id': 5, 'nome': 'Julia Costa',    'email': 'julia@email.com',   'senha': '1234'},
]

linguagens = [
    {'id': 1, 'nome': 'Python',     'status': 'Estudando',      'nota': 'Foco em Flask e automação',         'nivel': 'Intermediário'},
    {'id': 2, 'nome': 'JavaScript', 'status': 'Estudando',      'nota': 'Aprendendo DOM e eventos',          'nivel': 'Iniciante'},
    {'id': 3, 'nome': 'Java',       'status': 'Quero estudar',  'nota': 'Para entender POO mais fundo',      'nivel': 'Iniciante'},
    {'id': 4, 'nome': 'C#',         'status': 'Quero estudar',  'nota': 'Interessante para games com Unity', 'nivel': 'Iniciante'},
    {'id': 5, 'nome': 'TypeScript', 'status': 'Estudando',      'nota': 'Complemento do JavaScript',        'nivel': 'Iniciante'},
]

recursos = [
    {'id': 1, 'titulo': 'Flask - Documentação Oficial', 'tipo': 'Site',   'url': 'https://flask.palletsprojects.com', 'linguagem': 'Python',     'nota': 'Referência principal'},
    {'id': 2, 'titulo': 'Curso JS - The Odin Project',  'tipo': 'Site',   'url': 'https://www.theodinproject.com',   'linguagem': 'JavaScript', 'nota': 'Gratuito e muito bom'},
    {'id': 3, 'titulo': 'Python para Iniciantes',       'tipo': 'Vídeo',  'url': 'https://www.youtube.com',          'linguagem': 'Python',     'nota': 'Ótimo para revisão'},
    {'id': 4, 'titulo': 'MDN Web Docs',                 'tipo': 'Site',   'url': 'https://developer.mozilla.org',    'linguagem': 'JavaScript', 'nota': 'Melhor referência web'},
    {'id': 5, 'titulo': 'Curso Java Completo',          'tipo': 'Vídeo',  'url': 'https://www.youtube.com',          'linguagem': 'Java',       'nota': 'Quando começar Java'},
]


# ─────────────────────────────────────────
# Rotas públicas (sem login)
# ─────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = next((u for u in usuarios if u['email'] == email and u['senha'] == senha), None)

        if usuario:
            session['usuario_id']   = usuario['id']
            session['usuario_nome'] = usuario['nome']
            flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
            return redirect(url_for('listar_usuarios'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome           = request.form.get('nome')
        email          = request.form.get('email')
        senha          = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')

        if not nome or not email or not senha:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('cadastro.html')

        if senha != confirma_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('cadastro.html')

        novo_id = len(usuarios) + 1
        usuarios.append({'id': novo_id, 'nome': nome, 'email': email, 'senha': senha})
        flash('Cadastro realizado! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────
# Usuários
# ─────────────────────────────────────────

@app.route('/usuarios/listar')
def listar_usuarios():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('usuarios/listar_usuarios.html', usuarios=usuarios)


@app.route('/usuarios/inserir', methods=['GET', 'POST'])
def inserir_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome  = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not nome or not email or not senha:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('usuarios/inserir_usuario.html')

        novo_id = len(usuarios) + 1
        usuarios.append({'id': novo_id, 'nome': nome, 'email': email, 'senha': senha})
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))

    return render_template('usuarios/inserir_usuario.html')


@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = next((u for u in usuarios if u['id'] == id), None)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('listar_usuarios'))

    if request.method == 'POST':
        nome  = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not nome or not email:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('usuarios/editar_usuario.html', usuario=usuario)

        usuario['nome']  = nome
        usuario['email'] = email
        if senha:
            usuario['senha'] = senha

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))

    return render_template('usuarios/editar_usuario.html', usuario=usuario)


@app.route('/usuarios/excluir/<int:id>')
def excluir_usuario(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    global usuarios
    usuarios = [u for u in usuarios if u['id'] != id]
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('listar_usuarios'))


# ─────────────────────────────────────────
# Linguagens
# ─────────────────────────────────────────

@app.route('/linguagens/listar')
def listar_linguagens():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('linguagens/listar_linguagens.html', linguagens=linguagens)


@app.route('/linguagens/inserir', methods=['GET', 'POST'])
def inserir_linguagem():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome   = request.form.get('nome')
        status = request.form.get('status')
        nivel  = request.form.get('nivel')
        nota   = request.form.get('nota')

        if not nome or not status or not nivel:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('linguagens/inserir_linguagem.html')

        novo_id = len(linguagens) + 1
        linguagens.append({'id': novo_id, 'nome': nome, 'status': status, 'nivel': nivel, 'nota': nota})
        flash('Linguagem adicionada com sucesso!', 'success')
        return redirect(url_for('listar_linguagens'))

    return render_template('linguagens/inserir_linguagem.html')


@app.route('/linguagens/editar/<int:id>', methods=['GET', 'POST'])
def editar_linguagem(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    linguagem = next((l for l in linguagens if l['id'] == id), None)
    if not linguagem:
        flash('Linguagem não encontrada.', 'danger')
        return redirect(url_for('listar_linguagens'))

    if request.method == 'POST':
        nome   = request.form.get('nome')
        status = request.form.get('status')
        nivel  = request.form.get('nivel')
        nota   = request.form.get('nota')

        if not nome or not status or not nivel:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('linguagens/editar_linguagem.html', linguagem=linguagem)

        linguagem['nome']   = nome
        linguagem['status'] = status
        linguagem['nivel']  = nivel
        linguagem['nota']   = nota

        flash('Linguagem atualizada com sucesso!', 'success')
        return redirect(url_for('listar_linguagens'))

    return render_template('linguagens/editar_linguagem.html', linguagem=linguagem)


@app.route('/linguagens/excluir/<int:id>')
def excluir_linguagem(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    global linguagens
    linguagens = [l for l in linguagens if l['id'] != id]
    flash('Linguagem excluída com sucesso!', 'success')
    return redirect(url_for('listar_linguagens'))


# ─────────────────────────────────────────
# Recursos
# ─────────────────────────────────────────

@app.route('/recursos/listar')
def listar_recursos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('recursos/listar_recursos.html', recursos=recursos)


@app.route('/recursos/inserir', methods=['GET', 'POST'])
def inserir_recurso():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo    = request.form.get('titulo')
        tipo      = request.form.get('tipo')
        url       = request.form.get('url')
        linguagem = request.form.get('linguagem')
        nota      = request.form.get('nota')

        if not titulo or not tipo or not url:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('recursos/inserir_recurso.html', linguagens=linguagens)

        novo_id = len(recursos) + 1
        recursos.append({'id': novo_id, 'titulo': titulo, 'tipo': tipo, 'url': url, 'linguagem': linguagem, 'nota': nota})
        flash('Recurso adicionado com sucesso!', 'success')
        return redirect(url_for('listar_recursos'))

    return render_template('recursos/inserir_recurso.html', linguagens=linguagens)


@app.route('/recursos/editar/<int:id>', methods=['GET', 'POST'])
def editar_recurso(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    recurso = next((r for r in recursos if r['id'] == id), None)
    if not recurso:
        flash('Recurso não encontrado.', 'danger')
        return redirect(url_for('listar_recursos'))

    if request.method == 'POST':
        titulo    = request.form.get('titulo')
        tipo      = request.form.get('tipo')
        url       = request.form.get('url')
        linguagem = request.form.get('linguagem')
        nota      = request.form.get('nota')

        if not titulo or not tipo or not url:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('recursos/editar_recurso.html', recurso=recurso, linguagens=linguagens)

        recurso['titulo']    = titulo
        recurso['tipo']      = tipo
        recurso['url']       = url
        recurso['linguagem'] = linguagem
        recurso['nota']      = nota

        flash('Recurso atualizado com sucesso!', 'success')
        return redirect(url_for('listar_recursos'))

    return render_template('recursos/editar_recurso.html', recurso=recurso, linguagens=linguagens)


@app.route('/recursos/excluir/<int:id>')
def excluir_recurso(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    global recursos
    recursos = [r for r in recursos if r['id'] != id]
    flash('Recurso excluído com sucesso!', 'success')
    return redirect(url_for('listar_recursos'))


# Equipe
@app.route('/equipe')
def equipe():
    return render_template('sobre_equipe.html')


# Roda a aplicação em modo debug
if __name__ == '__main__':
    app.run(debug=True)
