"""Added bank account details.

Revision ID: 0c0c2110ae8b
Revises: bc1d6194ff58
Create Date: 2018-08-21 19:22:52.113441

"""

# revision identifiers, used by Alembic.
revision = '0c0c2110ae8b'
down_revision = 'bc1d6194ff58'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('bank', sqlalchemy_utils.types.encrypted.encrypted_type.EncryptedType(), nullable=True),
    sa.Column('clearing', sqlalchemy_utils.types.encrypted.encrypted_type.EncryptedType(), nullable=True),
    sa.Column('_number', sqlalchemy_utils.types.encrypted.encrypted_type.EncryptedType(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bank_accounts')
    # ### end Alembic commands ###
