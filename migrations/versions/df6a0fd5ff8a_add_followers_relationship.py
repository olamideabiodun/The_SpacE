"""Add followers relationship

Revision ID: df6a0fd5ff8a
Revises: 4d65f5c5abe9
Create Date: 2024-11-10 21:45:53.337754

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'df6a0fd5ff8a'
down_revision = '4d65f5c5abe9'
branch_labels = None
depends_on = None

def upgrade():
    # Get the current connection and create an inspector
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if the 'followers' table already exists
    if 'followers' not in inspector.get_table_names():
        op.create_table('followers',
            sa.Column('follower_id', sa.Integer(), nullable=False),
            sa.Column('followed_id', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('follower_id', 'followed_id'),
            sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ondelete='CASCADE')
        )
    else:
        # Optionally log that the table already exists
        print("The 'followers' table already exists. Skipping creation.")

def downgrade():
    # Drop the 'followers' table if it exists
    conn = op.get_bind()
    inspector = inspect(conn)

    if 'followers' in inspector.get_table_names():
        op.drop_table('followers')
