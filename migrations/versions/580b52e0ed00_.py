"""empty message

Revision ID: 580b52e0ed00
Revises: b6e94a32b09e
Create Date: 2023-01-11 01:46:59.910338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '580b52e0ed00'
down_revision = 'b6e94a32b09e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Poster_id', sa.Integer(), nullable=True))
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=500),
               existing_nullable=False)
        batch_op.alter_column('slug',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=500),
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'account', ['Poster_id'], ['id'])
        batch_op.drop_column('author')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('slug',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('title',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
        batch_op.drop_column('Poster_id')

    # ### end Alembic commands ###
