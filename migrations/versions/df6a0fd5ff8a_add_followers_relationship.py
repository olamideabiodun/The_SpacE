"""Add followers relationship

Revision ID: df6a0fd5ff8a
Revises: 4d65f5c5abe9
Create Date: 2024-11-10 21:45:53.337754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df6a0fd5ff8a'
down_revision = '4d65f5c5abe9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.alter_column('follower_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('followed_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.alter_column('followed_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('follower_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###