"""update card check constraints

Revision ID: 0a98877f4cc6
Revises: 153691204411
Create Date: 2026-05-11 01:51:16.561652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a98877f4cc6'
down_revision = '153691204411'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("card") as batch_op:
        batch_op.drop_constraint("check_max_in_deck_positive", type_="check")
    with op.batch_alter_table("card") as batch_op:
        batch_op.create_check_constraint("check_max_in_deck_positive", "max_in_deck >= -1")
        batch_op.create_check_constraint("check_uses_positive", "uses >= -1")


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""UPDATE card SET uses = 1 WHERE uses < 0"""))
    conn.execute(sa.text("""UPDATE card SET max_in_deck = 1 WHERE max_in_deck < 0""") )

    with op.batch_alter_table("card") as batch_op:
        batch_op.drop_constraint("check_max_in_deck_positive", type_="check")
        batch_op.drop_constraint("check_uses_positive", type_="check")
    with op.batch_alter_table("card") as batch_op:
        batch_op.create_check_constraint("check_max_in_deck_positive", "max_in_deck >= 0")
        batch_op.create_check_constraint("check_uses_positive", "uses >= 0")
