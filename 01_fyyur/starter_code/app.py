#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from zoneinfo import available_timezones
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database  -- done
migrate = Migrate(app, db)


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
    getting_avaliable_venues = db.session.query(
        Venue.state, Venue.city).group_by(Venue.state, Venue.city).all()
    data = []
    try:
        get_new_venue = ex_venue(getting_avaliable_venues, data)
        for venue in get_new_venue:
            data[-1]["venues"].append({"id": venue[0],
                                      "name": venue[1], })
            
    except:
        db.session.rollback()
        flash('Error Getting Area')
    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)

def ex_venue(getting_avaliable_venues, data):
    for existing_area in getting_avaliable_venues:
        get_new_venue = db.session.query(Venue.id, Venue.name, Venue.upcoming_shows_count).filter(
                Venue.state == existing_area[0], Venue.city == existing_area[1]).all()
        a_append(data, existing_area)
        
    return get_new_venue

def a_append(data, existing_area):
    data.append({
                "city": existing_area[0], "state": existing_area[1], "venues": []
            })


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    Venue_search_result, results_list = s_result()
    for venue in Venue_search_result:
        results_list["data"].append({"id": venue.id, "name": venue.name, })
    get_results_list = request.form.get('search_term')
    return render_template('pages/search_venues.html', results=results_list, search_term=get_results_list)

def s_result():
    Venue_search_result = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
    results_list = r_list(Venue_search_result)
    return Venue_search_result,results_list

def r_list(Venue_search_result):
    results_list = {"count": len(Venue_search_result), "data": []}
    return results_list


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows_query, upcoming_shows_query = s_query(venue_id)
    past_shows = []
    upcoming_shows = []
    s_shows(past_shows_query, upcoming_shows_query, past_shows, upcoming_shows)
    venue_data = {
        "id": venue.id, "name": venue.name, "genres": venue.genres, "address": venue.address, "city": venue.city,
        "state": venue.state, "phone": venue.phone, "website_link": venue.website_link, "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent, "seeking_description": venue.seeking_description, "image_link": venue.image_link,
        "past_shows": past_shows, "upcoming_shows": upcoming_shows, "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    data = list(filter(lambda d: d['id'] == venue_id, [venue_data]))[0]
    return render_template('pages/show_venue.html', venue=data)

def s_shows(past_shows_query, upcoming_shows_query, past_shows, upcoming_shows):
    for show in past_shows_query:
        p_shows(past_shows, show)
    for show in upcoming_shows_query:
        u_shows(upcoming_shows, show)

def u_shows(upcoming_shows, show):
    upcoming_shows.append(
            {"artist_id": show.artist_id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link,
             "start_time": str(show.start_time)}
        )

def p_shows(past_shows, show):
    past_shows.append(
            {"artist_id": show.artist_id,
             "artist_name": show.artist.name, "artist_image_link": show.artist.image_link, "start_time": str(show.start_time)}
        )

def s_query(venue_id):
    past_shows_query = Show.query.join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_query = Show.query.join(Venue).filter(
        Show.venue_id == venue_id).filter(Show. start_time > datetime.now()).all()
        
    return past_shows_query,upcoming_shows_query

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=('GET', 'POST'))
def create_venue_form():
    form = VenueForm()
    if form.validate_on_submit():
        if form.phone.data:
            return create_venue_submission()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    try:
        c_new_venue()
        db.session.commit()
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('Error' + request.form['name'] + 'could not be added')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')

def c_new_venue():
    db.session.add(Venue(name=request.form.get('name'), city=request.form.get('city'), state=request.form.get('state'),
                             address=request.form.get('address'), phone=request.form.get('phone'), image_link=request.form.get('image_link'),
                             facebook_link=request.form.get('facebook_link'), website_link=request.form.get('website_link'),
                             genres=request.form.getlist('genres'), seeking_description=request.form.get('seeking_description'),
                             seeking_talent=request.form.get('seeking_talent')
                             ))


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue_id = request.form.get('venue_id')
    del_venue, venueName = v_del(venue_id)
    try:
        db.session.delete(del_venue)
        db.session.commit()
        flash('Venue ' + venueName + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('please try again. Venue ' + venueName + ' could not be deleted.')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

def v_del(venue_id):
    del_venue = db.session.query(Venue).get(venue_id)
    venueName = del_venue.name
    return del_venue,venueName

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artist_search_result = db.session.query(Artist).filter(Artist.name.ilike(
        '%{}%'.format(request.form['search_term']))).all()

    artist_search_data = {
        "count": len(artist_search_result), "data": []
    }
    for artist in artist_search_result:
        artist_search_data['data'].append({
            "id": artist.id, "name": artist.name, "num_upcoming_shows": artist.upcoming_shows_count,
        })
    return render_template('pages/search_artists.html', results=artist_search_data, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    past_shows_query, upcoming_shows_query, past_shows, upcoming_shows = artist_shows(artist_id)
    try:
        view_artist(past_shows_query, upcoming_shows_query,
                    past_shows, upcoming_shows)
    except:
        db.session.rollback()
    finally:
        db.session.close()

    artist_data = a_data(artist, past_shows, upcoming_shows)
    data = list(filter(lambda d: d['id'] == artist_id, [artist_data]))[0]
    return render_template('pages/show_artist.html', artist=data)

def a_data(artist, past_shows, upcoming_shows):
    artist_data = {
        "id": artist.id, "name": artist.name, "genres": artist.genres, "city": artist.city, "state": artist.state,
        "phone": artist.phone, "website_link": artist.website_link, "facebook_link": artist.facebook_link, "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description, "image_link": artist.image_link, "past_shows": past_shows,
        "upcoming_shows": upcoming_shows, "past_shows_count": len(past_shows), "upcoming_shows_count": len(upcoming_shows)
    }
    
    return artist_data

def artist_shows(artist_id):
    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    past_shows = []
    upcoming_shows = []
    return past_shows_query,upcoming_shows_query,past_shows,upcoming_shows


def view_artist(past_shows_query, upcoming_shows_query, past_shows, upcoming_shows):
    p_query(past_shows_query, past_shows)
    up_query(upcoming_shows_query, upcoming_shows)

def up_query(upcoming_shows_query, upcoming_shows):
    for show in upcoming_shows_query:
        upcoming_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            }
        )

def p_query(past_shows_query, past_shows):
    for show in past_shows_query:
        past_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            }
        )


@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    deleted_artist, artistName = del_artist()
    try:
        db.session.delete(deleted_artist)
        db.session.commit()
        flash('Artist ' + artistName + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('please try again. Venue ' +
              artistName + ' could not be deleted.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

def del_artist():
    artist_id = request.form.get('artist_id')
    deleted_artist = Artist.query.get(artist_id)
    artistName = deleted_artist.name
    return deleted_artist,artistName
#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artists = Artist.query.get(artist_id)
    artist = {
        "id": artists.id, "name": artists.name, "genres": artists.genres, "city": artists.city, "state": artists.state,
        "phone": artists.phone, "website_link": artists.website_link, "facebook_link": artists.facebook_link,
        "seeking_venue": artists.seeking_venue, "seeking_description": artists.seeking_description, "image_link": artists.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    try:
        db.session.commit()
        flash("Artist {} is updated successfully".format(artist.name))
    except:
        db.session.rollback()
        flash("Artist {} isn't updated successfully".format(artist.name))
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venues = Venue.query.get(venue_id)
    venue = {
        "id": venues.id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website_link": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = request.form['seeking_talent']
    venue.seeking_description = request.form['seeking_description']
    try:
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=('GET', 'POST'))
def create_artist_form():
    form = ArtistForm()
    if form.validate_on_submit():
        phone = form.phone.data
        if phone:
            return create_artist_submission()
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    create_new_artist = Artist(
        name=request.form.get('name'), city=request.form.get('city'), state=request.form.get('state'),
        phone=request.form.get('phone'), image_link=request.form.get('image_link'), facebook_link=request.form.get('facebook_link'),
        website_link=request.form.get('website_link'), genres=request.form.getlist('genres'),
        seeking_description=request.form.get('seeking_description'), seeking_venue=request.form.get('seeking_venue')
    )
    try:
        # TODO: modify data to be the data object returned from db insertion
        db.session.add(create_new_artist)
        db.session.commit()
    # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
        flash('Error! Artist ' + request.form['name'] + ' could not be added')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    view_shows_data = Show.query.all()
    get_a_show = []
    show_data(view_shows_data, get_a_show)
    return render_template('pages/shows.html', shows=get_a_show)

def show_data(view_shows_data, get_a_show):
    for show in view_shows_data:
        all_data(get_a_show, show)

def all_data(get_a_show, show):
    get_a_show.append(
            {"venue_id": show.venue_id, "venue_name": show.venue.name, "artist_id": show.artist_id, "artist_name": show.artist.name,
             "artist_image_link": show.artist.image_link, "start_time": str(show.start_time)}
        )


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    if form.validate_on_submit():
        return create_show_submission()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    create_new_show = Show(artist_id=request.form.get('artist_id'), venue_id=request.form.get(
        'venue_id'), start_time=request.form.get('start_time'))
    try:
        db.session.add(create_new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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
