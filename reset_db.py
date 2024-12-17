import os
from app import app, db

# Remove o banco de dados existente
db_file = 'hotel.db'
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Banco de dados antigo removido: {db_file}")

# Cria um novo banco de dados
with app.app_context():
    db.create_all()
    print("Novo banco de dados criado com sucesso!")
