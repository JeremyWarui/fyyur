#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues',
                            lazy=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venue ID {self.id}, {self.name}, {self.city}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists',
                            lazy=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venue ID {self.id}, {self.name}, {self.city}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)

    def __repr__(self):
        return f"<Show ID {self.id}, {self.venue_id}, {self.artist_id}>"
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    results = Venue.query.distinct(Venue.city, Venue.state).all()
    print(results)

    for result in results:
        venue_obj = {
            'city': result.city,
            'state': result.state
        }

        venue_names = []

        venues = Venue.query.filter_by(
            city=result.city, state=result.state).all()

        for venue in venues:
            venue_names.append({
                'id': venue.id,
                'name': venue.name,
                "num_new_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })

        venue_obj['venues'] = venue_names

        data.append(venue_obj)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

    search_term = request.form.get('search_term')

    response = {}
    response['data'] = []

    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response['count'] = len(venues)

    for venue in venues:
        data_obj = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
        }
        response['data'].append(data_obj)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    print(venue)

    old_shows = list(filter(lambda show: show.start_time <
                     datetime.now(), venue.shows))

    pastshows = []

    for show in old_shows:
        pastshows.append({
            'artist_id': show.artists.id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': format_datetime(str(show.start_time))
        })

    upcoming_shows = list(
        filter(lambda show: show.start_time > datetime.now(), venue.shows))

    newshows = []

    for show in upcoming_shows:
        newshows.append({
            'artist_id': show.artists.id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': format_datetime(str(show.start_time))
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": pastshows,
        "upcoming_shows": newshows,
        "past_shows_count": len(pastshows),
        "upcoming_shows_count": len(newshows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)

    if form.validate():

        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=",".join(form.genres.data),  # convert to list
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                website=form.website_link.data
            )

            # add to the database
            db.session.add(new_venue)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                'Venue ' + request.form['name'] + ' was successfully listed!')

        except Exception:

            db.session.rollback()
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        print(" ", form.errors)
        flash("An error occured. Venue" +
              request.form['name'] + "could not be listed")

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        # venuename = venue['name']
        db.session.delete(venue)
        db.session.commit()

        flash('Venue' + venue.name + 'was successfully deleted!')
    except:
        db.session.rollback()
        print(sys.exe_info())
        flash("Venue was not successfully deleted")
    finally:
        db.session.close()
    return redirect(url_for('index'))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []

    artists = Artist.query.all()

    for artist in artists:
        data.append({
            'id': artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')

    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    response = {
        'count': len(artists),
        'data': []
    }

    for artist in artists:

        data_obj = {
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(list(filter(lambda show: show.start_time > datetime.now(), artist.shows)))
        }

        response['data'].append(data_obj)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    # artist['genres'] = artist.genres.split(",")

    # upcoming shows
    upcoming_shows = list(
        filter(lambda show: show.start_time > datetime.now(), artist.shows))

    # upcomingshows(no)
    upcoming = []

    for show in upcoming_shows:
        upcoming.append({
            'venue_id': show.venue_id,
            'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
            'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
            'start_time': format_datetime(str(show.start_time))
        })

    # pastshows(NO)
    past_shows = list(filter(lambda show: show.start_time <
                      datetime.now(), artist.shows))

    past = []
    for show in past_shows:
        past.append({
            'venue_id': show.venue_id,
            'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
            'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
            'start_time': format_datetime(str(show.start_time))
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }

    print(data)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    form.genres.data = artist.genres.split(',')

    # form.id.data = artist.id
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    if form.validate():

        try:
            artist = Artist.query.get(artist_id)

            artist.name = form.name.data,
            artist.city = form.city.data,
            artist.state = form.state.data,
            artist.phone = form.phone.data,
            artist.genres = ",".join(form.genres.data),  # convert to list
            artist.facebook_link = form.facebook_link.data,
            artist.image_link = form.image_link.data,
            artist.seeking_venue = True if form.seeking_venue.data else False
            artist.seeking_description = form.seeking_description.data,
            artist.website = form.website_link.data

            # add to the database
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                'Artist ' + form.name.data + ' was successfully updated!')

        except Exception:

            db.session.rollback()
            flash('Artist ' +
                  request.form['name'] + ' could not be updated.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        print(" ", form.errors)
        flash("Artist " +
              request.form['name'] + "could not be updated")

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    form = VenueForm()

    venue = Venue.query.get(venue_id)
    form.genres.data = venue.genres.split(',')  # to array

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    if form.validate():

        try:
            venue = Venue.query.get(venue_id)

            venue.name = form.name.data,
            venue.city = form.city.data,
            venue.state = form.state.data,
            venue.address = form.address.data,
            venue.phone = form.phone.data,
            venue.genres = ",".join(form.genres.data),  # convert to list
            venue.facebook_link = form.facebook_link.data,
            venue.image_link = form.image_link.data,
            venue.seeking_talent = True if form.seeking_talent.data else False
            venue.seeking_description = form.seeking_description.data,
            venue.website = form.website_link.data

            # add to the database
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                'Venue ' + form.name.data + ' was successfully updated!')

        except Exception:

            db.session.rollback()
            flash('Venue ' +
                  request.form['name'] + ' could not be updated.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        print(" ", form.errors)
        flash("Venue" +
              request.form['name'] + "could not be updated")

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)

    if form.validate():

        try:
            new_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=",".join(form.genres.data),  # convert to list
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                website=form.website_link.data
            )

            # add to the database
            db.session.add(new_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                'Venue ' + request.form['name'] + ' was successfully listed!')

        except Exception:

            db.session.rollback()
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        print(" ", form.errors)
        flash("An error occured. Venue" +
              request.form['name'] + "could not be listed")

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]

    data = []

    shows = Show.query.all()

    for show in shows:
        data.append({
            "venue_id": show.venues.id,
            "venue_name": show.venues.name,
            "artist_id": show.artists.id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

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
    form = ShowForm(request.form)

    if form.validate():

        try:
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )

            # add to the database
            db.session.add(new_show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')

        except Exception:

            db.session.rollback()
            flash('Show was not successfully added')
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        print(" ", form.errors)
        flash("An error occured. Show could not be listed")

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
