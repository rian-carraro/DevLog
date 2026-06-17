from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import execute_one, iniciar_bd, execute_query
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'devlog_secret_2026'

iniciar_bd() # inicia o BD e as tabelas


def garantir_admin():
    """Cria um administrador padrão caso não exista nenhum usuário (evita lockout)."""
    try:
        total = execute_one('SELECT COUNT(*) AS total FROM usuario')
        if total and total['total'] == 0:
            funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',))
            if not funcao:
                execute_query(
                    """INSERT INTO funcoes (nome, status, descricao,
                       gerenciar_funcoes, gerenciar_usuarios, gerenciar_linguagens, gerenciar_recursos)
                       VALUES (%s, 'Ativo', %s, 1, 1, 1, 1)""",
                    ('Administrador', 'Acesso total ao sistema')
                )
                funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',))
            execute_query(
                """INSERT INTO usuario (nome, email, senha, funcao_id)
                   VALUES (%s, %s, %s, %s)""",
                ('Administrador', 'admin@devlog.com',
                 generate_password_hash('admin1234'), funcao['id_funcao'])
            )
            print('Usuário administrador padrão criado: admin@devlog.com / admin1234')
    except Exception as e:
        print(f'Erro ao garantir admin: {e}')


garantir_admin()


# ── Rotas públicas ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        # Login sem verificação real — qualquer e-mail/senha entra
        usuario = execute_one(
            '''SELECT u.id_cliente, u.nome, u.email, u.senha,
                      f.nome AS funcao,
                      f.gerenciar_funcoes, f.gerenciar_usuarios,
                      f.gerenciar_linguagens, f.gerenciar_recursos
               FROM usuario AS u
               LEFT JOIN funcoes AS f ON u.funcao_id = f.id_funcao
               WHERE u.email = %s''',
            (email,)
        )

        # Se não encontrou nenhum usuário com esse e-mail, usa o primeiro cadastrado
        if not usuario:
            usuario = execute_one(
                '''SELECT u.id_cliente, u.nome, u.email, u.senha,
                          f.nome AS funcao,
                          f.gerenciar_funcoes, f.gerenciar_usuarios,
                          f.gerenciar_linguagens, f.gerenciar_recursos
                   FROM usuario AS u
                   LEFT JOIN funcoes AS f ON u.funcao_id = f.id_funcao
                   LIMIT 1'''
            )

        if not usuario:
            flash('Nenhum usuário cadastrado no sistema.', 'danger')
            return redirect(url_for('login'))

        session['usuario_id']            = usuario['id_cliente']
        session['usuario_nome']          = usuario['nome']
        session['usuario_funcao']        = usuario['funcao']
        session['gerenciar_funcoes']     = usuario['gerenciar_funcoes']
        session['gerenciar_usuarios']    = usuario['gerenciar_usuarios']
        session['gerenciar_linguagens']  = usuario['gerenciar_linguagens']
        session['gerenciar_recursos']    = usuario['gerenciar_recursos']

        flash(f'Bem-vindo, {usuario["nome"]}!', 'success')

        # Redireciona para a primeira área disponível
        if usuario['gerenciar_usuarios']:
            return redirect(url_for('listar_usuarios'))
        elif usuario['gerenciar_linguagens']:
            return redirect(url_for('listar_linguagens'))
        elif usuario['gerenciar_recursos']:
            return redirect(url_for('listar_recursos'))
        elif usuario['gerenciar_funcoes']:
            return redirect(url_for('listar_funcoes'))
        else:
            return redirect(url_for('equipe'))

    return render_template('login.html')


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('login'))


# ── Usuários ──────────────────────────────────────────────────────────────────

@app.route('/usuarios/listar')
def listar_usuarios():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    sql = '''
        SELECT
            u.id_cliente,
            u.nome AS nome,
            u.email,
            u.funcao_id,
            f.nome AS funcao
        FROM usuario AS u
        LEFT JOIN funcoes AS f ON u.funcao_id = f.id_funcao
        ORDER BY u.id_cliente DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('usuarios/listar_usuarios.html', dados=lista_dados)


@app.route('/usuarios/inserir', methods=['GET', 'POST'])
def inserir_usuario():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome           = request.form.get('nome', '').strip()
        email          = request.form.get('email', '').strip()
        senha          = request.form.get('senha', '').strip()
        confirma_senha = request.form.get('confirma_senha', '').strip()
        funcao_id      = request.form.get('funcao', '').strip()

        if not nome or not email or not senha:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('inserir_usuario'))

        if senha != confirma_senha:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('inserir_usuario'))

        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('inserir_usuario'))

        existente = execute_one('SELECT id_cliente FROM usuario WHERE email = %s', (email,))
        if existente:
            flash('E-mail já cadastrado!', 'danger')
            return redirect(url_for('inserir_usuario'))

        try:
            execute_query(
                'INSERT INTO usuario (nome, email, senha, funcao_id) VALUES (%s, %s, %s, %s)',
                (nome, email, generate_password_hash(senha), funcao_id)
            )
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            flash(f'Erro ao criar usuário: {e}', 'danger')
            return redirect(url_for('inserir_usuario'))

    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('usuarios/inserir_usuario.html', lista_funcoes=lista_funcoes)


@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip()
        senha     = request.form.get('senha', '').strip()
        funcao_id = request.form.get('funcao', '').strip()

        if not nome or not email:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('editar_usuario', id=id))

        existente = execute_one(
            'SELECT id_cliente FROM usuario WHERE email = %s AND id_cliente <> %s',
            (email, id)
        )
        if existente:
            flash('E-mail já cadastrado em outro usuário!', 'danger')
            return redirect(url_for('editar_usuario', id=id))

        try:
            if senha:
                if len(senha) < 8:
                    flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
                    return redirect(url_for('editar_usuario', id=id))
                execute_query(
                    'UPDATE usuario SET nome=%s, email=%s, senha=%s, funcao_id=%s WHERE id_cliente=%s',
                    (nome, email, generate_password_hash(senha), funcao_id, id)
                )
            else:
                execute_query(
                    'UPDATE usuario SET nome=%s, email=%s, funcao_id=%s WHERE id_cliente=%s',
                    (nome, email, funcao_id, id)
                )
            flash('Usuário alterado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            flash(f'Erro ao alterar usuário: {e}', 'danger')
            return redirect(url_for('editar_usuario', id=id))

    usuario = execute_one('SELECT * FROM usuario WHERE id_cliente = %s', (id,))
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('listar_usuarios'))

    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('usuarios/editar_usuario.html', usuario=usuario, lista_funcoes=lista_funcoes)


@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    try:
        execute_query('DELETE FROM usuario WHERE id_cliente = %s', (id,))
        flash('Usuário excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {e}', 'danger')
    return redirect(url_for('listar_usuarios'))


# ── Funções ───────────────────────────────────────────────────────────────────

@app.route('/funcoes/listar')
def listar_funcoes():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    sql = '''
    SELECT
        id_funcao,
        nome,
        status,
        descricao,
        gerenciar_usuarios,
        gerenciar_linguagens,
        gerenciar_recursos,
        gerenciar_funcoes,
        criado_em,
        alterado_em
    FROM funcoes
    ORDER BY id_funcao DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('funcoes/listar_funcoes.html', dados=lista_dados)


@app.route('/funcoes/inserir', methods=['GET', 'POST'])
def inserir_funcao():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        status    = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()
        permissoes = request.form.getlist('permissoes')

        gerenciar_usuarios   = 1 if 'usuarios'   in permissoes else 0
        gerenciar_linguagens = 1 if 'linguagens' in permissoes else 0
        gerenciar_recursos   = 1 if 'recursos'   in permissoes else 0
        gerenciar_funcoes    = 1 if 'funcoes'    in permissoes else 0

        if not nome or not status:
            flash('O campo <b>NOME</b> é obrigatório.', 'danger')
            return redirect(url_for('inserir_funcao'))

        try:
            sql = '''INSERT INTO funcoes (nome, status, descricao,
                        gerenciar_usuarios, gerenciar_linguagens,
                        gerenciar_recursos, gerenciar_funcoes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                '''
            dados = (nome, status, descricao,
                     gerenciar_usuarios, gerenciar_linguagens,
                     gerenciar_recursos, gerenciar_funcoes)

            execute_query(sql, dados)
            flash(f'A função <b>{nome}</b> inserida com sucesso!', 'success')
            return redirect(url_for('listar_funcoes'))

        except Exception as e:
            flash(f'Erro ao salvar: {e}', 'danger')
            return redirect(url_for('inserir_funcao'))

    return render_template('funcoes/inserir_funcao.html')


@app.route('/funcoes/editar/<int:id>', methods=['GET', 'POST'])
def editar_funcao(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        status    = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()
        permissoes = request.form.getlist('permissoes')

        gerenciar_usuarios   = 1 if 'usuarios'   in permissoes else 0
        gerenciar_linguagens = 1 if 'linguagens' in permissoes else 0
        gerenciar_recursos   = 1 if 'recursos'   in permissoes else 0
        gerenciar_funcoes    = 1 if 'funcoes'    in permissoes else 0

        if not nome or not status:
            flash('O campo <b>NOME</b> é obrigatório.', 'danger')
            return redirect(url_for('editar_funcao', id=id))

        try:
            execute_query(
                '''UPDATE funcoes SET nome=%s, status=%s, descricao=%s,
                   gerenciar_usuarios=%s, gerenciar_linguagens=%s,
                   gerenciar_recursos=%s, gerenciar_funcoes=%s
                   WHERE id_funcao=%s''',
                (nome, status, descricao,
                 gerenciar_usuarios, gerenciar_linguagens,
                 gerenciar_recursos, gerenciar_funcoes, id)
            )
            flash(f'A função <b>{nome}</b> alterada com sucesso!', 'success')
            return redirect(url_for('listar_funcoes'))
        except Exception as e:
            flash(f'Erro ao alterar: {e}', 'danger')
            return redirect(url_for('editar_funcao', id=id))

    funcao = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))
    if not funcao:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('listar_funcoes'))

    return render_template('funcoes/editar_funcao.html', funcao=funcao)


@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
def excluir_funcao(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    try:
        em_uso = execute_one('SELECT COUNT(*) as total FROM usuario WHERE funcao_id = %s', (id,))
        if em_uso and em_uso['total'] > 0:
            flash(f'Não é possível excluir: há {em_uso["total"]} usuário(s) com essa função.', 'warning')
            return redirect(url_for('listar_funcoes'))
        execute_query('DELETE FROM funcoes WHERE id_funcao = %s', (id,))
        flash('Função excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir função: {e}', 'danger')
    return redirect(url_for('listar_funcoes'))


# ── Linguagens ────────────────────────────────────────────────────────────────

@app.route('/linguagens/listar')
def listar_linguagens():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    sql = '''
    SELECT id_linguagens, nome, status, nivel, notas,
           criado_em, alterado_em
    FROM linguagens
    ORDER BY id_linguagens DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('linguagens/listar_linguagens.html', linguagens=lista_dados)


@app.route('/linguagens/inserir', methods=['GET', 'POST'])
def inserir_linguagem():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome   = request.form.get('nome', '').strip()
        status = request.form.get('status', '').strip()
        nivel  = request.form.get('nivel', '').strip()
        notas  = request.form.get('nota', '').strip()

        if not nome or not status or not nivel:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('inserir_linguagem'))

        try:
            execute_query(
                'INSERT INTO linguagens (nome, status, nivel, notas) VALUES (%s, %s, %s, %s)',
                (nome, status, nivel, notas)
            )
            flash('Linguagem adicionada com sucesso!', 'success')
            return redirect(url_for('listar_linguagens'))
        except Exception as e:
            flash(f'Erro ao salvar linguagem: {e}', 'danger')
            return redirect(url_for('inserir_linguagem'))

    return render_template('linguagens/inserir_linguagem.html')


@app.route('/linguagens/editar/<int:id>', methods=['GET', 'POST'])
def editar_linguagem(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome   = request.form.get('nome', '').strip()
        status = request.form.get('status', '').strip()
        nivel  = request.form.get('nivel', '').strip()
        notas  = request.form.get('notas', '').strip()

        if not nome or not status or not nivel:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('editar_linguagem', id=id))

        try:
            execute_query(
                'UPDATE linguagens SET nome=%s, status=%s, nivel=%s, notas=%s WHERE id_linguagens=%s',
                (nome, status, nivel, notas, id)
            )
            flash('Linguagem atualizada com sucesso!', 'success')
            return redirect(url_for('listar_linguagens'))
        except Exception as e:
            flash(f'Erro ao alterar linguagem: {e}', 'danger')
            return redirect(url_for('editar_linguagem', id=id))

    linguagem = execute_one('SELECT * FROM linguagens WHERE id_linguagens = %s', (id,))
    if not linguagem:
        flash('Linguagem não encontrada.', 'danger')
        return redirect(url_for('listar_linguagens'))

    return render_template('linguagens/editar_linguagem.html', linguagem=linguagem)


@app.route('/linguagens/excluir/<int:id>', methods=['POST'])
def excluir_linguagem(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    try:
        execute_query('DELETE FROM linguagens WHERE id_linguagens = %s', (id,))
        flash('Linguagem excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir linguagem: {e}', 'danger')
    return redirect(url_for('listar_linguagens'))


# ── Recursos ──────────────────────────────────────────────────────────────────

@app.route('/recursos/listar')
def listar_recursos():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    sql = '''
    SELECT id_recurso, titulo, tipo, url, linguagem, nota,
           criado_em, alterado_em
    FROM recursos
    ORDER BY id_recurso DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('recursos/listar_recursos.html', recursos=lista_dados)


@app.route('/recursos/inserir', methods=['GET', 'POST'])
def inserir_recurso():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo    = request.form.get('titulo', '').strip()
        tipo      = request.form.get('tipo', '').strip()
        url       = request.form.get('url', '').strip()
        linguagem = request.form.get('linguagem', '').strip()
        nota      = request.form.get('nota', '').strip()

        if not titulo or not tipo or not url:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('inserir_recurso'))

        try:
            execute_query(
                'INSERT INTO recursos (titulo, tipo, url, linguagem, nota) VALUES (%s, %s, %s, %s, %s)',
                (titulo, tipo, url, linguagem, nota)
            )
            flash('Recurso adicionado com sucesso!', 'success')
            return redirect(url_for('listar_recursos'))
        except Exception as e:
            flash(f'Erro ao salvar recurso: {e}', 'danger')
            return redirect(url_for('inserir_recurso'))

    linguagens = execute_query('SELECT id_linguagens, nome FROM linguagens ORDER BY nome', fetch=True)
    return render_template('recursos/inserir_recurso.html', linguagens=linguagens)


@app.route('/recursos/editar/<int:id>', methods=['GET', 'POST'])
def editar_recurso(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo    = request.form.get('titulo', '').strip()
        tipo      = request.form.get('tipo', '').strip()
        url       = request.form.get('url', '').strip()
        linguagem = request.form.get('linguagem', '').strip()
        nota      = request.form.get('nota', '').strip()

        if not titulo or not tipo or not url:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('editar_recurso', id=id))

        try:
            execute_query(
                'UPDATE recursos SET titulo=%s, tipo=%s, url=%s, linguagem=%s, nota=%s WHERE id_recurso=%s',
                (titulo, tipo, url, linguagem, nota, id)
            )
            flash('Recurso atualizado com sucesso!', 'success')
            return redirect(url_for('listar_recursos'))
        except Exception as e:
            flash(f'Erro ao alterar recurso: {e}', 'danger')
            return redirect(url_for('editar_recurso', id=id))

    recurso = execute_one('SELECT * FROM recursos WHERE id_recurso = %s', (id,))
    if not recurso:
        flash('Recurso não encontrado.', 'danger')
        return redirect(url_for('listar_recursos'))

    linguagens = execute_query('SELECT id_linguagens, nome FROM linguagens ORDER BY nome', fetch=True)
    return render_template('recursos/editar_recurso.html', recurso=recurso, linguagens=linguagens)


@app.route('/recursos/excluir/<int:id>', methods=['POST'])
def excluir_recurso(id):
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    try:
        execute_query('DELETE FROM recursos WHERE id_recurso = %s', (id,))
        flash('Recurso excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir recurso: {e}', 'danger')
    return redirect(url_for('listar_recursos'))


# ── Equipe ────────────────────────────────────────────────────────────────────

@app.route('/equipe')
def equipe():
    return render_template('sobre_equipe.html')


# Roda a aplicação em modo debug
if __name__ == '__main__':
    app.run(debug=True)
