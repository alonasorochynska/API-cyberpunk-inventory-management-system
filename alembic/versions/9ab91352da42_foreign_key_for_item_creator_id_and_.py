"""Foreign key for Item creator_id and owner_id

Revision ID: 9ab91352da42
Revises: 25a5b2b5116f
Create Date: 2024-09-21 22:20:41.762603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ab91352da42'
down_revision: Union[str, None] = '25a5b2b5116f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
