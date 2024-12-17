"""
Sistema de Reservas de Hotel
Este módulo implementa um sistema de reservas de hotel usando Flask.
"""

from datetime import datetime
import logging
import os
from werkzeug.utils import secure_filename
import traceback
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)

# Configuração do Flask
app.config.update(
    SECRET_KEY='123456',
    SQLALCHEMY_DATABASE_URI='sqlite:///hotel.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True,
    TEMPLATES_AUTO_RELOAD=True,
    UPLOAD_FOLDER='static/uploads/rooms',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max-limit
)

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extensões permitidas para imagens
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicialização do SQLAlchemy
db = SQLAlchemy()

# Garantir que o diretório instance existe
os.makedirs('instance', exist_ok=True)

with app.app_context():
    db.init_app(app)

# Inicialização do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # type: ignore

class User(UserMixin, db.Model):
    """Modelo para usuários do sistema."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def set_password(self, password):
        """Define a senha do usuário usando hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta."""
        return check_password_hash(self.password_hash, password)


class RoomImage(db.Model):
    """Modelo para imagens dos quartos."""
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Room(db.Model):
    """Modelo para quartos do hotel."""
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')
    reservations = db.relationship('Reservation', backref='room', lazy=True)
    images = db.relationship('RoomImage', backref='room', lazy=True, cascade='all, delete-orphan')


class Reservation(db.Model):
    """Modelo para reservas de quartos."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário pelo ID."""
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Rota principal."""
    rooms = Room.query.filter_by(status='available').all()
    return render_template('index.html', rooms=rooms)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de usuários."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        
        flash('Email ou senha inválidos.', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Rota para registro de novos usuários."""
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not all([name, email, password]):
                flash('Todos os campos são obrigatórios.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email já cadastrado.', 'error')
                return redirect(url_for('register'))
            
            user = User()
            user.name = name
            user.email = email
            user.set_password(password)
            user.is_admin = False
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registro realizado com sucesso!', 'success')
            return redirect(url_for('login'))
            
    except Exception as e:
        logger.error(f"Erro durante o registro: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        flash('Ocorreu um erro durante o registro.', 'error')
    
    return render_template('register.html')


@app.route('/make_reservation/<int:room_id>', methods=['GET', 'POST'])
@login_required
def make_reservation(room_id):
    """Rota para fazer uma reserva."""
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        try:
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')
            
            if not check_in_str or not check_out_str:
                flash('Todas as datas são obrigatórias.', 'error')
                return redirect(url_for('make_reservation', room_id=room_id))
            
            try:
                check_in = datetime.strptime(str(check_in_str), '%Y-%m-%d').date()
                check_out = datetime.strptime(str(check_out_str), '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de data inválido. Use o formato YYYY-MM-DD.', 'error')
                return redirect(url_for('make_reservation', room_id=room_id))
            
            if check_in >= check_out:
                flash('Data de check-out deve ser posterior ao check-in.', 'error')
                return redirect(url_for('make_reservation', room_id=room_id))
            
            reservation = Reservation()
            reservation.user_id = current_user.id
            reservation.room_id = room.id
            reservation.check_in = check_in
            reservation.check_out = check_out
            
            room.status = 'occupied'
            
            db.session.add(reservation)
            db.session.commit()
            
            flash('Reserva realizada com sucesso!', 'success')
            return redirect(url_for('my_reservations'))
            
        except Exception as e:
            logger.error(f"Erro ao fazer reserva: {str(e)}")
            db.session.rollback()
            flash('Erro ao fazer reserva.', 'error')
    
    return render_template('make_reservation.html', room=room)


@app.route('/logout')
@login_required
def logout():
    """Rota para logout de usuários."""
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


@app.route('/my_reservations')
@login_required
def my_reservations():
    """Rota para visualizar reservas do usuário."""
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('my_reservations.html', reservations=reservations)


@app.route('/admin')
@login_required
def admin_dashboard():
    """Rota para o painel administrativo."""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('index'))
    return render_template('admin/dashboard.html')


@app.route('/admin/rooms', methods=['GET', 'POST'])
@login_required
def admin_rooms():
    """Rota para gerenciamento de quartos."""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            room = Room()
            room.number = request.form.get('number')
            room.type = request.form.get('type')
            room.price = float(request.form.get('price', 0))
            room.description = request.form.get('description')
            room.status = 'available'
            
            db.session.add(room)
            db.session.commit()
            
            flash('Quarto adicionado com sucesso!', 'success')
            return redirect(url_for('admin_rooms'))
            
        except Exception as e:
            logger.error(f"Erro ao adicionar quarto: {str(e)}")
            db.session.rollback()
            flash('Erro ao adicionar quarto.', 'error')
    
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)


@app.route('/admin/reservations')
@login_required
def admin_reservations():
    """Rota para gerenciamento de reservas."""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('index'))
    
    reservations = Reservation.query.all()
    return render_template('admin/reservations.html', reservations=reservations)


@app.route('/admin/reservation/<int:reservation_id>/update', methods=['POST'])
@login_required
def update_reservation(reservation_id):
    """Rota para atualizar status de reserva."""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    action = request.form.get('action')
    
    if action == 'confirm':
        reservation.status = 'confirmed'
        flash('Reserva confirmada!', 'success')
    elif action == 'cancel':
        reservation.status = 'cancelled'
        reservation.room.status = 'available'
        flash('Reserva cancelada!', 'success')
    
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"Erro ao atualizar reserva: {str(e)}")
        db.session.rollback()
        flash('Erro ao atualizar reserva.', 'error')
    
    return redirect(url_for('admin_reservations'))


@app.route('/admin/rooms/<int:room_id>/upload_image', methods=['POST'])
@login_required
def upload_room_image(room_id):
    """Rota para upload de imagens do quarto."""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('index'))
    
    room = Room.query.get_or_404(room_id)
    file_path = None  # Inicializa file_path fora do bloco try
    
    if 'image' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin_rooms'))
    
    file = request.files['image']
    if not file or file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin_rooms'))
    
    if file and allowed_file(file.filename or ''):
        try:
            # Garante que filename não é None
            original_filename = file.filename or 'unnamed_file'
            filename = secure_filename(original_filename)
            
            # Adiciona timestamp ao nome do arquivo para evitar duplicatas
            base, ext = os.path.splitext(filename)
            timestamp = int(datetime.utcnow().timestamp())
            unique_filename = f"{base}_{timestamp}{ext}"
            
            # Define o caminho do arquivo
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Salva o arquivo
            file.save(file_path)
            
            # Cria novo objeto RoomImage
            new_image = RoomImage()
            new_image.filename = unique_filename
            new_image.room_id = room.id
            
            db.session.add(new_image)
            db.session.commit()
            
            flash('Imagem adicionada com sucesso!', 'success')
        except Exception as e:
            logger.error(f"Erro ao fazer upload da imagem: {str(e)}")
            flash('Erro ao fazer upload da imagem.', 'error')
            db.session.rollback()
            
            # Remove o arquivo se houve erro no banco de dados
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo temporário: {str(e)}")
    else:
        flash('Tipo de arquivo não permitido.', 'error')
    
    return redirect(url_for('admin_rooms'))


@app.route('/admin/rooms/<int:room_id>/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_room_image(room_id, image_id):
    """Rota para deletar imagem do quarto."""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('index'))
    
    image = RoomImage.query.get_or_404(image_id)
    if image.room_id != room_id:
        flash('Imagem não pertence a este quarto.', 'error')
        return redirect(url_for('admin_rooms'))
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        db.session.delete(image)
        db.session.commit()
        
        flash('Imagem removida com sucesso!', 'success')
    except Exception as e:
        logger.error(f"Erro ao remover imagem: {str(e)}")
        flash('Erro ao remover imagem.', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_rooms'))


def init_admin():
    """Inicializa o usuário administrador."""
    admin = User.query.filter_by(email='admin@hotel.com').first()
    if not admin:
        admin = User()
        admin.name = 'Administrador'
        admin.email = 'admin@hotel.com'
        admin.set_password('admin123')
        admin.is_admin = True
        
        db.session.add(admin)
        db.session.commit()
        logger.info('Usuário administrador criado com sucesso')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_admin()
    app.run(debug=True)
