from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///florist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rg = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) 
    tipo = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('pedidos', lazy=True))
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    produtos = db.relationship('Produto', secondary='pedido_produto', backref='pedidos')

pedido_produto = db.Table('pedido_produto',
    db.Column('pedido_id', db.Integer, db.ForeignKey('pedido.id'), primary_key=True),
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), primary_key=True)
)

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'POST':
        rg = request.form['rg']
        nome = request.form['nome']
        telefone = request.form['telefone']
        novo_cliente = Cliente(rg=rg, nome=nome, telefone=telefone)
        db.session.add(novo_cliente)
        db.session.commit()
        return redirect(url_for('clientes'))
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/remover/<int:id>', methods=['GET', 'POST'])
def remover_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('clientes'))

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'POST':
        nome = request.form['nome']  
        tipo = request.form['tipo']
        preco = float(request.form['preco'])
        novo_produto = Produto(nome=nome, tipo=tipo, preco=preco)  
        db.session.add(novo_produto)
        db.session.commit()
        return redirect(url_for('produtos'))
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/remover/<int:id>', methods=['GET', 'POST'])
def remover_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('produtos'))

@app.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        produto_ids = request.form.getlist('produtos')
        novo_pedido = Pedido(cliente_id=cliente_id)
        for produto_id in produto_ids:
            produto = Produto.query.get(produto_id)
            novo_pedido.produtos.append(produto)
        db.session.add(novo_pedido)
        db.session.commit()
        return redirect(url_for('pedidos'))
    pedidos = Pedido.query.all()
    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    return render_template('pedidos.html', pedidos=pedidos, clientes=clientes, produtos=produtos)

@app.route('/pedidos/remover/<int:id>', methods=['GET', 'POST'])
def remover_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    db.session.delete(pedido)
    db.session.commit()
    return redirect(url_for('pedidos'))


if __name__ == '__main__':
    from init_db import init_db
    init_db()
    app.run(debug=True)

