"""empty message

Revision ID: 8b159f5f16ff
Revises: 
Create Date: 2017-05-10 18:25:13.227947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b159f5f16ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dealership',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('code', sa.String(length=16), nullable=True),
    sa.Column('distance', sa.String(length=16), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('street', sa.String(length=128), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('zipcode', sa.String(length=12), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('vehicle',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vin', sa.String(length=32), nullable=True),
    sa.Column('stage', sa.String(length=32), nullable=True),
    sa.Column('sticker_url', sa.String(length=2048), nullable=True),
    sa.Column('vehicle_url', sa.String(length=2048), nullable=True),
    sa.Column('f_box_size', sa.String(length=32), nullable=True),
    sa.Column('f_cab_style', sa.String(length=32), nullable=True),
    sa.Column('f_drivetrain', sa.String(length=8), nullable=True),
    sa.Column('f_engine', sa.String(length=64), nullable=True),
    sa.Column('f_mpg', sa.String(length=32), nullable=True),
    sa.Column('f_package', sa.String(length=32), nullable=True),
    sa.Column('f_transmission', sa.String(length=256), nullable=True),
    sa.Column('dealership_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dealership_id'], ['dealership.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('vin')
    )
    op.create_table('price',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('msrp_adjusted', sa.Integer(), nullable=True),
    sa.Column('allx_adjusted', sa.Integer(), nullable=True),
    sa.Column('az_adjusted', sa.Integer(), nullable=True),
    sa.Column('az_applicable', sa.Boolean(), nullable=True),
    sa.Column('vehicle_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['vehicle_id'], ['vehicle.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('price')
    op.drop_table('vehicle')
    op.drop_table('dealership')
    # ### end Alembic commands ###
