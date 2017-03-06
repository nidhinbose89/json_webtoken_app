"""empty message

Revision ID: c5c6dd870152
Revises: 
Create Date: 2017-01-12 17:30:28.122343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5c6dd870152'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('days',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('first_name', sa.String(length=80), nullable=False),
    sa.Column('last_name', sa.String(length=80), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('exercises',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('activity', sa.String(length=200), nullable=True),
    sa.Column('day_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['day_id'], ['days.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('exercises')
    op.drop_table('clients')
    op.drop_table('users')
    op.drop_table('plans')
    op.drop_table('days')
    # ### end Alembic commands ###