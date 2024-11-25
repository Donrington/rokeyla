"""empty message

Revision ID: 776a5c3e1a78
Revises: f7f792f382e1
Create Date: 2024-11-05 19:44:04.208290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '776a5c3e1a78'
down_revision = 'f7f792f382e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('facebook_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('google_id', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('google_id')
        batch_op.drop_column('facebook_id')

    # ### end Alembic commands ###
