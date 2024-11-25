"""cancel request

Revision ID: f6f9354ebda5
Revises: f643ad82002b
Create Date: 2024-11-21 21:03:26.005264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6f9354ebda5'
down_revision = 'f643ad82002b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cancel_request', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('cancel_request')

    # ### end Alembic commands ###
