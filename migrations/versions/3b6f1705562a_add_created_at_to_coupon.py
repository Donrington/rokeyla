"""Add created_at to Coupon

Revision ID: 3b6f1705562a
Revises: 94a5dfaa113a
Create Date: 2024-11-23 14:35:12.928149

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3b6f1705562a'
down_revision = '94a5dfaa113a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_variants')
    with op.batch_alter_table('coupons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('coupons', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    op.create_table('product_variants',
    sa.Column('variant_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('product_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('size', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('color', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('stock_quantity', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], name='product_variants_ibfk_1'),
    sa.PrimaryKeyConstraint('variant_id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###