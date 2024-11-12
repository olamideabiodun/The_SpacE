"""Add likes_count and comments_count to Post model

Revision ID: 9b87b5bfee8f
Revises: f104ce518ee3
Create Date: 2024-11-11 22:28:35.560963

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b87b5bfee8f'
down_revision = 'f104ce518ee3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'bookmarks' not in inspector.get_table_names():
        op.create_table('bookmarks',
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('post_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
        )
    
    if 'post_likes' not in inspector.get_table_names():
        op.create_table('post_likes',
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('post_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
        )

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_message_sender_id_user', 'user', ['sender_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_message_recipient_id_user', 'user', ['recipient_id'], ['id'], ondelete='CASCADE')
        
        try:
            batch_op.create_index('idx_message_sender_recipient', ['sender_id', 'recipient_id'], unique=False)
        except Exception:
            pass
        try:
            batch_op.create_index('idx_message_timestamp', ['timestamp'], unique=False)
        except Exception:
            pass

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('likes_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('comments_count', sa.Integer(), nullable=True))
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=9999),
               type_=sa.String(length=140),
               nullable=True)
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        
        try:
            batch_op.drop_index('ix_post_user_id')
        except Exception:
            pass
            
        try:
            batch_op.create_index('idx_post_timestamp', ['timestamp'], unique=False)
        except Exception:
            pass
        try:
            batch_op.create_index('idx_post_user_id', ['user_id'], unique=False)
        except Exception:
            pass

    with op.batch_alter_table('user', schema=None) as batch_op:
        try:
            batch_op.create_index('idx_user_last_seen', ['last_seen'], unique=False)
        except Exception:
            pass
        try:
            batch_op.create_index('idx_user_username_email', ['username', 'email'], unique=False)
        except Exception:
            pass


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('idx_user_username_email')
        batch_op.drop_index('idx_user_last_seen')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_index('idx_post_user_id')
        batch_op.drop_index('idx_post_timestamp')
        batch_op.create_index('ix_post_user_id', ['user_id'], unique=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.alter_column('body',
               existing_type=sa.String(length=140),
               type_=sa.VARCHAR(length=9999),
               nullable=False)
        batch_op.drop_column('comments_count')
        batch_op.drop_column('likes_count')

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_message_sender_id_user', 'user', ['sender_id'], ['id'])
        batch_op.create_foreign_key('fk_message_recipient_id_user', 'user', ['recipient_id'], ['id'])
        batch_op.drop_index('idx_message_timestamp')
        batch_op.drop_index('idx_message_sender_recipient')

    op.drop_table('post_likes')
    op.drop_table('bookmarks')
