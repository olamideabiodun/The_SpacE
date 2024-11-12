from flask import render_template, request, current_app
from app.errors import bp
from app.models import db

@bp.app_errorhandler(404)
def not_found_error(error):
    current_app.logger.warning(f'Page not found: {request.url}')
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    current_app.logger.error('Server Error: %s', error, exc_info=True)
    db.session.rollback()
    return render_template('errors/500.html'), 500 