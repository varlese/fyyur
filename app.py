#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import babel
import datetime
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
import json
from sqlalchemy.sql import exists
import logging
from logging import Formatter, FileHandler
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
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
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
  data = []
  locales = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for locale in locales:
    data.append({
      'city': locale[0],
      'state': locale[1],
      'venues': Venue.query.filter_by(city = locale[0], state = locale[1]).all(),
      })
  return render_template('pages/venues.html', areas = data);

# Implement venues search

@app.route('/venues/search', methods = ['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
    'count': len(data),
    'data': data
  }
  return render_template('pages/search_venues.html', results = response, search_term = search_term)

# Show venue page

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))
  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), venue.shows))

  past_shows = list(map(lambda x: x.with_artist(), past_shows))
  upcoming_shows = list(map(lambda x: x.with_artist(), upcoming_shows))

  data = venue.to_dict()
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)

  if venue:
    return render_template(
      'pages/show_venue.html',
      venue = data,
      venue_edit_link = url_for('edit_venue', venue_id = venue_id)
    )
  else:
    abort(404)

# Add a new venue

@app.route('/venues/create', methods = ['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form = form)

@app.route('/venues/create', methods = ['POST'])
def create_venue_submission():
  error = False
  venue_id = 0
  form = VenueForm(request.form)

  if not form.validate():
    flash(form.errors)
    return redirect(url_for(['create_venue_submission']))

  try:
    genres = []
    for genre in form.genres.data:
      genres.append( Genre.query.get( genre ) )

    venue = Venue(
      name = form.name.data,
      slug = slugify(form.name.data),
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = genres,
      image_link = form.image_link.data,
      website = form.website.data,
      facebook_link = form.facebook_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(venue)
    db.session.commit()
    venue_id = venue.id

  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  if not error:
    flash('Venue ' + form.name.data + ' was successfully added!')
    return redirect(url_for('show_venue', venue_id = venue_id))

  else:
    flash('An error occurred. Venue ' + form.name.data + ' could not be created.')
    abort(500)

  return render_template('pages/home.html')

# Edit an existing venue

@app.route('/venues/<int:venue_id>/edit', methods = ['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  genres = []
  for genre in venue.genres:
    genres.append(genre)
  form.genres.data = genres
  return render_template(
    'forms/edit_venue.html',
    form = form,
    venue = venue,
    delete_venue_link = url_for('delete_venue', venue_id = venue_id)
  )

@app.route('/venues/<int:venue_id>/edit', methods = ['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  try:
    genres = []
    for genre in form.genres.data:
      genres.append( Genre.query.get( genre ))

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
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  if not error:
    return redirect(url_for('show_venue', venue_id = venue_id))

  else:
    abort(500)

  return redirect(url_for('show_venue', venue_id = venue_id))

# Delete a venue

@app.route('/venues/<venue_id>/delete', methods = ['GET'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(id = venue_id)
    venue.genres = []
    venue.delete()
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  return redirect(url_for('venues'))

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

# Show artists list

@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists = data)

# Search artists

@app.route('/artists/search', methods = ['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results = response, search_term = search_term)

# Show artist page

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows))
  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), artist.shows))

  past_shows = list(map(lambda x: x.with_venue(), past_shows))
  upcoming_shows = list(map(lambda x: x.with_venue(), upcoming_shows))

  data = artist.to_dict()
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)

  if artist:
    return render_template(
      'pages/show_artist.html',
      artist = data,
      artist_edit_link = url_for('edit_artist', artist_id = artist_id)
    )
  else:
    abort(404)

# Add a new artist

@app.route('/artists/create', methods = ['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form = form)

@app.route('/artists/create', methods = ['POST'])
def create_artist_submission():
  error = False
  artist_id = 0
  print( request.form )
  form = ArtistForm(request.form)
  print( form.genres.data )

  if not form.validate():
    flash(form.errors)
    return redirect(url_for(['create_artist_submission']))
  try:
    genres = []
    for genre in form.genres.data:
      genres.append( Genre.query.get( genre ) )

    artist = Artist(
      name = form.name.data,
      slug = slugify(form.name.data),
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = genres,
      image_link = form.image_link.data,
      website = form.website.data,
      facebook_link = form.facebook_link.data,
      seeking_venues = form.seeking_venues.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
    artist_id = artist.id

  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully created!')
    return redirect(url_for('show_artist', artist_id = artist_id))

  else:
    flash('An error occurred. ' + form.name.data + ' could not be added.')
    abort(500)

  return render_template('pages/home.html')

# Edit an existing artist 

@app.route('/artists/<int:artist_id>/edit', methods = ['GET'])
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
    delete_artist_link = url_for('delete_artist', artist_id = artist_id)
  )

@app.route('/artists/<int:artist_id>/edit', methods = ['POST'])
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
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  if not error:
    return redirect(url_for('show_artist', artist_id = artist_id))

  else:
    abort(500)

  return redirect(url_for('show_artist', artist_id = artist_id))

# Delete an artist

@app.route('/artists/<artist_id>/delete', methods = ['GET'])
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
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  return redirect(url_for('artists'))

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  shows = Show.query.filter(Show.start_time >= today).all()
  data = []
  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows = data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form = form)

@app.route('/shows/create', methods = ['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    exc_type, exc_value, exc_traceback = sys.exc_info()

    print("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit = 2, file = sys.stdout)

  finally:
    db.session.close()

  if not error:
    flash('Show was successfully listed!')

  else:
    flash('An error occurred. Show could not be listed.')
    abort(500)

  return redirect(url_for('shows'))

#----------------------------------------------------------------------------#
# Error handlers
#----------------------------------------------------------------------------#

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
