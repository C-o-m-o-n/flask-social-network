"""empty message

Revision ID: 88d90ca5697d
Revises: f3c754905b9e
Create Date: 2023-01-13 12:48:40.212529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88d90ca5697d'
down_revision = 'f3c754905b9e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_comments_username_users'), 'users', ['username'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_comments_username_users'), type_='foreignkey')
        batch_op.drop_column('username')

    # ### end Alembic commands ###
