"""init

Revision ID: 8e4da284e0d0
Revises: 
Create Date: 2024-07-18 20:35:33.771407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e4da284e0d0'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('firstname', sa.Text(), nullable=False),
    sa.Column('lastname', sa.Text(), nullable=True),
    sa.Column('passwd_hash', sa.Text(), nullable=True),
    sa.Column('role', sa.Text(), server_default='basic', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###