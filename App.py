from flask import Flask, render_template
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

    cursor.execute("SELECT nome, preco, disponibilidade foto FROM Produto")

    produtos = cursor.fetchall()

    return render_template("index.html", produtos=produtos)

app.run(debug=True)
