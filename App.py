from flask import Flask, redirect, render_template, url_for
import pyodbc

app = Flask(__name__)

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
        "titulo": "Pães Frescos",
        "imagem": "img/LOGO_SITE/pães.jpg",
        "texto": "Produzidos diariamente com ingredientes selecionados",
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
        "slug": "paes-especiais",
        "titulo": "Pães Especiais",
        "imagem": "img/LOGO_SITE/pães-especiais.png",
        "texto": "Pães artesanais feitos na casa, com tradição e muito sabor",
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
        "slug": "mini-croissant",
        "titulo": "Mini Croissant",
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

PRODUTOS_POR_CATEGORIA = {
    "paes-frescos": [
        {"nome": "Pão francês", "imagem": "img/LOGO_SITE/pães.jpg", "preco": "0,90"},
        {"nome": "Pão de leite", "imagem": "img/LOGO_SITE/pães.jpg", "preco": "1,20"},
        {"nome": "Pão integral", "imagem": "img/LOGO_SITE/pães.jpg", "preco": "1,50"},
    ],
    "frios-premium": [
        {"nome": "Presunto fatiado", "imagem": "img/LOGO_SITE/frios.png", "preco": "8,90"},
        {"nome": "Queijo mussarela", "imagem": "img/LOGO_SITE/frios.png", "preco": "9,90"},
        {"nome": "Peito de peru", "imagem": "img/LOGO_SITE/frios.png", "preco": "12,90"},
    ],
    "tortas-doces": [
        {"nome": "Torta de morango", "imagem": "img/LOGO_SITE/receitas-de-tortas-doces.jpg", "preco": "42,90"},
        {"nome": "Torta de chocolate", "imagem": "img/LOGO_SITE/receitas-de-tortas-doces.jpg", "preco": "45,90"},
        {"nome": "Sobremesa especial", "imagem": "img/LOGO_SITE/receitas-de-tortas-doces.jpg", "preco": "12,90"},
    ],
    "sonhos-recheados": [
        {"nome": "Sonho de creme", "imagem": "img/LOGO_SITE/sonho.png", "preco": "6,00"},
        {"nome": "Sonho de doce de leite", "imagem": "img/LOGO_SITE/sonho.png", "preco": "6,50"},
        {"nome": "Sonho de chocolate", "imagem": "img/LOGO_SITE/sonho.png", "preco": "6,50"},
    ],
    "lanches-de-metro": [
        {"nome": "Lanche de metro tradicional", "imagem": "img/LOGO_SITE/metro2.jpg", "preco": "89,90"},
        {"nome": "Lanche de metro especial", "imagem": "img/LOGO_SITE/Lanche de metro (2).png", "preco": "99,90"},
        {"nome": "Lanche de metro premium", "imagem": "img/LOGO_SITE/Lanche de metro 3.png", "preco": "109,90"},
    ],
    "sucos-naturais": [
        {"nome": "Suco de laranja", "imagem": "img/LOGO_SITE/suco-de-laranja-natural.jpg", "preco": "8,00"},
        {"nome": "Suco de polpa", "imagem": "img/LOGO_SITE/suco-de-laranja-natural.jpg", "preco": "7,00"},
        {"nome": "Suco natural misto", "imagem": "img/LOGO_SITE/suco-de-laranja-natural.jpg", "preco": "9,00"},
    ],
    "baguetes-folhadas": [
        {"nome": "Baguete folhada", "imagem": "img/LOGO_SITE/baguete.png", "preco": "12,90"},
        {"nome": "Baguete de queijo", "imagem": "img/LOGO_SITE/baguete.png", "preco": "13,90"},
        {"nome": "Baguete recheada", "imagem": "img/LOGO_SITE/baguete.png", "preco": "15,90"},
    ],
    "lanches-naturais": [
        {"nome": "Lanche natural de frango", "imagem": "img/LOGO_SITE/Sanduiche-de-pao-de-batata.jpg", "preco": "13,90"},
        {"nome": "Lanche natural de peito de peru", "imagem": "img/LOGO_SITE/Sanduiche-de-pao-de-batata.jpg", "preco": "14,90"},
        {"nome": "Lanche natural vegetariano", "imagem": "img/LOGO_SITE/Sanduiche-de-pao-de-batata.jpg", "preco": "12,90"},
    ],
    "salgados": [
        {"nome": "Coxinha", "imagem": "img/LOGO_SITE/croissant.png", "preco": "6,50"},
        {"nome": "Esfiha", "imagem": "img/LOGO_SITE/mini-salgado.png", "preco": "5,90"},
        {"nome": "Folhado", "imagem": "img/LOGO_SITE/croissant.png", "preco": "7,90"},
    ],
    "bolos-fatias": [
        {"nome": "Fatia de bolo", "imagem": "img/LOGO_SITE/bolo.pedaço.png", "preco": "8,50"},
        {"nome": "Bolo recheado", "imagem": "img/LOGO_SITE/bolo.pedaço.png", "preco": "54,90"},
        {"nome": "Bolo de chocolate", "imagem": "img/LOGO_SITE/bolo.pedaço.png", "preco": "49,90"},
    ],
    "bolos-secos": [
        {"nome": "Bolo de fubá", "imagem": "img/LOGO_SITE/bolo.seco.png", "preco": "18,90"},
        {"nome": "Bolo de laranja", "imagem": "img/LOGO_SITE/bolo.seco.png", "preco": "19,90"},
        {"nome": "Bolo de cenoura", "imagem": "img/LOGO_SITE/bolo.seco.png", "preco": "22,90"},
    ],
    "paes-doces": [
        {"nome": "Pão doce de creme", "imagem": "img/LOGO_SITE/pao-doce.png", "preco": "5,90"},
        {"nome": "Rosquinha doce", "imagem": "img/LOGO_SITE/pao-doce.png", "preco": "4,90"},
        {"nome": "Pão doce com coco", "imagem": "img/LOGO_SITE/pao-doce.png", "preco": "6,90"},
    ],
    "paes-especiais": [
        {"nome": "Pão especial", "imagem": "img/LOGO_SITE/pães-especiais.png", "preco": "9,90"},
        {"nome": "Pão artesanal", "imagem": "img/LOGO_SITE/pães-especiais.png", "preco": "12,90"},
        {"nome": "Pão português", "imagem": "img/LOGO_SITE/pães-especiais.png", "preco": "10,90"},
    ],
    "broas-artesanais": [
        {"nome": "Broa simples", "imagem": "img/LOGO_SITE/broa.png", "preco": "4,90"},
        {"nome": "Broa de fubá", "imagem": "img/LOGO_SITE/broa.png", "preco": "5,50"},
        {"nome": "Broa recheada", "imagem": "img/LOGO_SITE/broa.png", "preco": "6,50"},
    ],
    "rocamboles": [
        {"nome": "Rocambole de goiabada", "imagem": "img/LOGO_SITE/rocambole.png", "preco": "24,90"},
        {"nome": "Rocambole de chocolate", "imagem": "img/LOGO_SITE/rocambole.png", "preco": "28,90"},
        {"nome": "Rocambole de doce de leite", "imagem": "img/LOGO_SITE/rocambole.png", "preco": "29,90"},
    ],
    "salgados-festa": [
        {"nome": "Mini coxinha", "imagem": "img/LOGO_SITE/mini-salgado.png", "preco": "59,90"},
        {"nome": "Mini esfiha", "imagem": "img/LOGO_SITE/mini-salgado.png", "preco": "59,90"},
        {"nome": "Mix de salgados", "imagem": "img/LOGO_SITE/mini-salgado.png", "preco": "69,90"},
    ],
    "mini-doces": [
        {"nome": "Mini sonho", "imagem": "img/LOGO_SITE/mini-sonhos-recheados.webp", "preco": "45,90"},
        {"nome": "Mini doce recheado", "imagem": "img/LOGO_SITE/mini-sonhos-recheados.webp", "preco": "49,90"},
        {"nome": "Kit mini doces", "imagem": "img/LOGO_SITE/mini-sonhos-recheados.webp", "preco": "59,90"},
    ],
    "mini-croissant": [
        {"nome": "Mini croissant simples", "imagem": "img/LOGO_SITE/MINI-CROISSANT.jpg", "preco": "4,50"},
        {"nome": "Mini croissant de queijo", "imagem": "img/LOGO_SITE/MINI-CROISSANT.jpg", "preco": "5,50"},
        {"nome": "Mini croissant recheado", "imagem": "img/LOGO_SITE/MINI-CROISSANT.jpg", "preco": "6,50"},
    ],
    "tortas-salgadas": [
        {"nome": "Torta de frango", "imagem": "img/LOGO_SITE/torta-salgada.jpg", "preco": "39,90"},
        {"nome": "Torta de palmito", "imagem": "img/LOGO_SITE/torta-salgada.jpg", "preco": "42,90"},
        {"nome": "Torta salgada especial", "imagem": "img/LOGO_SITE/torta-salgada.jpg", "preco": "45,90"},
    ],
    "calzones": [
        {"nome": "Calzone de calabresa", "imagem": "img/LOGO_SITE/calzone.png", "preco": "13,90"},
        {"nome": "Calzone de frango", "imagem": "img/LOGO_SITE/calzone.png", "preco": "13,90"},
        {"nome": "Calzone de queijo", "imagem": "img/LOGO_SITE/calzone.png", "preco": "12,90"},
    ],
    "paes-queijo": [
        {"nome": "Pão de queijo", "imagem": "img/LOGO_SITE/Pao-de-queijo.jpg", "preco": "6,50"},
        {"nome": "Pão de queijo grande", "imagem": "img/LOGO_SITE/Pao-de-queijo.jpg", "preco": "9,90"},
        {"nome": "Chipa", "imagem": "img/LOGO_SITE/Pao-de-queijo.jpg", "preco": "5,90"},
    ],
    "bebidas": [
        {"nome": "Coca-Cola 2L", "imagem": "img/bebida.01/coca_2l.jpg.avif", "preco": "16,90"},
        {"nome": "Guaraná Dolly 2L", "imagem": "img/bebida.01/dolly_2l.jpg.webp", "preco": "9,90"},
        {"nome": "Refrigerante Guaraná Antarctica 2 litros", "imagem": "img/bebida.01/guarana_ant_2l.jpg.jpeg", "preco": "12,90"},
        {"nome": "Refrigerante Sprite 2 litros", "imagem": "img/bebida.01/sprite_2l.jpg.jpg", "preco": "9,90"},
        {"nome": "Refrigerante Fanta Uva 2 litros", "imagem": "img/bebida.01/fanta_uva_2l.jpg.png", "preco": "12,90"},
        {"nome": "Fanta Laranja 2L", "imagem": "img/bebida.01/fanta_laranja_2l.jpg.webp", "preco": "12,90"},
        {"nome": "Refrigerante Coca-Cola Zero 2 litros", "imagem": "img/bebida.01/coca_zero_2l.jpg.png", "preco": "16,90"},
        {"nome": "Refrigerante Pepsi Black 2 litros", "imagem": "img/bebida.01/pepsi_black_2l.jpg", "preco": "12,90"},
        {"nome": "Refrigerante Pepsi Twist 2 litros", "imagem": "img/bebida.01/pepsi_twist_2l.jpg", "preco": "12,90"},
        {"nome": "Refrigerante Kuat 2 litros", "imagem": "img/bebida.01/kuat_2l.jpg.jpeg", "preco": "9,90"},
        {"nome": "Refrigerante Coca-Cola lata", "imagem": "img/bebida.01/coca_lata.jpg.webp", "preco": "6,50"},
        {"nome": "Refrigerante Guaraná Antarctica lata", "imagem": "img/bebida.01/guarana_ant_lata.jpg", "preco": "6,50"},
        {"nome": "Refrigerante Sprite lata", "imagem": "img/bebida.01/sprite_lata.jpg", "preco": "6,50"},
        {"nome": "Refrigerante Fanta lata", "imagem": "img/bebida.01/fanta_lata.jpg.webp", "preco": "6,50"},
        {"nome": "Refrigerante Pepsi lata", "imagem": "img/bebida.01/pepsi_lata.jpg", "preco": "6,50"},
        {"nome": "Refrigerante Schweppes lata", "imagem": "img/bebida.01/schweppes_lata.jpg.webp", "preco": "6,50"},
        {"nome": "Água tônica lata", "imagem": "img/bebida.01/agua_tonica.jpg.webp", "preco": "6,50"},
        {"nome": "Refrigerante Coca-Cola 600ml", "imagem": "img/bebida.01/coca_600ml.jpg.webp", "preco": "8,90"},
        {"nome": "Refrigerante Guaraná Antarctica 600ml", "imagem": "img/bebida.01/guarana_ant_600ml.jpg", "preco": "8,90"},
        {"nome": "Refrigerante Fanta 600ml", "imagem": "img/bebida.01/fanta_600ml.jpg.webp", "preco": "8,90"},
        {"nome": "Refrigerante Refrigerante Fanta 200ml", "imagem": "img/bebida.01/fanta_200ml.jpg.webp", "preco": "4,00"},
        {"nome": "Refrigerante Coca-Cola 200ml", "imagem": "img/bebida.01/coca_200ml.jpg.webp", "preco": "4,00"},
        {"nome": "Refrigerante Coca-Cola Zero 200ml", "imagem": "img/bebida.01/coca_zero_200ml.jpg.webp", "preco": "4,00"},
        {"nome": "Refrigerante Guaraná 200ml", "imagem": "img/bebida.01/guarana_200ml.jpg.webp", "preco": "4,00"},
        {"nome": "Pepsi 200ml", "imagem": "img/bebida.01/pepsi_200ml.jpg.webp", "preco": "4,00"},
        {"nome": "Refrigerante Coca-Cola vidro", "imagem": "img/bebida.01/coca_vidro.jpg.jpg", "preco": "6,50"},
        {"nome": "Refrigerante Coca-Cola Café", "imagem": "img/bebida.01/coca_cafe.jpg.webp", "preco": "4,50"},
        {"nome": "Água mineral Crystal", "imagem": "img/bebida.01/agua_crystal.jpg.jpg", "preco": "4,00"},
         ],
    "mercearia": [
        {"nome": "Arroz", "imagem": "img/LOGO_SITE/padaria_interior.png", "preco": "24,90"},
        {"nome": "Feijão", "imagem": "img/LOGO_SITE/padaria_interior.png", "preco": "9,90"},
        {"nome": "Leite", "imagem": "img/LOGO_SITE/padaria_interior.png", "preco": "5,90"},
        {"nome": "Açúcar", "imagem": "img/LOGO_SITE/padaria_interior.png", "preco": "4,90"},
    ],
}


@app.route('/')
def inicio():

    return render_template("index.html", categorias=CATEGORIAS)


@app.route('/cardapio')
def cardapio():

    return render_template(
        "cardapio.html",
        categorias=CATEGORIAS,
        produtos_por_categoria=PRODUTOS_POR_CATEGORIA,
    )


@app.route('/categoria/<slug>')
def categoria(slug):

    categoria_encontrada = next(
        (categoria for categoria in CATEGORIAS if categoria["slug"] == slug),
        None,
    )

    if categoria_encontrada is None:
        return redirect(url_for("cardapio"))

    return render_template(
        "categoria.html",
        categoria=categoria_encontrada,
        produtos=PRODUTOS_POR_CATEGORIA.get(slug, []),
        categorias=CATEGORIAS,
    )


app.run(debug=True)
