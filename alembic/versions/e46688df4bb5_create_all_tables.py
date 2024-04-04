"""create_all_tables

Revision ID: e46688df4bb5
Revises: 
Create Date: 2024-03-22 14:18:11.037417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from datetime import datetime, UTC


# revision identifiers, used by Alembic.
revision: str = 'e46688df4bb5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'db_managers',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('first_name', sa.String, nullable=False),
        sa.Column('last_name', sa.String),
        sa.Column('role', sa.Enum('superuser', 'admin', 'editor', name='role'), default='editor'),
        sa.Column('access_token', sa.Enum('READ_ONLY', 'READ_WRITE', 'READ_WRITE_MODIFY', 'ALL', name='access_token'), default='READ_ONLY'),
        sa.Column('created_at', sa.DateTime, default= lambda: datetime.now(UTC)),
    )

    op.create_table(
        'sanskrit_words',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word', sa.String, nullable=False),
        sa.Column('english_transliteration', sa.String, nullable=False, index=True),
    )

    op.create_table(
        'meanings',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning', sa.String, nullable=False),
    )

    op.create_table(
        'etymologies',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'),nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('etymology', sa.String, nullable=False),
    )

    op.create_table(
        'derivations',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('derivation', sa.String, nullable=False),
    )

    op.create_table(
        'translations',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('language', sa.String, nullable=False),
        sa.Column('translation', sa.String, nullable=False),
    )

    op.create_table(
        'examples',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('example_sentence', sa.String, nullable=False),
        sa.Column('applicable_modern_concept', sa.String, nullable=True),
    )

    op.create_table(
        'reference_nyaya_texts',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('source', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
    )

    op.create_table(
        'synonyms',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('synonym', sa.String, nullable=False),
    )

    op.create_table(
        'antonyms',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('sanskrit_word_id', sa.Integer, sa.ForeignKey('sanskrit_words.id'), nullable=False),
        sa.Column('meaning_id', sa.Integer, sa.ForeignKey('meanings.id'), nullable=False),
        sa.Column('antonym', sa.String, nullable=False),
    )

    op.create_table(
        'database_audits',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('table_name', sa.String, nullable=False),
        sa.Column('record_id', sa.Integer, nullable=False),
        sa.Column('operation', sa.String, nullable=False),
        sa.Column('db_manager_id', sa.Integer, sa.ForeignKey('db_managers.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.now(UTC)),
        sa.Column('new_value', sa.String, nullable=False),
    )

    op.create_table(
        'login_audits',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('db_manager_id', sa.Integer, sa.ForeignKey('db_managers.id'), nullable=False),
        sa.Column('ip_address', sa.String, nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.now(UTC)),
    )


def downgrade() -> None:
    op.drop_table("db_managers")
    op.drop_table("sanskrit_words")
    op.drop_table("etymologies")
    op.drop_table("derivations")
    op.drop_table("translations")
    op.drop_table("descriptions")
    op.drop_table("examples")
    op.drop_table("reference_nyaya_texts")
    op.drop_table("synonyms")
    op.drop_table("antonyms")
    op.drop_table("database_audits")
    op.drop_table("login_audits")