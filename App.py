from flask import Flask, redirect, render_template, url_for, request, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'padaria_vitoria_2026'

conexao = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=dbPadaria;'
    'Trusted_Connection=yes;'
    'MARS_Connection=yes;'
)

cursor = conexao.cursor()

print("Conexão realizada com sucesso!")

def verificar_pedidos_expirados():
    cursor.execute("""
        UPDATE Pedido
        SET status_pedido = 'recusado', motivo_recusa = 'Tempo de confirmação expirado (15 minutos)'
        WHERE status_pedido = 'pendente'
        AND DATEDIFF(MINUTE, data_pedido, GETDATE()) > 15
        AND NOT EXISTS (
            SELECT 1 FROM Mensagem WHERE Mensagem.id_pedido = Pedido.id_pedido
        )
    """)
    conexao.commit()

def buscar_categorias():
    cursor.execute("SELECT nome, slug, imagem, texto FROM Categoria ORDER BY nome")
    categorias_raw = cursor.fetchall()
    return [
        {"slug": c.slug, "titulo": c.nome, "imagem": c.imagem, "texto": c.texto}
        for c in categorias_raw
    ]

@app.route('/')
def inicio():

    return render_template("index.html", categorias=buscar_categorias())


@app.route('/cardapio')
def cardapio():

    cursor.execute("""
        SELECT c.slug, p.nome, p.imagem, p.preco, p.unidade_venda, p.descricao
        FROM Produto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
        WHERE p.disponibilidade = 'disponivel'
    """)

    produtos_por_categoria = {}
    for row in cursor.fetchall():
        preco_formatado = f"{row.preco:.2f}".replace('.', ',')
        produto = {
            "nome": row.nome,
            "imagem": row.imagem if row.imagem else "img/LOGO_SITE/padaria_interior.png",
            "preco": preco_formatado,
            "unidade_venda": row.unidade_venda,
            "descricao": row.descricao,
        }
        produtos_por_categoria.setdefault(row.slug, []).append(produto)

    return render_template(
        "cardapio.html",
        categorias=buscar_categorias(),
        produtos_por_categoria=produtos_por_categoria,
    )


@app.route('/categoria/<slug>')
def categoria(slug):

    categorias_lista = buscar_categorias()
    categoria_encontrada = next(
        (categoria for categoria in categorias_lista if categoria["slug"] == slug),
        None,
    )

    if categoria_encontrada is None:
        return redirect(url_for("cardapio"))
    
    cursor.execute("""
        SELECT p.nome, p.imagem, p.preco, p.unidade_venda, p.descricao
        FROM Produto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
        WHERE c.slug = ? AND p.disponibilidade = 'disponivel'
    """, slug)

    produtos_db = []
    for row in cursor.fetchall():
        preco_formatado = f"{row.preco:.2f}".replace('.',',')
        produtos_db.append({
            "nome": row.nome,
            "imagem": row.imagem if row.imagem else "img/LOGO_SITE/padaria_interior.png",
            "preco": preco_formatado,
            "unidade_venda": row.unidade_venda,
            "descricao" : row.descricao,
        })

    return render_template(
        "categoria.html",
        categoria=categoria_encontrada,
        produtos=produtos_db,
        categorias=categorias_lista,
    )
from werkzeug.security import generate_password_hash

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        cpf = request.form['cpf']
        data_nascimento = request.form['data_nascimento']
        senha = request.form['senha']

        senha_hash = generate_password_hash(senha)

        cursor.execute(""" 
                INSERT INTO Cliente (nome, telefone, email, cpf, data_nascimento, senha)
                VALUES (?, ?, ?, ?, ?, ?)
             """, nome, telefone, email, cpf, data_nascimento, senha_hash)
        conexao.commit()

        return redirect(url_for('inicio'))

    return render_template('cadastro.html')

from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():

    erro = None

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor.execute("SELECT id_cliente, nome, senha FROM Cliente WHERE email = ?", email)
        cliente = cursor.fetchone()

        if cliente and check_password_hash(cliente.senha, senha):
            session['cliente_id'] = cliente.id_cliente
            session['cliente_nome'] = cliente.nome
            return redirect(url_for('inicio'))
        else:
            erro = "Email ou senha incorretos."

    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

@app.route('/pedidos')
def pedidos():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    verificar_pedidos_expirados()

    cursor.execute("""
        SELECT id_pedido, tipo_entrega, status_pedido, valor_total, data_pedido
        FROM Pedido
        WHERE id_cliente = ?
        ORDER BY data_pedido DESC
    """, session['cliente_id'])
    lista_pedidos = cursor.fetchall()

    return render_template('pedidos.html', pedidos=lista_pedidos)

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']

        cursor.execute(""" 
            UPDATE Cliente SET nome = ?, telefone = ?, email = ?
            WHERE id_cliente = ?
         """, nome, telefone, email, session['cliente_id'])
        conexao.commit()

        session['cliente_nome'] = nome
        return redirect(url_for('perfil'))
    
    cursor.execute("SELECT nome, telefone, email, cpf, data_nascimento FROM Cliente WHERE id_cliente = ?", session['cliente_id'])
    cliente = cursor.fetchone()

    return render_template('perfil.html', cliente=cliente)

@app.route('/finalizar-pedido')
def finalizar_pedido():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    cursor.execute("SELECT id_endereco, rua, numero, bairro FROM Endereco WHERE id_cliente = ?", session['cliente_id'])
    enderecos = cursor.fetchall()

    return render_template('finalizar_pedido.html', enderecos=enderecos)

import json
import re

@app.route('/confirmar-pedido', methods=['POST'])
def confirmar_pedido():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))

    itens_json = request.form['itens_json']
    tipo_entrega = request.form['tipo_entrega']
    id_endereco = request.form.get('id_endereco')
    forma_pagamento = request.form['forma_pagamento']

    itens = json.loads(itens_json)

    valor_produto = sum(item[1]['price'] * item[1]['quantity'] for item in itens)
    taxa_entrega = 5.00 if tipo_entrega == 'entrega' else 0.00
    valor_total = valor_produto + taxa_entrega

    id_endereco_final = id_endereco if tipo_entrega == 'entrega' else None

    cursor.execute("""
        INSERT INTO Pedido (id_cliente, id_endereco, tipo_entrega, status_pedido, valor_produto, taxa_entrega, valor_total, data_pedido)
        VALUES (?, ?, ?, 'pendente', ?, ?, ?, GETDATE())
    """, session['cliente_id'], id_endereco_final, tipo_entrega, valor_produto, taxa_entrega, valor_total)
    conexao.commit()

    cursor.execute("SELECT @@IDENTITY AS id")
    id_pedido = cursor.fetchone().id

    for nome_carrinho, item in itens:
        nome_produto = re.sub(r' - \d+g$', '', item['name'])

        cursor.execute("SELECT id_produto FROM Produto WHERE nome = ?", nome_produto)
        produto = cursor.fetchone()

        if produto:
            subtotal = item['price'] * item['quantity']
            cursor.execute("""
                INSERT INTO ItemPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, id_pedido, produto.id_produto, item['quantity'], item['price'], subtotal)

    cursor.execute("""
        INSERT INTO Pagamento (id_pedido, forma_pagamento, status_pagamento)
        VALUES (?, ?, 'pendente')
    """, id_pedido, forma_pagamento)
    conexao.commit()

    return redirect(url_for('pedido_confirmado', id_pedido=id_pedido))

@app.route('/pedido-confirmado/<int:id_pedido>')
def pedido_confirmado(id_pedido):
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    verificar_pedidos_expirados()

    cursor.execute("""
        SELECT p.id_pedido, p.tipo_entrega, p.status_pedido, p.valor_produto,
               p.taxa_entrega, p.valor_total, p.data_pedido,
               e.rua, e.numero, e.bairro,
               pg.forma_pagamento
        FROM Pedido p
        LEFT JOIN Endereco e ON e.id_endereco = p.id_endereco
        LEFT JOIN Pagamento pg ON pg.id_pedido = p.id_pedido
        WHERE p.id_pedido = ? AND p.id_cliente = ?
    """, id_pedido, session['cliente_id'])
    pedido = cursor.fetchone()

    if not pedido:
        return redirect(url_for('pedidos'))

    cursor.execute("""
        SELECT pr.nome, ip.quantidade, ip.preco_unitario, ip.subtotal
        FROM ItemPedido ip
        INNER JOIN Produto pr ON pr.id_produto = ip.id_produto
        WHERE ip.id_pedido = ?
    """, id_pedido)
    itens = cursor.fetchall()

    info_recusa = None
    outros_produtos = []
    if pedido.status_pedido == 'recusado':
        cursor.execute("""
            SELECT p.motivo_recusa, 
                   pf.nome AS produto_faltante_nome,
                   ps.id_produto AS substituto_id, ps.nome AS substituto_nome, ps.preco AS substituto_preco,
                   ip.id_produto AS produto_faltante_id
            FROM Pedido p
            LEFT JOIN ItemPedido ip ON ip.id_item = p.id_item_pedido_faltante
            LEFT JOIN Produto pf ON pf.id_produto = ip.id_produto
            LEFT JOIN Produto ps ON ps.id_produto = p.id_produto_substituto
            WHERE p.id_pedido = ?
        """, id_pedido)
        info_recusa = cursor.fetchone()

        if info_recusa and info_recusa.produto_faltante_id:
            cursor.execute("""
                SELECT id_produto, nome, preco 
                FROM Produto 
                WHERE id_categoria = (SELECT id_categoria FROM Produto WHERE id_produto = ?)
                AND id_produto != ?
                ORDER BY nome
            """, info_recusa.produto_faltante_id, info_recusa.produto_faltante_id)
            outros_produtos = cursor.fetchall()

    tempo_estimado = "40 a 50 minutos" if pedido.tipo_entrega == 'entrega' else "20 a 30 minutos"

    mensagens_status = {
        'pendente': 'Aguardando confirmação da padaria',
        'em_preparo': 'Seu pedido está sendo preparado',
        'pronto': 'Pedido pronto!',
        'saiu_para_entrega': 'Seu pedido saiu para entrega',
        'aguardando_retirada': 'Pedido pronto para retirada',
        'entregue': 'Pedido entregue',
        'retirado': 'Pedido retirado',
        'recusado': 'Pedido recusado',
    }
    status_texto = mensagens_status.get(pedido.status_pedido, pedido.status_pedido)

    cursor.execute("SELECT id_produto, nome, preco FROM Produto ORDER BY nome")
    todos_produtos_geral = cursor.fetchall()

    return render_template(
        'pedido_confirmado.html',
        pedido=pedido,
        itens=itens,
        tempo_estimado=tempo_estimado,
        status_texto=status_texto,
        info_recusa=info_recusa,
        outros_produtos=outros_produtos,
        todos_produtos_geral=todos_produtos_geral,
    )

@app.route('/novo-endereco', methods=['GET', 'POST'])
def novo_endereco():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        cep = request.form['cep']
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        complemento = request.form.get('complemento', '')
        referencia = request.form.get('referenceia', '')

        cursor.execute("""
            INSERT INTO Endereco (id_cliente, cep, rua, numero, bairro, cidade, estado, complemento, referencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, session['cliente_id'], cep, rua, numero, bairro, cidade, estado, complemento, referencia)
        conexao.commit()
        
        return redirect(url_for('finalizar_pedido'))
    
    return render_template ('novo_endereco.html')

@app.route('/painel/login', methods=['GET', 'POST'])
def login_funcionario():
    erro = None

    if request.method == 'POST':
        email = request.form['email_func']
        senha = request.form['senha_func']

        cursor.execute("SELECT id_funcionario, nome, senha, cargo FROM Funcionario WHERE email = ?", email)
        funcionario = cursor.fetchone()

        if funcionario and check_password_hash(funcionario.senha, senha):
            session['funcionario_id'] = funcionario.id_funcionario
            session['funcionario_nome'] = funcionario.nome
            session['funcionario_cargo'] = funcionario.cargo
            return redirect(url_for('painel'))
        else:
            erro = "Email ou senha incorretos."

    return render_template('login_funcionario.html', erro=erro)


@app.route('/painel')
def painel():
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    verificar_pedidos_expirados()

    cursor.execute("""
        SELECT p.id_pedido, p.tipo_entrega, p.status_pedido, p.valor_total, p.data_pedido,
               c.nome AS cliente_nome, c.telefone AS cliente_telefone,
               e.rua, e.numero, e.bairro
        FROM Pedido p
        INNER JOIN Cliente c ON c.id_cliente = p.id_cliente
        LEFT JOIN Endereco e ON e.id_endereco = p.id_endereco
        ORDER BY p.data_pedido DESC
    """)
    pedidos_raw = cursor.fetchall()

    cursor.execute("SELECT id_produto, nome, id_categoria FROM Produto ORDER BY nome")
    todos_produtos = cursor.fetchall()

    proximo_status = {
        'em_preparo': ('pronto', 'Marcar como Pronto'),
    }

    pedidos = []
    for p in pedidos_raw:
        cursor.execute("""
            SELECT ip.id_item, pr.nome, ip.quantidade, pr.id_categoria, pr.id_produto
            FROM ItemPedido ip
            INNER JOIN Produto pr ON pr.id_produto = ip.id_produto
            WHERE ip.id_pedido = ?
        """, p.id_pedido)
        itens = cursor.fetchall()

        if p.status_pedido == 'pronto':
            if p.tipo_entrega == 'entrega':
                prox_valor, prox_label = 'saiu_para_entrega', 'Saiu para Entrega'
            else:
                prox_valor, prox_label = 'aguardando_retirada', 'Aguardando Retirada'
        elif p.status_pedido == 'saiu_para_entrega':
            prox_valor, prox_label = 'entregue', 'Marcar como Entregue'
        elif p.status_pedido == 'aguardando_retirada':
            prox_valor, prox_label = 'retirado', 'Marcar como Retirado'
        elif p.status_pedido in proximo_status:
            prox_valor, prox_label = proximo_status[p.status_pedido]
        else:
            prox_valor, prox_label = None, None

        pedidos.append({
            'id_pedido': p.id_pedido,
            'tipo_entrega': p.tipo_entrega,
            'status_pedido': p.status_pedido,
            'valor_total': p.valor_total,
            'data_pedido': p.data_pedido,
            'cliente_nome': p.cliente_nome,
            'cliente_telefone': p.cliente_telefone,
            'endereco': f"{p.rua}, {p.numero} - {p.bairro}" if p.rua else None,
            'itens': itens,
            'proximo_valor': prox_valor,
            'proximo_label': prox_label,
        })

    pendentes = [p for p in pedidos if p['status_pedido'] == 'pendente']
    em_andamento = [p for p in pedidos if p['status_pedido'] in ('confirmado', 'em_preparo', 'pronto', 'saiu_para_entrega', 'aguardando_retirada')]
    concluidos = [p for p in pedidos if p['status_pedido'] in ('entregue', 'retirado')]
    recusados = [p for p in pedidos if p['status_pedido'] == 'recusado']

    return render_template('painel.html', pendentes=pendentes, em_andamento=em_andamento, concluidos=concluidos, recusados=recusados, todos_produtos=todos_produtos)    


@app.route('/painel/pedido/<int:id_pedido>/avancar', methods=['POST'])
def avancar_status(id_pedido):
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    novo_status = request.form['novo_status']

    cursor.execute("""
        UPDATE Pedido SET status_pedido = ?, id_funcionario = ?
        WHERE id_pedido = ?
    """, novo_status, session['funcionario_id'], id_pedido)
    conexao.commit()

    return redirect(url_for('painel'))


@app.route('/painel/pedido/<int:id_pedido>/recusar', methods=['POST'])
def recusar_pedido(id_pedido):
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    motivo = request.form['motivo']
    item_faltante = request.form.get('item_faltante') or None
    produto_substituto = request.form.get('produto_substituto') or None

    cursor.execute("""
        UPDATE Pedido 
        SET status_pedido = 'recusado', motivo_recusa = ?, id_funcionario = ?, 
            id_item_pedido_faltante = ?, id_produto_substituto = ?
        WHERE id_pedido = ?
    """, motivo, session['funcionario_id'], item_faltante, produto_substituto, id_pedido)
    conexao.commit()

    return redirect(url_for('painel'))

@app.route('/pedido-status/<int:id_pedido>')
def pedido_status(id_pedido):
    if 'cliente_id' not in session:
        return {'erro': 'não autorizado'}, 401

    cursor.execute("SELECT status_pedido FROM Pedido WHERE id_pedido = ? AND id_cliente = ?", id_pedido, session['cliente_id'])
    pedido = cursor.fetchone()

    if not pedido:
        return {'erro': 'não encontrado'}, 404

    return {'status': pedido.status_pedido}

@app.route('/pedido/<int:id_pedido>/aceitar-substituto', methods=['POST'])
def aceitar_substituto(id_pedido):
    if 'cliente_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("""
        SELECT id_cliente, id_endereco, tipo_entrega, id_item_pedido_faltante, id_produto_substituto
        FROM Pedido WHERE id_pedido = ? AND id_cliente = ?
    """, id_pedido, session['cliente_id'])
    pedido_original = cursor.fetchone()

    if not pedido_original or not pedido_original.id_produto_substituto:
        return redirect(url_for('pedido_confirmado', id_pedido=id_pedido))

    cursor.execute("""
        SELECT ip.id_item, ip.id_produto, ip.quantidade, ip.preco_unitario
        FROM ItemPedido ip
        WHERE ip.id_pedido = ?
    """, id_pedido)
    itens_originais = cursor.fetchall()

    cursor.execute("SELECT id_produto, preco FROM Produto WHERE id_produto = ?", pedido_original.id_produto_substituto)
    produto_substituto = cursor.fetchone()

    itens_finais = []
    for item in itens_originais:
        if item.id_item == pedido_original.id_item_pedido_faltante:
            itens_finais.append({
                'id_produto': produto_substituto.id_produto,
                'quantidade': 1,
                'preco_unitario': float(produto_substituto.preco),
            })
        else:
            itens_finais.append({
                'id_produto': item.id_produto,
                'quantidade': item.quantidade,
                'preco_unitario': float(item.preco_unitario),
            })

    valor_produto = sum(i['preco_unitario'] * i['quantidade'] for i in itens_finais)
    quantidade_produtos = len(itens_finais)
    desconto = 5.00 if (valor_produto >= 18.90 and quantidade_produtos <= 2) else 0.00

    taxa_entrega = 5.00 if pedido_original.tipo_entrega == 'entrega' else 0.00
    valor_total = valor_produto + taxa_entrega - desconto

    cursor.execute("""
        INSERT INTO Pedido (id_cliente, id_endereco, tipo_entrega, status_pedido, valor_produto, taxa_entrega, desconto_aplicado, valor_total, data_pedido)
        VALUES (?, ?, ?, 'pendente', ?, ?, ?, ?, GETDATE())
    """, session['cliente_id'], pedido_original.id_endereco, pedido_original.tipo_entrega, valor_produto, taxa_entrega, desconto, valor_total)
    conexao.commit()

    cursor.execute("SELECT @@IDENTITY AS id")
    novo_id_pedido = cursor.fetchone().id

    for item in itens_finais:
        subtotal = item['preco_unitario'] * item['quantidade']
        cursor.execute("""
            INSERT INTO ItemPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, novo_id_pedido, item['id_produto'], item['quantidade'], item['preco_unitario'], subtotal)

    cursor.execute("SELECT forma_pagamento FROM Pagamento WHERE id_pedido = ?", id_pedido)
    pagamento_original = cursor.fetchone()
    cursor.execute("""
        INSERT INTO Pagamento (id_pedido, forma_pagamento, status_pagamento)
        VALUES (?, ?, 'pendente')
    """, novo_id_pedido, pagamento_original.forma_pagamento if pagamento_original else 'dinheiro')
    conexao.commit()

    return redirect(url_for('pedido_confirmado', id_pedido=novo_id_pedido))


@app.route('/pedido/<int:id_pedido>/escolher-outro', methods=['POST'])
def escolher_outro_produto(id_pedido):
    if 'cliente_id' not in session:
        return redirect(url_for('login'))

    produto_escolhido_id = request.form['produto_escolhido']

    cursor.execute("""
        SELECT id_cliente, id_endereco, tipo_entrega, id_item_pedido_faltante
        FROM Pedido WHERE id_pedido = ? AND id_cliente = ?
    """, id_pedido, session['cliente_id'])
    pedido_original = cursor.fetchone()

    if not pedido_original:
        return redirect(url_for('pedido_confirmado', id_pedido=id_pedido))

    cursor.execute("""
        SELECT ip.id_item, ip.id_produto, ip.quantidade, ip.preco_unitario
        FROM ItemPedido ip
        WHERE ip.id_pedido = ?
    """, id_pedido)
    itens_originais = cursor.fetchall()

    cursor.execute("SELECT id_produto, preco FROM Produto WHERE id_produto = ?", produto_escolhido_id)
    produto_escolhido = cursor.fetchone()

    itens_finais = []
    for item in itens_originais:
        if item.id_item == pedido_original.id_item_pedido_faltante:
            itens_finais.append({
                'id_produto': produto_escolhido.id_produto,
                'quantidade': 1,
                'preco_unitario': float(produto_escolhido.preco),
            })
        else:
            itens_finais.append({
                'id_produto': item.id_produto,
                'quantidade': item.quantidade,
                'preco_unitario': float(item.preco_unitario),
            })

    valor_produto = sum(i['preco_unitario'] * i['quantidade'] for i in itens_finais)
    quantidade_produtos = len(itens_finais)
    desconto = 5.00 if (valor_produto >= 18.90 and quantidade_produtos <= 2) else 0.00

    taxa_entrega = 5.00 if pedido_original.tipo_entrega == 'entrega' else 0.00
    valor_total = valor_produto + taxa_entrega - desconto

    cursor.execute("""
        INSERT INTO Pedido (id_cliente, id_endereco, tipo_entrega, status_pedido, valor_produto, taxa_entrega, desconto_aplicado, valor_total, data_pedido)
        VALUES (?, ?, ?, 'pendente', ?, ?, ?, ?, GETDATE())
    """, session['cliente_id'], pedido_original.id_endereco, pedido_original.tipo_entrega, valor_produto, taxa_entrega, desconto, valor_total)
    conexao.commit()

    cursor.execute("SELECT @@IDENTITY AS id")
    novo_id_pedido = cursor.fetchone().id

    for item in itens_finais:
        subtotal = item['preco_unitario'] * item['quantidade']
        cursor.execute("""
            INSERT INTO ItemPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, novo_id_pedido, item['id_produto'], item['quantidade'], item['preco_unitario'], subtotal)

    cursor.execute("SELECT forma_pagamento FROM Pagamento WHERE id_pedido = ?", id_pedido)
    pagamento_original = cursor.fetchone()
    cursor.execute("""
        INSERT INTO Pagamento (id_pedido, forma_pagamento, status_pagamento)
        VALUES (?, ?, 'pendente')
    """, novo_id_pedido, pagamento_original.forma_pagamento if pagamento_original else 'dinheiro')
    conexao.commit()

    return redirect(url_for('pedido_confirmado', id_pedido=novo_id_pedido))


@app.route('/pedido/<int:id_pedido>/continuar-sem-item', methods=['POST'])
def continuar_sem_item(id_pedido):
    if 'cliente_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("""
        SELECT id_cliente, id_endereco, tipo_entrega, id_item_pedido_faltante
        FROM Pedido WHERE id_pedido = ? AND id_cliente = ?
    """, id_pedido, session['cliente_id'])
    pedido_original = cursor.fetchone()

    if not pedido_original:
        return redirect(url_for('pedido_confirmado', id_pedido=id_pedido))

    cursor.execute("""
        SELECT ip.id_item, ip.id_produto, ip.quantidade, ip.preco_unitario
        FROM ItemPedido ip
        WHERE ip.id_pedido = ?
    """, id_pedido)
    itens_originais = cursor.fetchall()

    itens_finais = [
        {'id_produto': item.id_produto, 'quantidade': item.quantidade, 'preco_unitario': float(item.preco_unitario)}
        for item in itens_originais
        if item.id_item != pedido_original.id_item_pedido_faltante
    ]

    if not itens_finais:
        return redirect(url_for('pedido_confirmado', id_pedido=id_pedido))

    valor_produto = sum(i['preco_unitario'] * i['quantidade'] for i in itens_finais)
    taxa_entrega = 5.00 if pedido_original.tipo_entrega == 'entrega' else 0.00
    valor_total = valor_produto + taxa_entrega

    cursor.execute("""
        INSERT INTO Pedido (id_cliente, id_endereco, tipo_entrega, status_pedido, valor_produto, taxa_entrega, desconto_aplicado, valor_total, data_pedido)
        VALUES (?, ?, ?, 'pendente', ?, ?, 0, ?, GETDATE())
    """, session['cliente_id'], pedido_original.id_endereco, pedido_original.tipo_entrega, valor_produto, taxa_entrega, valor_total)
    conexao.commit()

    cursor.execute("SELECT @@IDENTITY AS id")
    novo_id_pedido = cursor.fetchone().id

    for item in itens_finais:
        subtotal = item['preco_unitario'] * item['quantidade']
        cursor.execute("""
            INSERT INTO ItemPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, novo_id_pedido, item['id_produto'], item['quantidade'], item['preco_unitario'], subtotal)

    cursor.execute("SELECT forma_pagamento FROM Pagamento WHERE id_pedido = ?", id_pedido)
    pagamento_original = cursor.fetchone()
    cursor.execute("""
        INSERT INTO Pagamento (id_pedido, forma_pagamento, status_pagamento)
        VALUES (?, ?, 'pendente')
    """, novo_id_pedido, pagamento_original.forma_pagamento if pagamento_original else 'dinheiro')
    conexao.commit()

    return redirect(url_for('pedido_confirmado', id_pedido=novo_id_pedido))

@app.route('/painel/produtos')
def painel_produtos():
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    cursor.execute("""
        SELECT p.id_produto, p.nome, p.preco, p.imagem, p.disponibilidade, c.nome AS categoria_nome
        FROM Produto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
        ORDER BY c.nome, p.nome
    """)
    produtos_raw = cursor.fetchall()

    produtos_por_categoria = {}
    for produto in produtos_raw:
        produtos_por_categoria.setdefault(produto.categoria_nome, []).append(produto)

    return render_template('painel_produtos.html', produtos_por_categoria=produtos_por_categoria, total=len(produtos_raw))

import os
from werkzeug.utils import secure_filename

@app.route('/painel/produtos/<int:id_produto>/editar', methods=['GET', 'POST'])
def editar_produto(id_produto):
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco'].replace(',', '.')
        descricao = request.form.get('descricao', '')

        arquivo = request.files.get('nova_foto')
        if arquivo and arquivo.filename != '':
            nome_seguro = secure_filename(arquivo.filename)
            caminho_pasta = os.path.join('static', 'img', 'produtos')
            os.makedirs(caminho_pasta, exist_ok=True)
            caminho_completo = os.path.join(caminho_pasta, f"{id_produto}_{nome_seguro}")
            arquivo.save(caminho_completo)

            caminho_banco = f"img/produtos/{id_produto}_{nome_seguro}"

            cursor.execute("""
                UPDATE Produto SET nome = ?, preco = ?, descricao = ?, imagem = ?
                WHERE id_produto = ?
            """, nome, preco, descricao, caminho_banco, id_produto)
        else:
            cursor.execute("""
                UPDATE Produto SET nome = ?, preco = ?, descricao = ?
                WHERE id_produto = ?
            """, nome, preco, descricao, id_produto)

        conexao.commit()
        return redirect(url_for('painel_produtos'))

    cursor.execute("SELECT id_produto, nome, preco, descricao, imagem FROM Produto WHERE id_produto = ?", id_produto)
    produto = cursor.fetchone()

    return render_template('editar_produto.html', produto=produto)

@app.route('/painel/produtos/<int:id_produto>/disponibilidade', methods=['POST'])
def alternar_disponibilidade(id_produto):
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    cursor.execute("SELECT disponibilidade FROM Produto WHERE id_produto = ?", id_produto)
    produto = cursor.fetchone()

    novo_status = 'esgotado' if produto.disponibilidade == 'disponivel' else 'disponivel'

    cursor.execute("UPDATE Produto SET disponibilidade = ? WHERE id_produto = ?", novo_status, id_produto)
    conexao.commit()

    return redirect(url_for('painel_produtos'))

@app.route('/painel/produtos/novo', methods=['GET', 'POST'])
def novo_produto():
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco'].replace(',', '.')
        descricao = request.form.get('descricao', '')
        id_categoria = request.form['id_categoria']
        unidade_venda = request.form.get('unidade_venda', 'unidade')

        cursor.execute("""
            INSERT INTO Produto (id_categoria, nome, preco, descricao, unidade_venda, disponibilidade)
            VALUES (?, ?, ?, ?, ?, 'disponivel')
        """, id_categoria, nome, preco, descricao, unidade_venda)
        conexao.commit()

        cursor.execute("SELECT @@IDENTITY AS id")
        novo_id = cursor.fetchone().id

        arquivo = request.files.get('nova_foto')
        if arquivo and arquivo.filename != '':
            nome_seguro = secure_filename(arquivo.filename)
            caminho_pasta = os.path.join('static', 'img', 'produtos')
            os.makedirs(caminho_pasta, exist_ok=True)
            caminho_completo = os.path.join(caminho_pasta, f"{novo_id}_{nome_seguro}")
            arquivo.save(caminho_completo)

            caminho_banco = f"img/produtos/{novo_id}_{nome_seguro}"
            cursor.execute("UPDATE Produto SET imagem = ? WHERE id_produto = ?", caminho_banco, novo_id)
            conexao.commit()

        return redirect(url_for('painel_produtos'))

    cursor.execute("SELECT id_categoria, nome FROM Categoria ORDER BY nome")
    categorias = cursor.fetchall()

    return render_template('novo_produto.html', categorias=categorias)

@app.route('/painel/categorias/nova', methods=['GET', 'POST'])
def nova_categoria():
    if 'funcionario_id' not in session:
        return redirect(url_for('login_funcionario'))

    if request.method == 'POST':
        nome = request.form['nome']
        slug = request.form['slug']

        cursor.execute("INSERT INTO Categoria (nome, slug) VALUES (?, ?)", nome, slug)
        conexao.commit()

        return redirect(url_for('novo_produto'))

    return render_template('nova_categoria.html')

@app.route('/painel/verificar-novos')
def verificar_novos_pedidos():
    if 'funcionario_id' not in session:
        return {'erro': 'não autorizado'}, 401

    cursor_local = conexao.cursor()
    cursor_local.execute("SELECT COUNT(*) AS total FROM Pedido WHERE status_pedido = 'pendente'")
    resultado = cursor_local.fetchone()

    return {'total_pendentes': resultado.total}

app.run(debug=True)
