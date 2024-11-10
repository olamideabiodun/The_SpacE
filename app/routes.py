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
from app.forms import EmptyForm
from app.forms import PostForm
from app.models import Post


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    search_query = request.args.get('q', '')
    
    if search_query:
        posts = current_user.search_posts(search_query).all()
        users = current_user.search_users(search_query).all()
    else:
        posts = current_user.following_posts().all()
        users = []
    
    return render_template('index.html', 
                         title='Home', 
                         posts=posts, 
                         users=users, 
                         search_query=search_query, 
                         form=form)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
    return redirect(url_for('index'))

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
    form = EmptyForm()
    return render_template('user.html', user = user, posts = posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/editProfile', methods=['GET', 'POST'])
@login_required
def editProfile():
    form = EditProfile(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Changes saved.')
        return redirect(url_for('editProfile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('editProfile.html', title='Edit Profile', form=form)

    # if request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.about_me.data = current_user.about_me
    #     return render_template('editProfile.html', title='Edit Profile', form=form)
    # elif form.validate_on_submit():
    #     current_user.username = form.username.data
    #     current_user.about_me = form.about_me.data
    #     db.session.commit()

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!')
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}.')
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    # Similar to index but shows all posts, not just from followed users
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)
