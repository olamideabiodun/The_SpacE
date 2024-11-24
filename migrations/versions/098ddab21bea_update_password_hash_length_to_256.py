"""Update password_hash length to 256

Revision ID: 098ddab21bea
Revises: ab1287056126
Create Date: 2024-11-24 20:29:50.216805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '098ddab21bea'
down_revision = 'ab1287056126'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    op.drop_table('posts')
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.alter_column('follower_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('followed_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=140),
               type_=sa.String(length=99999),
               existing_nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=256),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=128),
               existing_nullable=False)

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.String(length=99999),
               type_=sa.VARCHAR(length=140),
               existing_nullable=True)

    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.alter_column('followed_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('follower_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    op.create_table('posts',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comments',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
