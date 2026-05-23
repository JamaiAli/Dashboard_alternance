"""add_location_and_is_flagged

Revision ID: c8b9d3ef123a
Revises: 7b9aa0e8edb3
Create Date: 2026-05-23 15:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8b9d3ef123a'
down_revision: Union[str, Sequence[str], None] = '7b9aa0e8edb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('applications', sa.Column('location', sa.String(), nullable=True))
    op.add_column('applications', sa.Column('is_flagged', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    op.drop_column('applications', 'is_flagged')
    op.drop_column('applications', 'location')
