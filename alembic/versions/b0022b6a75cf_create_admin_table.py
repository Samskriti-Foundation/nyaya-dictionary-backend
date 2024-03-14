"""Create Admin Table

Revision ID: b0022b6a75cf
Revises: 
Create Date: 2024-03-14 12:20:18.354395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'b0022b6a75cf'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'admins',
        sa.Column('email', sa.String(), nullable=False, primary_key=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String()),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )


def downgrade() -> None:
    op.drop_table("admins")
