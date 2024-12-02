from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import User, Post, Message, followers as followers_table, Activity
from app.main.forms import PostForm, EditProfile, EmptyForm, MessageForm, ResetPasswordForm, ResetPasswordRequestForm
from datetime import datetime, timezone
from sqlalchemy import or_
from app.email import send_password_reset_email
from app.main.forms import CommentForm
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Optional
from werkzeug.security import check_password_hash
import requests
from app.services.news_services import get_random_news

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(Post).join(
        followers_table, (followers_table.c.followed_id == Post.user_id)
    ).filter(followers_table.c.follower_id == current_user.id).order_by(
        Post.timestamp.desc()
    ).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data.strip(), author=current_user)
        db.session.add(post)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Error committing post: {str(e)}')
            db.session.rollback()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.index'))
    else:
        current_app.logger.debug(f'Form errors: {form.errors}')

    recent_activities = Activity.query.order_by(Activity.timestamp.desc()).limit(10).all()
    return render_template('main/index.html', 
                         title='Home',
                         form=form,
                         posts=posts.items,
                         recent_activities=recent_activities)

@bp.route('/explore', methods=['GET'])
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
    
    # If no search query, show regular explore page with sorting and filtering
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'recent')
    filter_type = request.args.get('filter', 'all')
    
    posts_query = Post.query
    
    if sort == 'popular':
        posts_query = posts_query.order_by(Post.likes_count.desc())
    elif sort == 'commented':
        posts_query = posts_query.order_by(Post.comments_count.desc())
    else:
        posts_query = posts_query.order_by(Post.timestamp.desc())
    
    featured_users = User.query.order_by(User.followers_count.desc()).limit(4).all()
    
    posts = posts_query.paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    latest_news = get_random_news()
    
    return render_template('main/explore.html',
                         title='Explore',
                         posts=posts.items,
                         featured_users=featured_users,
                         search_query=search_query,
                         news=latest_news)

@bp.route('/user/<username>', methods=['GET', 'POST'])
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
    else:
        flash('Please correct the errors in the form.', 'danger')
        current_app.logger.debug(f'Form errors: {form.errors}')
    
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    current_app.logger.debug(f'Number of posts for user {user.username}: {len(posts)}')
    
    return render_template('main/user.html', user=user, posts=posts, form=form)

@bp.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfile(original_username=username)
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.about_me = form.about_me.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('main.profile', username=current_user.username))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('main/edit_profile.html', form=form, user=current_user)

@bp.route('/follow/<username>', methods=['POST'])
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
        
        try:
            if current_user.follow(user):
                db.session.commit()
                flash(f'You are now following {username}!')
            else:
                flash(f'You are already following {username}.')
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of error
            current_app.logger.error(f'Error following user {username}: {e}')
            flash('An error occurred while trying to follow the user. Please try again.')
        
        return redirect(url_for('main.user', username=username))
    
    flash('There was an issue with your follow request. Please try again.')
    return redirect(url_for('main.explore', q=request.args.get('q', '')))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You have unfollowed {username}.')
        return redirect(url_for('main.user', username=username))
    return redirect(url_for('main.index'))

# API routes for post interactions
@bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user in post.likes:
        post.likes.remove(current_user)
        post.likes_count -= 1
    else:
        post.likes.append(current_user)
        post.likes_count += 1
    db.session.commit()
    return jsonify({'likes_count': len(post.likes)})

@bp.route('/api/posts/<int:post_id>/bookmark', methods=['POST'])
@login_required
def bookmark_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post in current_user.bookmarks:
        current_user.bookmarks.remove(post)
    else:
        current_user.bookmarks.append(post)
    db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/user/<username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template('main/followers.html', user=user, followers=followers)

@bp.route('/user/<username>/following')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    following = user.followed.all()
    return render_template('main/following.html', user=user, following=following)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('main/reset_password_request.html',
                         title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('main/reset_password.html', form=form)


# will work on this later
@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('main.user', username=recipient))
    return render_template('main/send_message.html', title='Send Message', form=form, recipient=user)

@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    db.session.commit()
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).all()
    return render_template('main/messages.html', messages=messages)


@bp.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    return render_template('main/post.html', post=post, form=form)

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
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

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    submit = SubmitField('Submit')

def fetch_latest_news():
    api_key = 'c837c86742e740c18ddc42ecfb52852e'
    url = f'https://newsapi.org/v2/everything?q=edtech&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        news_data = response.json()
        return news_data.get('articles', [])
    except Exception as e:
        current_app.logger.error(f'Error fetching news: {str(e)}')
        return []

