from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///florist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'CHAVEMUITOSECRETA'

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
        try:
            rg = request.form['rg']
            nome = request.form['nome']
            telefone = request.form['telefone']
            # Verificar se o RG já existe
            if Cliente.query.filter_by(rg=rg).first():
                flash('Este RG já está cadastrado.', 'danger')
            else:
                novo_cliente = Cliente(rg=rg, nome=nome, telefone=telefone)
                db.session.add(novo_cliente)
                db.session.commit()
                flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar cliente: {e}', 'danger')
            return redirect(url_for('clientes'))
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/remover/<int:id>', methods=['GET', 'POST'])
def remover_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover cliente. Existe um pedido associado a ele!', 'danger')
    return redirect(url_for('clientes'))

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'POST':
        try:
            nome = request.form['nome']  
            tipo = request.form['tipo']
            preco = float(request.form['preco'])
            novo_produto = Produto(nome=nome, tipo=tipo, preco=preco)
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('produtos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar produto: {e}', 'danger')
            return redirect(url_for('produtos'))
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/remover/<int:id>', methods=['GET', 'POST'])
def remover_produto(id):
    try:
        produto = Produto.query.get_or_404(id)
        db.session.delete(produto)
        db.session.commit()
        flash('Produto removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover produto: {e}', 'danger')
    return redirect(url_for('produtos'))

@app.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    if request.method == 'POST':
        try:
            cliente_id = request.form['cliente_id']
            produto_ids = request.form.getlist('produtos')
            novo_pedido = Pedido(cliente_id=cliente_id)
            for produto_id in produto_ids:
                produto = Produto.query.get(produto_id)
                if produto:
                    novo_pedido.produtos.append(produto)
                else:
                    flash(f'Produto com ID {produto_id} não encontrado.', 'danger')
                    return redirect(url_for('pedidos'))
            db.session.add(novo_pedido)
            db.session.commit()
            flash('Pedido cadastrado com sucesso!', 'success')
            return redirect(url_for('pedidos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar pedido: {e}', 'danger')
            return redirect(url_for('pedidos'))
    pedidos = Pedido.query.all()
    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    return render_template('pedidos.html', pedidos=pedidos, clientes=clientes, produtos=produtos)

@app.route('/pedidos/remover/<int:id>', methods=['GET', 'POST'])
def remover_pedido(id):
    try:
        pedido = Pedido.query.get_or_404(id)
        db.session.delete(pedido)
        db.session.commit()
        flash('Pedido removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover pedido: {e}', 'danger')
    return redirect(url_for('pedidos'))


if __name__ == '__main__':
    from init_db import init_db
    init_db()
    app.run(debug=True)