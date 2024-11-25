"""Newsletter subscription added

Revision ID: 101f7e1667ae
Revises: edbd67ce0f40
Create Date: 2024-11-25 16:32:44.235837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '101f7e1667ae'
down_revision = 'edbd67ce0f40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('newsletter_subscribers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('subscribed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('newsletter_subscribers')
    # ### end Alembic commands ###
