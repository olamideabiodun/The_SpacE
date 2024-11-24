"""Update password_hash length to 256

Revision ID: 098ddab21bea
Revises: ab1287056126
Create Date: 2024-11-24 00:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '098ddab21bea'
down_revision = 'ab1287056126'
branch_labels = None
depends_on = None

def upgrade():
    # Alter the password_hash column to increase its length
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('password_hash',
            type_=sa.String(length=256),  # Increase length as needed
            existing_type=sa.String(length=128),
            postgresql_using='password_hash::varchar(256)'  # PostgreSQL specific
        )

def downgrade():
    # Revert the password_hash column back to its original length
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('password_hash',
            type_=sa.String(length=128),  # Revert back to original length
            existing_type=sa.String(length=256),
            postgresql_using='password_hash::varchar(128)'  # PostgreSQL specific
        )
