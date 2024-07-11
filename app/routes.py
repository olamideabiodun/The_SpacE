from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LOgin
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User
from flask_login import logout_user
from flask_login import login_required, UserMixin, LoginManager
from flask import request
from urllib.parse import urlsplit
from app.forms import Register
from datetime import timezone, datetime
from app.forms import EditProfile


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    posts= [
        {
            'author': {'username':'Fareedah'},
            'body': 'I really wanna be the very best!'
        },
        {
            'author': {'username':'Maddie'},
            'body': 'I really hope i pass the design course!'
        },
        {
            'author': {'username': 'Yasir'},
            'body': 'May Allah accept all our prayers, Ameen!'
        },
        {
            'author': {'username': 'Aarol'},
            'body': 'I am not undecided!'
        }
        
    ]
    return render_template('index.html', title='Home page', posts=posts, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LOgin()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.Password.data):
            flash('Invalid username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title = 'Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = Register()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sign up successful, now proceed to login!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Testing'},
        {'author': user, 'body': 'Testing'}
    ]
    return render_template('user.html', user = user, posts = posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/editProfile', methods=['GET', 'POST'])
@login_required
def editProfile():
    form = EditProfile()
    # if form.validate_on_submit():
    #     current_user.username = form.username.data
    #     current_user.about_me = form.about_me.data
    #     db.session.commit()
    #     flash('Changes saved.')
    #     return redirect(url_for('editProfile'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.about_me.data = current_user.about_me
    # return render_template('editProfile.html', title='Edit Profile', form=form)

    if request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        return render_template('editProfile.html', title='Edit Profile', form=form)
    elif form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('editProfile'))
