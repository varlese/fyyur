from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL
from models import *

# load genres from database for New Artist and New Venue forms

def get_genres_for_form():
    genre_choices = []
    for genre in Genre.query.all():
        genre_choices.append(( genre.id, genre.name ))
    return genre_choices

# load artists for show form

def get_artists_for_form():
    artist_choices = [
        ('', 'Select Artist')
    ]
    for artist in Artist.query.all():
        artist_choices.append(( artist.id, artist.name ))
    return artist_choices

# load venues for show form 

def get_venues_for_form():
    venue_choices = [
        ('', 'Select Venue')
    ]
    for venue in Venue.query.all():
        venue_choices.append(( venue.id, venue.name ))
    return venue_choices

class ShowForm(Form):
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        choices = get_artists_for_form()
    )
    venue_id = SelectField(
        'venue_id',
        validators=[DataRequired()],
        choices = get_venues_for_form()
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

# Venue form

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    # TODO implement validation logic for state
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
        validators=[DataRequired()],
        coerce=int,
        choices=get_genres_for_form()
    )
    website = StringField(
        'website', validators=[URL()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description'
    )

## Artist form

class ArtistForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )

    city = StringField(
        'city', validators=[DataRequired()]
    )

    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )

    # TODO implement validation logic for state
    phone = StringField(
        'phone'
    )

    image_link = StringField(
        'image_link'
    )

    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=get_genres_for_form()
    )

    website = StringField(
        'website', validators=[URL()]
    )

    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
    )

    seeking_venues = BooleanField(
        'seeking_venues'
    )

    seeking_description = StringField(
        'seeking_description'
    )
