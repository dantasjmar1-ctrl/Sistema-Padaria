from flask import Flask, redirect, render_template, url_for, request, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'padaria_vitoria_2026'

conexao = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=dbPadaria;'
    'Trusted_Connection=yes;'
)

cursor = conexao.cursor()

print("Conexão realizada com sucesso!")

CATEGORIAS = [
    {
        "slug": "paes-frescos",
        "titulo": "Pães Especiais",
        "imagem": "img/LOGO_SITE/pães-especiais.png",
        "texto": "Pães artesanais feitos na casa, com tradição e muito sabor",
    },
    {
        "slug": "frios-premium",
        "titulo": "Frios Premium",
        "imagem": "img/LOGO_SITE/frios.png",
        "texto": "Frios e defumados de alta qualidade",
    },
    {
        "slug": "tortas-doces",
        "titulo": "Tortas Doces e Sobremesas Especiais",
        "imagem": "img/LOGO_SITE/receitas-de-tortas-doces.jpg",
        "texto": "O toque doce perfeito para qualquer momento do seu dia",
    },
    {
        "slug": "sonhos-recheados",
        "titulo": "Sonhos Recheados",
        "imagem": "img/LOGO_SITE/sonho.png",
        "texto": "Sonhos super recheados, macios e incrivelmente saborosos",
    },
    {
        "slug": "lanches-de-metro",
        "titulo": "Lanches de Metro",
        "imagem": "img/LOGO_SITE/metro2.jpg",
        "texto": "A combinação perfeita de sabor e tamanho para momentos especiais",
    },
    {
        "slug": "sucos-naturais",
        "titulo": "Sucos Naturais e de Polpa",
        "imagem": "img/LOGO_SITE/suco-de-laranja-natural.jpg",
        "texto": "Refrescantes, naturais e preparados na hora",
    },
    {
        "slug": "baguetes-folhadas",
        "titulo": "Baguetes Folhadas",
        "imagem": "img/LOGO_SITE/baguete.png",
        "texto": "Sabor e crocância em cada mordida",
    },
    {
        "slug": "lanches-naturais",
        "titulo": "Lanches Naturais de Pão de Batata",
        "imagem": "img/LOGO_SITE/Sanduiche-de-pao-de-batata.jpg",
        "texto": "A combinação perfeita de leveza, maciez e sabor",
    },
    {
        "slug": "salgados",
        "titulo": "Salgados",
        "imagem": "img/LOGO_SITE/croissant.png",
        "texto": "Salgados variados, assados, fritos e fresquinhos",
    },
    {
        "slug": "bolos-fatias",
        "titulo": "Bolos e Fatias",
        "imagem": "img/LOGO_SITE/bolo.pedaço.png",
        "texto": "Bolos macios, fofinhos e irresistíveis",
    },
    {
        "slug": "bolos-secos",
        "titulo": "Bolos Secos",
        "imagem": "img/LOGO_SITE/bolo.seco.png",
        "texto": "O clássico sabor de bolo caseiro que conquista qualquer um",
    },
    {
        "slug": "paes-doces",
        "titulo": "Pães Doces",
        "imagem": "img/LOGO_SITE/pao-doce.png",
        "texto": "Sabor delicado e textura macia para momentos especiais",
    },
    {
        "slug": "pizzas",
        "titulo": "Pizzas",
        "imagem": "img/LOGO_SITE/padaria_interior.png",
        "texto": "Fatias ou pizza inteira, sempre fresquinha",
    },
    {
        "slug": "broas-artesanais",
        "titulo": "Broas Artesanais",
        "imagem": "img/LOGO_SITE/broa.png",
        "texto": "Fresquinhas e perfeitas para acompanhar um café",
    },
    {
        "slug": "rocamboles",
        "titulo": "Rocamboles",
        "imagem": "img/LOGO_SITE/rocambole.png",
        "texto": "Camadas leves com recheios generosos",
    },
    {
        "slug": "salgados-festa",
        "titulo": "Salgados para Festa",
        "imagem": "img/LOGO_SITE/mini-salgado.png",
        "texto": "Variedade e praticidade para servir seus convidados",
    },
    {
        "slug": "mini-doces",
        "titulo": "Mini Doces",
        "imagem": "img/LOGO_SITE/mini-sonhos-recheados.webp",
        "texto": "Delicadeza e sabor em porções ideais para momentos especiais",
    },
    {
        "slug": "mini-folhados",
        "titulo": "Mini Folhados",
        "imagem": "img/LOGO_SITE/MINI-CROISSANT.jpg",
        "texto": "Pequenas porções cheias de sabor para qualquer ocasião",
    },
    {
        "slug": "tortas-salgadas",
        "titulo": "Tortas Salgadas",
        "imagem": "img/LOGO_SITE/torta-salgada.jpg",
        "texto": "Recheios bem elaborados em massas leves",
    },
    {
        "slug": "calzones",
        "titulo": "Calzones",
        "imagem": "img/LOGO_SITE/calzone.png",
        "texto": "Uma opção completa e saborosa",
    },
    {
        "slug": "paes-queijo",
        "titulo": "Pães de Queijo e Especiais",
        "imagem": "img/LOGO_SITE/Pao-de-queijo.jpg",
        "texto": "Receitas que trazem aconchego e praticidade no dia a dia",
    },
    {
        "slug": "bebidas",
        "titulo": "Bebidas",
        "imagem": "img/LOGO_SITE/bebidas.png",
        "texto": "Bebidas variadas para acompanhar e completar sua escolha",
    },
    {
        "slug": "mercearia",
        "titulo": "Mercearia",
        "imagem": "img/LOGO_SITE/padaria_interior.png",
        "texto": "Itens essenciais para levar junto com seu pedido",
    },
]

@app.route('/')
def inicio():

    return render_template("index.html", categorias=CATEGORIAS)


@app.route('/cardapio')
def cardapio():

    cursor.execute("""
        SELECT c.slug, p.nome, p.imagem, p.preco, p.unidade_venda
        FROM Produto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
    """)

    produtos_por_categoria = {}
    for row in cursor.fetchall():
        preco_formatado = f"{row.preco:.2f}".replace('.', ',')
        produto = {
            "nome": row.nome,
            "imagem": row.imagem if row.imagem else "img/LOGO_SITE/padaria_interior.png",
            "preco": preco_formatado,
            "unidade_venda": row.unidade_venda,
        }
        produtos_por_categoria.setdefault(row.slug, []).append(produto)

    return render_template(
        "cardapio.html",
        categorias=CATEGORIAS,
        produtos_por_categoria=produtos_por_categoria,
    )


@app.route('/categoria/<slug>')
def categoria(slug):

    categoria_encontrada = next(
        (categoria for categoria in CATEGORIAS if categoria["slug"] == slug),
        None,
    )

    if categoria_encontrada is None:
        return redirect(url_for("cardapio"))
    
    cursor.execute("""
        SELECT p.nome, p.imagem, p.preco, p.unidade_venda, p.descricao
        FROM Produto p
        INNER JOIN Categoria c ON c.id_categoria = p.id_categoria
        WHERE c.slug = ?
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
        categorias=CATEGORIAS,
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
    return render_template('pedidos.html')

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


app.run(debug=True)
