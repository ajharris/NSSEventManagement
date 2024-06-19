"""empty message

Revision ID: 5a75b2da5b71
Revises: a3f950fb2555
Create Date: 2024-06-19 13:43:45.513640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a75b2da5b71'
down_revision = 'a3f950fb2555'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('showName', sa.String(), nullable=True),
    sa.Column('showNumber', sa.Integer(), nullable=False),
    sa.Column('accountManager', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('showNumber')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    # ### end Alembic commands ###