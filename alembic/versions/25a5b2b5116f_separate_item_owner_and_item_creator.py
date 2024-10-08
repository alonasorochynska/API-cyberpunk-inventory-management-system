"""Separate Item owner and Item creator

Revision ID: 25a5b2b5116f
Revises: 5345ff63cde6
Create Date: 2024-09-21 22:04:31.140047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25a5b2b5116f'
down_revision: Union[str, None] = '5345ff63cde6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('creator_id', sa.Integer(), nullable=False))
    op.alter_column('items', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'items', 'users', ['creator_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'items', type_='foreignkey')
    op.alter_column('items', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('items', 'creator_id')
    # ### end Alembic commands ###
