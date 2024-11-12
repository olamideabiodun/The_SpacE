from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail
import logging
import sys

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
moment = Moment()
mail = Mail()

def create_app(config_class=Config):
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['POSTS_PER_PAGE'] = 25

    # Set database URL based on environment
    if app.config.get('ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URL')
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

    # Configure logging for production
    if not app.debug and not app.testing:
        # Use sys.stdout for logging
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        app.logger.info('The Space startup')

    return app