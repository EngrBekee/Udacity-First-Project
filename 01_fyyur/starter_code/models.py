from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
  
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(),nullable=False)
    state = db.Column(db.String(),nullable=False)
    address = db.Column(db.String(),nullable=False)
    phone = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(),nullable=False)
    facebook_link = db.Column(db.String(),nullable=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate -- done
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    website_link = db.Column(db.String(),nullable=False)
    seeking_talent = db.Column(db.String(),nullable=True)
    seeking_description = db.Column(db.Text,nullable=True)
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show',backref='venue',lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(),nullable=False)
    state = db.Column(db.String(),nullable=False)
    phone = db.Column(db.String(), nullable=False)
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(),nullable=False)
    facebook_link = db.Column(db.String(),nullable=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(),nullable=False)
    seeking_venue = db.Column(db.String(),nullable=True)
    seeking_description = db.Column(db.Text,nullable=True)
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show',backref='artist',lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)