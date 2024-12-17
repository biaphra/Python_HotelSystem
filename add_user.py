"""
Script para adicionar um novo usuário ao sistema
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

def add_user(name, email, password, is_admin=False):
    """Adiciona um novo usuário ao sistema."""
    with app.app_context():
        # Verifica se o usuário já existe
        if User.query.filter_by(email=email).first():
            print(f"Usuário com email {email} já existe!")
            return False
        
        # Cria novo usuário
        user = User()
        user.name = name
        user.email = email
        user.password_hash = generate_password_hash(password)
        user.is_admin = is_admin
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"Usuário {name} adicionado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao adicionar usuário: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    # Exemplo de uso
    add_user(
        name='João Silva',
        email='joao.silva@email.com',
        password='senha123',
        is_admin=False
    )
