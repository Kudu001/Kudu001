from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.admin import admin_bp
    from app.views.doctor import doctor_bp
    from app.views.nurse import nurse_bp
    from app.views.receptionist import receptionist_bp
    from app.views.accountant import accountant_bp
    from app.views.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(nurse_bp, url_prefix='/nurse')
    app.register_blueprint(receptionist_bp, url_prefix='/receptionist')
    app.register_blueprint(accountant_bp, url_prefix='/accountant')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app