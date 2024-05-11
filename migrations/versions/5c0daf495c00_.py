"""empty message

Revision ID: 5c0daf495c00
Revises: 01daa67d54c1
Create Date: 2024-05-10 23:11:28.364386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c0daf495c00'
down_revision = '01daa67d54c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shifts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('worker', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shifts', schema=None) as batch_op:
        batch_op.drop_column('worker')

    # ### end Alembic commands ###
