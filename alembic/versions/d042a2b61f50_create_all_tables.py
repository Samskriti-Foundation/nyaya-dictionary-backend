"""Create All Tables

Revision ID: d042a2b61f50
Revises: e46688df4bb5
Create Date: 2024-04-04 11:08:05.204641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd042a2b61f50'
down_revision: Union[str, None] = 'e46688df4bb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
