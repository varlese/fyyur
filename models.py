#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from app import app

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Genre database 

class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(), nullable = False)
  slug = db.Column(db.String(), unique = True, nullable = False)

# Creating relationship to connect Genre categories to Venue table
venue_genre_relationship = db.Table('venue_genre_relationship',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id')),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete = 'cascade')),
    db.Column('id', db.Integer, primary_key = True)
)

# Creating relationship to connect Genre categories to Artist table
artist_genre_relationship = db.Table('artist_genre_relationship',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete='cascade')),
    db.Column('id', db.Integer, primary_key = True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default = False)
    seeking_description = db.Column(db.String(500))
    slug = db.Column(db.String(120))
    genres = db.relationship(
      'Genre', 
      secondary = venue_genre_relationship,
      lazy = 'subquery',
      backref = db.backref('Venue', lazy = True)
    )
    shows = db.relationship(
      'Show',
      lazy = 'subquery',
      backref = db.backref('Venue', lazy=True)
    )
    def __repr__(self):
      return f"<Venue id='{self.id}' name='{self.name}'>"

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean(), default = False)
    seeking_description = db.Column(db.String(500))
    slug = db.Column(db.String(120))
    genres = db.relationship(
      'Genre', 
      secondary = artist_genre_relationship,
      lazy = 'subquery',
      backref = db.backref('Artist', lazy = True)
    )
    shows = db.relationship(
      'Show',
      lazy = 'subquery',
      backref = db.backref('Artist', lazy = True)
    )

# Creating Show database

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key = True)
  start_time = db.Column(db.DateTime, nullable = False)
  artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete = 'cascade'))
  venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete = 'cascade'))
  venue = db.relationship('Venue')
  artist = db.relationship('Artist')

  def with_venue(self):
    return {
      'venue_id': self.venue_id,
      'venue_name': self.venue.name,
      'venue_image_link': self.venue.image_link,
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }

  def with_artist(self):
    return {
      'artist_id': self.artist_id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    }