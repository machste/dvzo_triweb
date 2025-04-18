"""Support multiple vehicles per workday

Revision ID: 260ba23a0b7f
Revises: 6f342ee09ce3
Create Date: 2024-10-15 11:03:00.809427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '260ba23a0b7f'
down_revision = '6f342ee09ce3'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workday_vehicle_associations',
            sa.Column('workday_id', sa.Integer(), nullable=False),
            sa.Column('vehicle_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'],
                    name=op.f('fk_workday_vehicle_associations_vehicle_id_vehicles')
            ),
            sa.ForeignKeyConstraint(['workday_id'], ['workdays.id'],
                    name=op.f('fk_workday_vehicle_associations_workday_id_workdays')
            ),
            sa.PrimaryKeyConstraint('workday_id', 'vehicle_id',
                    name=op.f('pk_workday_vehicle_associations'))
    )
    with op.batch_alter_table('workdays') as batch_op:
        batch_op.drop_constraint(op.f('fk_workdays_vehicle_id_vehicles'),
                type_='foreignkey'
        )
        batch_op.drop_column('vehicle_id')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workdays') as batch_op:
        batch_op.add_column(
                sa.Column('vehicle_id', sa.INTEGER(), nullable=True)
        )
        batch_op.create_foreign_key(op.f('fk_workdays_vehicle_id_vehicles'),
                'vehicles', ['vehicle_id'], ['id']
        )
    op.drop_table('workday_vehicle_associations')
    # ### end Alembic commands ###
