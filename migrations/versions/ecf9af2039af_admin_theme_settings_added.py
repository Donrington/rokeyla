"""admin theme settings added

Revision ID: ecf9af2039af
Revises: 3215ae1881d0
Create Date: 2024-11-18 23:32:36.076134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecf9af2039af'
down_revision = '3215ae1881d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.add_column(sa.Column('theme_preference', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.drop_column('theme_preference')

    # ### end Alembic commands ###