"""rename description to details:

Revision ID: 5d7f51c4530b
Revises: 93a5f419bc6e
Create Date: 2026-10-08 19:48:44.223225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d7f51c4530b'
down_revision: Union[str, Sequence[str], None] = '93a5f419bc6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("tasks", "description", new_column_name="details")


def downgrade() -> None:
    op.alter_column("tasks", "details", new_column_name="description")