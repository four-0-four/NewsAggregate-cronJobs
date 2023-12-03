"""added language and locations

Revision ID: fec90aef0ff4
Revises: 
Create Date: 2023-12-02 21:46:03.978885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fec90aef0ff4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('__EFMigrationsHistory')
    op.drop_table('EmailSubscriptions')
    op.drop_index('ix_newsletter_email', table_name='newsletter')
    op.drop_index('ix_newsletter_id', table_name='newsletter')
    op.drop_table('newsletter')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('newsletter',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_newsletter_id', 'newsletter', ['id'], unique=False)
    op.create_index('ix_newsletter_email', 'newsletter', ['email'], unique=False)
    op.create_table('EmailSubscriptions',
    sa.Column('Id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('Email', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_0900_ai_ci'), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_table('__EFMigrationsHistory',
    sa.Column('MigrationId', mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=150), nullable=False),
    sa.Column('ProductVersion', mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=32), nullable=False),
    sa.PrimaryKeyConstraint('MigrationId')
    )
    # ### end Alembic commands ###
