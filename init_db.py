from app import db, app

# Garante que as tabelas sejam criadas no banco de dados
with app.app_context():
    db.create_all()
    print("Banco de dados inicializado com sucesso.")