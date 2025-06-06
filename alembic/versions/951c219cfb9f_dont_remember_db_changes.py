"""dont remember db changes

Revision ID: 951c219cfb9f
Revises: 76a85a955b1f
Create Date: 2025-05-31 20:21:14.332931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '951c219cfb9f'
down_revision: Union[str, None] = '76a85a955b1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('book_sale_info_ibfk_1', 'book_sale_info', type_='foreignkey')
    op.create_foreign_key(None, 'book_sale_info', 'books', ['book_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'book_sale_info', type_='foreignkey')
    op.create_foreign_key('book_sale_info_ibfk_1', 'book_sale_info', 'books', ['book_id'], ['id'])
    # ### end Alembic commands ###
