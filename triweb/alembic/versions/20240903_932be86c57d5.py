"""Add workdays table

Revision ID: 932be86c57d5
Revises: 1ec15c6a9203
Create Date: 2024-09-03 13:59:45.844150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '932be86c57d5'
down_revision = '1ec15c6a9203'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workdays',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('cook', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], name=op.f('fk_workdays_manager_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_workdays'))
    )
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workdays')
    # ### end Alembic commands ###