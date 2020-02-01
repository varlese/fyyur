#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
import sys, traceback
from utils import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

# Models need to be imported after app is set up for migrations.
from models import *
from forms import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

# Show venues list

@app.route('/venues')
def venues():
  # TODO: num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  locales = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for locale in locales:
    data.append({
      'city': locale[0],
      'state': locale[1],
      'venues': Venue.query.filter_by(city=locale[0], state=locale[1]).all(),
      })
  return render_template('pages/venues.html', areas=data);

# Venues search

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
    'count': len(data),
    'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

# Show venue page

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    return render_template('pages/show_venue.html', venue=venue, venue_edit_link = url_for('edit_venue', venue_id=venue_id))
  else:
    abort(404)

# Add a new venue

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue_data = {
    'name': request.form.get('name'),
    'city': request.form.get('city'),
    'state': request.form.get('state'),
    'address': request.form.get('address'),
    'phone': request.form.get('phone'),
    'genres': request.form.get('genres'),
    'image_link': request.form.get('image_link'),
    'website': request.form.get('website'),
    'facebook_link': request.form.get('facebook_link'),
    'seeking_talent': request.form.get('seeking_talent'),
    'seeking_description': request.form.get('seeking_description')
  }
  
  error = False
  body = {}
  try:
    genres = []
    for genre in venue_data['genres']:
      genres.append( Genre.query.get( genre ) )

    venue = Venue(
      name = venue_data['name'],
      slug = slugify(venue_data['name']),
      city = venue_data['city'],
      state = venue_data['state'],
      address = venue_data['address'],
      phone = venue_data['phone'],
      genres = genres,
      image_link = venue_data['image_link'],
      website = venue_data['website'],
      facebook_link = venue_data['facebook_link'],
      seeking_talent = bool(venue_data['seeking_talent'])
    )
    db.session.add(venue)
    db.session.commit()
    body['id'] = venue.id
  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

  finally:
    db.session.close()
  if not error:
    flash('Venue ' + venue_data['name'] + ' was successfully added!')
    return redirect(url_for('show_venue', venue_id=int(body['id'])))
  else:
    flash('An error occurred. Venue ' + venue_data['name'] + ' could not be created.')
    abort(500)

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

# Edit a venue

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  genres = []
  for genre in venue.genres:
    genres.append(genre)
  form.genres.data = genres
  return render_template(
    'forms/edit_venue.html',
    form=form,
    venue=venue,
    delete_venue_link = url_for('delete_venue', venue_id=venue_id)
  )

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  try:
    genres = []
    for genre in form.genres.data:
      genres.append( Genre.query.get( genre ) )

    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.slug = slugify(venue.name)
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = genres
    venue.image_link = form.image_link.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    abort(500)

  return redirect(url_for('show_venue', venue_id=venue_id))

# Delete a venue

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id)
    venue.genres = []
    venue.delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

  finally:
    db.session.close()

  return redirect(url_for('venues'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

# Show artists list

@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

# Search artists

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

# Show artist page

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    return render_template('pages/show_artist.html', artist=artist, artist_edit_link = url_for('edit_artist', artist_id=artist_id))
  else:
    abort(404)

# Add a new artist

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist_data = {
    'name': request.form.get('name'),
    'city': request.form.get('city'),
    'state': request.form.get('state'),
    'address': request.form.get('address'),
    'phone': request.form.get('phone'),
    'genres': request.form.get('genres'),
    'image_link': request.form.get('image_link'),
    'website': request.form.get('website'),
    'facebook_link': request.form.get('facebook_link'),
    'seeking_venues': request.form.get('seeking_venues'),
    'seeking_description': request.form.get('seeking_description')
  }
  
  error = False
  body = {}
  try:
    genres = []
    for genre in artist_data['genres']:
      genres.append( Genre.query.get( genre ) )

    artist = Artist(
      name = artist_data['name'],
      slug = slugify(artist_data['name']),
      city = artist_data['city'],
      state = artist_data['state'],
      phone = artist_data['phone'],
      genres = genres,
      image_link = artist_data['image_link'],
      website = artist_data['website'],
      facebook_link = artist_data['facebook_link'],
      seeking_venues = bool(artist_data['seeking_venues']),
      seeking_description = artist_data['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
    body['id'] = artist.id
  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_artist', artist_id=int(body['id'])))
  else:
    abort(500)

  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

# Edit artist 

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  genres = []
  for genre in artist.genres:
    genres.append(genre.id)
  form.genres.data = genres
  return render_template(
    'forms/edit_artist.html',
    form=form,
    artist=artist,
    delete_artist_link = url_for('delete_artist', artist_id=artist_id)
  )

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):  
  error = False
  form = ArtistForm(request.form)
  try:
    genres = []
    for genre in form.genres.data:
      genres.append( Genre.query.get( genre ) )

    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.slug = slugify(artist.name)
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = genres
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venues = form.seeking_venues.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    abort(500)

  return redirect(url_for('show_artist', artist_id=artist_id))

# Delete an artist

@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.filter_by(id=artist_id)
    artist.genres = []
    artist.delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

  finally:
    db.session.close()

  return redirect(url_for('artists'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
