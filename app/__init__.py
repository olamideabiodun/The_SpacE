from flask import Flask, request, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail
import logging
from logging import StreamHandler
import sys

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
moment = Moment()
mail = Mail()

def configure_logging(app):
    # Clear any existing handlers to avoid duplicates
    app.logger.handlers.clear()
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Set log level based on environment
    if app.debug:
        console_handler.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # Add handler to app logger
    app.logger.addHandler(console_handler)
    
    # Log startup
    app.logger.info('The Space startup')
    
    # Request logging
    @app.before_request
    def log_request_info():
        app.logger.debug(f'Request: {request.method} {request.url}')
        
    @app.after_request
    def log_response_info(response):
        app.logger.debug(f'Response: {response.status}')
        return response
        
    # Error logging
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return render_template('errors/500.html'), 500

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging first
    configure_logging(app)
    
    app.config['POSTS_PER_PAGE'] = 25

    # Set database URL based on environment
    if app.config.get('ENV') == 'production':
        database_url = app.config.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Use SQLite for local development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    # Initialize Flask extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    login.login_view = 'auth.login'

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Register API blueprint
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Move the models import here
    from app import models

    return app