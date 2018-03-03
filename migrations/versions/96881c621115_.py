"""empty message

Revision ID: 96881c621115
Revises: 
Create Date: 2018-03-03 07:54:09.973733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96881c621115'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_username', table_name='users')
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    # ### end Alembic commands ###