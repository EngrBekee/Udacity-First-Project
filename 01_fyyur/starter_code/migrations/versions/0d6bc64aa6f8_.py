"""empty message

Revision ID: 0d6bc64aa6f8
Revises: ac3e37c6943a
Create Date: 2022-06-04 15:54:47.653432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d6bc64aa6f8'
down_revision = 'ac3e37c6943a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('genres', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('image_link', sa.String(), nullable=False),
    sa.Column('facebook_link', sa.String(), nullable=False),
    sa.Column('website_link', sa.String(), nullable=False),
    sa.Column('seeking_venue', sa.String(), nullable=True),
    sa.Column('seeking_description', sa.Text(), nullable=True),
    sa.Column('upcoming_shows_count', sa.Integer(), nullable=True),
    sa.Column('past_shows_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('venue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('image_link', sa.String(), nullable=False),
    sa.Column('facebook_link', sa.String(), nullable=False),
    sa.Column('genres', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('website_link', sa.String(), nullable=False),
    sa.Column('seeking_talent', sa.String(), nullable=True),
    sa.Column('seeking_description', sa.Text(), nullable=True),
    sa.Column('upcoming_shows_count', sa.Integer(), nullable=True),
    sa.Column('past_shows_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shows')
    op.drop_table('venue')
    op.drop_table('artist')
    # ### end Alembic commands ###