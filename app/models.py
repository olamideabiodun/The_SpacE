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



followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index = True, unique=True, nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index = True, unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional [str]] = so.mapped_column(sa.String(180))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )

    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()))
    
    def following_count(self):
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            self.following.select().subquery()))

    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id).union(
            Post.query.filter_by(user_id=self.id)
        ).order_by(Post.timestamp.desc())

    def following_posts(self):
        return db.session.scalars(
            sa.select(Post)
            .join(followers, Post.user_id == followers.c.followed_id)
            .where(followers.c.follower_id == self.id)
            .order_by(Post.timestamp.desc())
        )

    def search_posts(self, query_text):
        return db.session.scalars(
            sa.select(Post)
            .where(
                or_(
                    Post.body.ilike(f'%{query_text}%'),
                    User.username.ilike(f'%{query_text}%')
                )
            )
            .join(User, Post.user_id == User.id)
            .order_by(Post.timestamp.desc())
        )

    def search_users(self, query_text):
        return db.session.scalars(
            sa.select(User)
            .where(
                or_(
                    User.username.ilike(f'%{query_text}%'),
                    User.email.ilike(f'%{query_text}%'),
                    User.about_me.ilike(f'%{query_text}%')
                )
            )
            .where(User.id != self.id)  # Exclude the current user
            .order_by(User.username)
        )


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(9999))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


