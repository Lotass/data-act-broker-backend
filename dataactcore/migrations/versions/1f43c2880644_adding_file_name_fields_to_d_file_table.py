"""adding file name fields to d file table

Revision ID: 1f43c2880644
Revises: 6f5c2c66b328
Create Date: 2016-08-02 19:57:57.561765

"""

# revision identifiers, used by Alembic.
revision = '1f43c2880644'
down_revision = '6f5c2c66b328'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_data_broker():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('d_file_metadata', sa.Column('original_file_name', sa.Text(), nullable=True))
    op.add_column('d_file_metadata', sa.Column('upload_file_name', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade_data_broker():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('d_file_metadata', 'upload_file_name')
    op.drop_column('d_file_metadata', 'original_file_name')
    ### end Alembic commands ###

