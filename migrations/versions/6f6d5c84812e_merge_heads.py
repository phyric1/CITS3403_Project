"""merge heads

Revision ID: 6f6d5c84812e
Revises: 0b74f35ca467, 35784f1a0a98, 8701d957134e, fb1e318a05ad
Create Date: 2026-05-15 23:47:00.367647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f6d5c84812e'
down_revision = ('0b74f35ca467', '35784f1a0a98', '8701d957134e', 'fb1e318a05ad')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
