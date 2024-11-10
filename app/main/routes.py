from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app.main import bp
from app.models import Post, User
from app import db

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Home', posts=posts)

# Add other main routes here 