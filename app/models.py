from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from flask_login import UserMixin
from app import login
from hashlib import md5
from sqlalchemy.orm import aliased
from sqlalchemy import or_
from time import time
import jwt
from flask import current_app
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from sqlalchemy import Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy.orm import Query
from sqlalchemy.orm import backref




followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(db.String(120), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(128))
    about_me: Mapped[Optional[str]] = mapped_column(sa.String(180))
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # Add indexes for better query performance
    __table_args__ = (
        Index('idx_user_username_email', 'username', 'email'),
        Index('idx_user_last_seen', 'last_seen')
    )

    # Optimize relationships with join loading strategies
    posts = relationship(
        'Post',
        back_populates='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    followed = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=backref('followers', lazy='dynamic'),
        lazy='dynamic',
        join_depth=1  # Optimize join depth
    )

    messages_sent = relationship(
        'Message',
        foreign_keys='Message.sender_id',
        back_populates='sender',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    messages_received = relationship(
        'Message',
        foreign_keys='Message.recipient_id',
        back_populates='recipient',
        lazy='dynamic',
        cascade='all, delete'
    )

    skills = db.relationship('Skill', backref='user', lazy='dynamic')

    @hybrid_property
    def following_count(self) -> int:
        return self.followed.count()
    
    @hybrid_property
    def followers_count(self):
        return self.followers.count()

    @followers_count.expression
    def followers_count(cls):
        return (
            select(func.count())
            .select_from(followers)
            .where(followers.c.followed_id == cls.id)
            .scalar_subquery()
        )

    def follow(self, user: 'User') -> bool:
        if not user or not isinstance(user, User):
            return False
        if user.id == self.id:
            return False
        if not self.is_following(user):
            self.followed.append(user)
            return True
        return False
    
    def unfollow(self, user: 'User') -> bool:
        if not user or not isinstance(user, User):
            return False
        if self.is_following(user):
            self.followed.remove(user)
            return True
        return False

    def is_following(self, user: 'User') -> bool:
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        # Optimize query with single join and union
        return (
            db.session.scalars(
                select(Post)
                .where(
                    or_(
                        and_(
                            followers.c.follower_id == self.id,
                            followers.c.followed_id == Post.user_id
                        ),
                        Post.user_id == self.id
                    )
                )
                .order_by(Post.timestamp.desc())
                .execution_options(join_hint='USE_INDEX')
            )
        )

    def following_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def search_posts(self, query):
        return Post.query.filter(
            or_(Post.body.ilike(f'%{query}%'),
                Post.author.has(User.username.ilike(f'%{query}%')))
        ).order_by(Post.timestamp.desc())

    def search_users(self, query):
        return User.query.filter(
            or_(User.username.ilike(f'%{query}%'),
                User.about_me.ilike(f'%{query}%'))
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        except:
            return None
        return db.session.get(User, id)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page=1, per_page=10):
        try:
            ids, total = cls.query.filter(cls.__ts_vector__.match(expression)).with_entities(
                cls.id, func.count(cls.id).over()
            ).offset((page - 1) * per_page).limit(per_page).all()
            if total == 0:
                return cls.query.filter_by(id=0), 0
            when = []
            for i in range(len(ids)):
                when.append((ids[i], i))
            return cls.query.filter(cls.id.in_(ids)).order_by(
                db.case(when, value=cls.id)), total
        except Exception as e:
            current_app.logger.error(f'Search error: {str(e)}')
            return cls.query.filter_by(id=0), 0

class Post(db.Model):
    __searchable__ = ['body']  # fields to be searched
    __table_args__ = (
        Index('idx_post_timestamp', 'timestamp'),
        Index('idx_post_user_id', 'user_id'),
        {'extend_existing': True}  # Add this to prevent table conflicts
    )
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship(
        'User', secondary='post_likes',
        backref=db.backref('liked_posts', lazy='dynamic')
    )
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return f'<Post {self.body}>'

# Association table for post likes
post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

# Association table for bookmarks
bookmarks = db.Table('bookmarks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

# Move the event listener outside of the Post class
@event.listens_for(Post, 'after_insert')
def update_post_search_vector(mapper, connection, target):
    try:
        connection.execute(
            'UPDATE post SET ts_vector = to_tsvector(\'english\', body) WHERE id = %s',
            target.id
        )
    except Exception as e:
        current_app.logger.error(f'Error updating search vector: {str(e)}')
        # Consider whether to raise the exception or handle silently


@login.user_loader
def load_user(id):
    try:
        return db.session.get(User, int(id))
    except Exception as e:
        current_app.logger.error(f'Error loading user: {str(e)}')
        return None


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(
        sa.ForeignKey('user.id', ondelete='CASCADE', name='fk_message_sender'),
        index=True
    )
    recipient_id: Mapped[int] = mapped_column(
        sa.ForeignKey('user.id', ondelete='CASCADE', name='fk_message_recipient'),
        index=True
    )
    body: Mapped[str] = mapped_column(sa.String(140))
    timestamp: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    # Optimize relationships with lazy loading and join conditions
    sender: Mapped[User] = relationship(
        'User',
        foreign_keys=[sender_id],
        back_populates='messages_sent',
        lazy='joined'
    )
    
    recipient: Mapped[User] = relationship(
        'User',
        foreign_keys=[recipient_id],
        back_populates='messages_received',
        lazy='joined'
    )

    def __repr__(self):
        return f'<Message {self.body}>'

    __table_args__ = (
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_sender_recipient', 'sender_id', 'recipient_id')
    )


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Skill {self.name}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    post = db.relationship('Post', backref='comments', lazy='select')
    author = db.relationship('User', backref='comments', lazy='select')

    def __repr__(self):
        return f'<Comment {self.body[:20]} by {self.author.username}>'


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(140))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)  # Optional reference to a post
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # Optional reference to a comment
    timestamp = db.Column(db.DateTime, index=True, default=db.func.current_timestamp())

    user = db.relationship('User', backref='activities')
    post = db.relationship('Post', backref='activities', foreign_keys=[post_id])
    comment = db.relationship('Comment', backref='activities', foreign_keys=[comment_id])

    def __repr__(self):
        return f'<Activity {self.action} by User {self.user_id}>'


