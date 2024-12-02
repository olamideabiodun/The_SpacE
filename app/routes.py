#Supposed to be deleted but keot for reference
from app import app, db
from flask import render_template, flash, redirect, url_for
from app.main.forms import Login
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User
from flask_login import logout_user
from flask_login import login_required, UserMixin, LoginManager
from flask import request
from urllib.parse import urlsplit
from app.main.forms import Register
from datetime import timezone, datetime
from app.main.forms import EditProfile
from app.main.forms import EmptyForm
from app.main.forms import PostForm
from app.models import Post
from app.main.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.main.forms import ResetPasswordForm
from sqlalchemy import or_
from app.main.forms import MessageForm
from app.models import Message
from sqlalchemy.orm import joinedload


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
        
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
                         form=form, 
                         user=current_user)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(body=form.post.data.strip(), author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.user', username=username))
        except Exception as e:
            current_app.logger.error(f'Error committing post: {str(e)}')
            db.session.rollback()
            flash('An error occurred while creating your post. Please try again.', 'danger')
    
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    current_app.logger.debug(f'Number of posts for user {user.username}: {len(posts)}')
    
    return render_template('main/user.html', user=user, posts=posts, form=form)

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

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('main.user', username=username))
    
    flash('There was an issue with your follow request. Please try again.')
    return redirect(url_for('main.explore', q=request.args.get('q', '')))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/user/<username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template('followers.html', user=user, followers=followers)

@app.route('/user/<username>/following')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    following = user.followed.all()
    return render_template('following.html', user=user, following=following)

@app.route('/explore')
@login_required
def explore():
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        # Search users
        users = User.query.filter(or_(
            User.username.ilike(f'%{search_query}%'),
            User.about_me.ilike(f'%{search_query}%')
        )).limit(8).all()
        
        # Search posts
        posts = Post.query.filter(or_(
            Post.body.ilike(f'%{search_query}%'),
            Post.author.has(User.username.ilike(f'%{search_query}%'))
        )).order_by(Post.timestamp.desc()).limit(10).all()
        
        return render_template('main/explore.html',
                             title='Search Results',
                             search_query=search_query,
                             users=users,
                             posts=posts)
    
    # If no search query, show regular explore page content
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('main/explore.html',
                         title='Explore',
                         posts=posts.items)

@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('user', username=recipient))
    return render_template('send_message.html', title='Send Message',
                         form=form, recipient=user)

@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    db.session.commit()
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, post_id=post_id, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.post', post_id=post_id))
    return redirect(url_for('main.post', post_id=post_id))
