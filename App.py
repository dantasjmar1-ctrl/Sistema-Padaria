from flask import Flask
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

@app.route('/')
def inicio():

    cursor.execute("SELECT nome, preco, disponibilidade FROM Produto")

    produtos = cursor.fetchall()

    html = """
    <html>
    <head>
        <title>Padaria Online</title>

        <style>

            body{
                font-family: Arial;
                background-color: #f5f5f5;
                padding: 30px;
            }

            h1{
                text-align: center;
                color: orange;
            }

            .container{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
            }

            .card{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px gray;
            }

            .preco{
                color: green;
                font-size: 22px;
                font-weight: bold;
            }

            .status{
                color: blue;
            }

        </style>

    </head>

    <body>

        <h1>Produtos da Padaria</h1>

        <div class="container">
    """

    for produto in produtos:

        html += f"""

        <div class="card">

            <h2>{produto.nome}</h2>

            <p class="preco">
                R$ {produto.preco}
            </p>

            <p class="status">
                {produto.disponibilidade}
            </p>

        </div>

        """

    html += """

        </div>

    </body>

    </html>

    """

    return html

app.run(debug=True)
