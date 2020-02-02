from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError
from wtforms.validators import DataRequired, AnyOf, URL
from models import *
from utils import *

# Set up genre validation
def validate_genres(form, field):
    if not field.data:
        raise ValidationError('Genre invalid.')
    for genre_value in field.data:
        if not Genre.query.get( genre_value ):
            raise ValidationError('Invalid genre choice!')

# Load genres from database for artist and venue forms

def get_genres_for_form():
    genre_choices = []
    for genre in Genre.query.all():
        genre_choices.append(( genre.id, genre.name ))
    return genre_choices

# Load artists from database for shows form

def get_artists_for_form():
    artist_choices = [
        ('', 'Select Artist')
    ]
    for artist in Artist.query.all():
        artist_choices.append(( artist.id, artist.name ))
    return artist_choices

# Load venues from database for shows form

def get_venues_for_form():
    venue_choices = [
        ('', 'Select Venue')
    ]
    for venue in Venue.query.all():
        venue_choices.append(( venue.id, venue.name ))
    return venue_choices

# Show form

class ShowForm(Form):
    artist_id = SelectField(
        'artist_id',
        validators = [DataRequired()],
        choices = get_artists_for_form()
    )

    venue_id = SelectField(
        'venue_id',
        validators = [DataRequired()],
        choices = get_venues_for_form()
    )

    start_time = DateTimeField(
        'start_time',
        validators = [DataRequired()],
        default = datetime.today()
    )

# Venue form

class VenueForm(Form):
    name = StringField(
        'name',
        validators = [DataRequired()]
    )

    city = StringField(
        'city',
        validators = [DataRequired()]
    )

    state = SelectField(
        'state',
        validators = [
            DataRequired(),
            AnyOf( [state.value for state in State] )
        ],
        choices = State.choices()
    )

    address = StringField(
        'address', validators=[DataRequired()]
    )

    phone = StringField(
        'phone'
    )

    image_link = StringField(
        'image_link'
    )

    genres = SelectMultipleField(
        'genres', 
        validators = [
            validate_genres
        ],
        coerce = int,
        choices = get_genres_for_form()
    )

    website = StringField(
        'website', validators = [URL()]
    )

    facebook_link = StringField(
        'facebook_link', validators = [URL()]
    )

    seeking_talent = BooleanField(
        'seeking_talent'
    )

    seeking_description = StringField(
        'seeking_description'
    )

# Artist form

class ArtistForm(Form):
    name = StringField(
        'name',
        validators = [DataRequired()]
    )

    city = StringField(
        'city', validators = [DataRequired()]
    )

    state = SelectField(
        'state',
        validators = [
            DataRequired(),
            AnyOf([state.value for state in State])
        ],
        choices = State.choices()
    )

    phone = StringField(
        'phone'
    )

    image_link = StringField(
        'image_link'
    )

    genres = SelectMultipleField(
        'genres', 
        validators = [
            validate_genres
        ],
        coerce = int,
        choices = get_genres_for_form()
    )

    website = StringField(
        'website', validators = [URL()]
    )

    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    seeking_venues = BooleanField(
        'seeking_venues'
    )

    seeking_description = StringField(
        'seeking_description'
    )