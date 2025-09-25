"""new models

Revision ID: a4cf3ae393f7
Revises: 613f17f0e165
Create Date: 2025-09-22 19:48:58.615193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4cf3ae393f7'
down_revision: Union[str, Sequence[str], None] = '613f17f0e165'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = sa.Enum('ADMIN', 'AUTHOR', 'USER', name='role_enum')

def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_favourites_book_id'), table_name='favourites')
    op.drop_index(op.f('ix_favourites_user_id'), table_name='favourites')
    op.drop_column('favourites', 'id')
    op.drop_index(op.f('ix_reviews_book_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_user_id'), table_name='reviews')
    op.drop_constraint(op.f('uq_review_user_book'), 'reviews', type_='unique')
    op.drop_column('reviews', 'id')

    role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'users',
        sa.Column('role', role_enum, nullable=False, server_default='USER')
    )

    op.drop_constraint(op.f('users_role_id_fkey'), 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')


def downgrade() -> None:
    """Downgrade schema."""
    # вернём role_id и связь
    op.add_column('users', sa.Column('role_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('users_role_id_fkey'), 'users', 'roles', ['role_id'], ['id'], ondelete='SET NULL')
    op.drop_column('users', 'role')

    role_enum.drop(op.get_bind(), checkfirst=True)

    op.add_column(
        'reviews',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False)
    )
    op.create_unique_constraint(op.f('uq_review_user_book'), 'reviews', ['user_id', 'book_id'], postgresql_nulls_not_distinct=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)
    op.create_index(op.f('ix_reviews_book_id'), 'reviews', ['book_id'], unique=False)
    op.add_column(
        'favourites',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False)
    )
    op.create_index(op.f('ix_favourites_user_id'), 'favourites', ['user_id'], unique=False)
    op.create_index(op.f('ix_favourites_book_id'), 'favourites', ['book_id'], unique=False)
