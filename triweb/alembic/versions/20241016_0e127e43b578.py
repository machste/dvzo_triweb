"""Add workday_user_polls table

Revision ID: 0e127e43b578
Revises: 260ba23a0b7f
Create Date: 2024-10-16 12:33:34.839904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e127e43b578'
down_revision = '260ba23a0b7f'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workday_user_polls',
    sa.Column('workday_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('state', sa.Text(), nullable=True),
    sa.Column('fixed', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_workday_user_polls_user_id_users')),
    sa.ForeignKeyConstraint(['workday_id'], ['workdays.id'], name=op.f('fk_workday_user_polls_workday_id_workdays')),
    sa.PrimaryKeyConstraint('workday_id', 'user_id', name=op.f('pk_workday_user_polls'))
    )
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workday_user_polls')
    # ### end Alembic commands ###
