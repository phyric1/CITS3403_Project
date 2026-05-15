"""merge migration heads

Revision ID: 558cd6f7f52c
Revises: 0b74f35ca467, fb1e318a05ad
Create Date: 2026-05-15 22:13:33.294649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '558cd6f7f52c'
down_revision = ('0b74f35ca467', 'fb1e318a05ad')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
