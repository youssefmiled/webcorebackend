"""add fk user_id to websites

Revision ID: be6c27b43138
Revises: 04b6f7c576bb
Create Date: 2026-03-20 19:35:53.810491

"""
from alembic import op
import sqlalchemy as sa


revision = 'be6c27b43138'
down_revision = '04b6f7c576bb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM websites WHERE user_id IS NULL")

    with op.batch_alter_table('websites', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key('fk_websites_user_id', 'users', ['user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('websites', schema=None) as batch_op:
        batch_op.drop_constraint('fk_websites_user_id', type_='foreignkey')
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)