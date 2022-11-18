from flask import Flask, request, render_template, g, redirect, Response, session
from sqlalchemy.pool import NullPool
from sqlalchemy import *
import os
from flask import Flask, redirect, url_for, request
from typing import ItemsView
import requests
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import spotipy.util as util
from flask_debugtoolbar import DebugToolbarExtension
from datetime import date
import sys

app = Flask(__name__)
client_id = "67bdc4b1d4d74f5d88cdab031fee6a41"
client_secret = "1a88af0b600d4ce3bf81c5191ae3aac0"
scopes = "playlist-read-private,user-read-private,user-read-email,user-library-read, playlist-modify-public"

external_ip = input("Enter the external IP so that the Spotify API can be configured:")
print("External IP: " + external_ip)
print("Enable this external IP on the Spotify dev console for the API to work!")

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""


tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.debug = True
app.secret_key = '648e2097fec28316b68b70c56305fdb7d2c07c82e4f00fce04e26ff0230eb3e4'


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
# DATABASEURI = "postgresql://alg2252:5368@34.75.94.195/proj1part2"
DATABASEURI = "postgresql://na2852:1353@34.75.94.195/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/', methods=["GET", "POST"])
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

    """
    tracks = []
    if request.method == 'POST':
        tracks = filter()

    playlist_options = []
    liked_by_options = []
    album_options = []
    artist_options = []
    mood_options = []
    genre_options = []
    new_playlist_options = []

    if 'username' in session:
        try:
            cursor = g.conn.execute(
                """SELECT DISTINCT E.id, E.name
      FROM existing_user_playlists E
      WHERE username=%s
      ORDER BY E.name
      """, session['username'])
            for result in cursor:
                # can also be accessed using result[0]
                playlist_options.append(
                    {'name': result['name'], 'id': result['id']})

            cursor = g.conn.execute(
                """
      SELECT DISTINCT F.display_name AS name, F.id
      FROM friends F, is_friends_with I
      WHERE I.username=%s AND F.id=I.friend_id
      ORDER BY F.display_name
      LIMIT 10
      """, session['username'])
            for result in cursor:
                # can also be accessed using result[0]
                liked_by_options.append(
                    {'name': result['name'], 'id': result['id']})

            # all albums associated with tracks on one of the user's existing playlists or Recommendations
            cursor = g.conn.execute(
                """
      SELECT DISTINCT A.name, A.id
      FROM Released_On R, Tracks T, Albums A, Saved_To S, existing_user_playlists E
      WHERE A.id=R.album_id AND R.track_id=S.track_id AND S.existing_playlist_id=E.id AND E.username=%s
      UNION
      SELECT DISTINCT A.name, A.id
      FROM Released_On R, Tracks T, Albums A, Added_To AD
      WHERE A.id=R.album_id AND
      AD.track_id=R.track_id AND AD.new_playlist_username=%s AND AD.new_playlist_name=%s AND AD.new_playlist_description=%s
      ORDER BY name
      LIMIT 150
      """, session['username'], session['username'], "Recommendations", "")
            for result in cursor:
                # can also be accessed using result[0]
                album_options.append(
                    {'name': result['name'], 'id': result['id']})

            # all artists associated with tracks on one of the user's existing playlists or Recommendations
            cursor = g.conn.execute(
                """
      SELECT DISTINCT A.name, A.id
      FROM Is_On I, Tracks T, Artists A, Saved_To S, existing_user_playlists E
      WHERE A.id=I.artist_id AND I.track_id=S.track_id AND S.existing_playlist_id=E.id
      AND E.username=%s
      UNION
      SELECT DISTINCT A.name, A.id
      FROM Is_On I, Tracks T, Artists A, Added_To AD
      WHERE A.id=I.artist_id AND AD.track_id=I.track_id AND AD.new_playlist_username=%s AND AD.new_playlist_name=%s AND AD.new_playlist_description=%s
      ORDER BY name
      LIMIT 400
      """, session['username'], session['username'], "Recommendations", "")
            for result in cursor:
                # can also be accessed using result[0]
                artist_options.append(
                    {'name': result['name'], 'id': result['id']})
            # all moods from this user
            cursor = g.conn.execute(
                """
      SELECT DISTINCT M.mood as name
      FROM assigned_Mood_To M
      WHERE M.username=%s
      UNION
      SELECT DISTINCT M.mood as name
      FROM assigned_Mood_To2 M
      WHERE M.username=%s
      ORDER BY name
      LIMIT 50
      """, session['username'], session['username'])
            for result in cursor:
                # can also be accessed using result[0]
                mood_options.append({'name': result['name']})

            # all genres from this user
            cursor = g.conn.execute(
                """
      SELECT DISTINCT I.genre
      FROM existing_user_playlists E, Saved_To S, Is_In I, Is_On O
      WHERE I.artist_id=O.artist_id AND O.track_id=S.track_id AND S.existing_playlist_id=E.id
      AND E.username=%s 
      UNION
      SELECT DISTINCT I.genre
      FROM Saved_To S, Is_In I, Is_On O, Added_To AD
      WHERE I.artist_id=O.artist_id AND AD.track_id=O.track_id AND AD.new_playlist_username=%s AND AD.new_playlist_name=%s AND AD.new_playlist_description=%s
      ORDER BY genre
      LIMIT 150
      """, session['username'], session['username'], "Recommendations", "")
            for result in cursor:
                # can also be accessed using result[0]
                genre_options.append({'name': result['genre']})

            # all new playlists
            cursor = g.conn.execute(
                """SELECT DISTINCT E.name, E.description
                FROM new_user_playlists E
                WHERE username=%s
                ORDER BY E.name
                """, session['username'])
            for result in cursor:
                # can also be accessed using result[0]
                new_playlist_options.append(
                    {'len': len(result['name']),'name': result['name'], 'description': result['description']})



            cursor.close()
        except Exception as e:
            print(e)
            return redirect("/logout")

    context = dict(genre_options=genre_options, tracks=tracks, liked_by_options=liked_by_options, mood_options=mood_options,
                   album_options=album_options, playlist_options=playlist_options, artist_options=artist_options,
                   new_playlist_options=new_playlist_options)

    return render_template("index.html", **context)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/recommendations', methods=["POST", "GET"])
def recommendations():
    moods = []
    tracks = set()
    recommendations = {}
    if request.method == 'POST':
        try:
            redirect_uri = "http://{}:8111/data-processing".format(external_ip)
            auth = spotipy.oauth2.SpotifyOAuth(cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(
                session), client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)
            session["access_token"] = auth.get_cached_token()["access_token"]
            session["refresh_token"] = auth.get_cached_token()["refresh_token"]
            sp = spotipy.Spotify(auth=session["access_token"])

        except Exception as e:
            print(e)
            return redirect("/logout")
        try:
            if "username" in session:
                # for each mood get tracks in database for it
                for mood in request.form.keys():
                    m = request.form[mood]
                    cursor = g.conn.execute(
                        """
                        SELECT DISTINCT T.id
                        FROM tracks T 
                        WHERE T.id = 
                        ANY(SELECT M.track_id 
                        FROM Assigned_Mood_To M 
                        WHERE M.mood=%s AND M.username=%s)
                        OR T.id = 
                        ANY(SELECT R.track_id 
                        FROM Released_On R, Albums A, Assigned_Mood_To2 M
                        WHERE R.album_id=A.id AND A.id=M.album_id AND M.mood=%s AND M.username=%s
                        )
                        LIMIT 10
                        """, m, session["username"], m, session["username"])
                    for result in cursor:
                        tracks.add(result["id"])
                # get recommendations for each track

                try:
                    recs = sp.recommendations(seed_tracks=tracks, limit=10)
                except Exception as e:
                    return redirect("/logout")

                if "tracks" in recs:
                    # add each track to new_playlist Recommendations
                    try:
                        g.conn.execute(
                            '''INSERT INTO New_User_Playlists (name, description, username, date_created) VALUES 
                            (%s, %s, %s, %s)''',
                            "Recommendations", "", session["username"], date.today().strftime("%Y-%m-%d"))
                    except Exception:  # may already exist
                        pass

                    for r in recs["tracks"]:
                        try:
                            try:
                                d = r["album"]["release_date"]
                                if len(d) == 4:
                                    d = d + "-01-01" 
                                g.conn.execute(
                                    '''INSERT INTO Tracks (id, name, popularity, duration, release_date) VALUES 
                        (%s, %s, %s, %s, %s)''',
                                    r["id"], r["name"], r["popularity"], r["duration_ms"], d)
                              
                                recommendations[r["id"]] = {
                                    "artist": [], "name": r["name"]}
                                for artist in r["artists"]:
                                    recommendations[r["id"]]["artist"].append(
                                        artist["name"])
                            except Exception as e:
                                print(e)
                            try:
                                g.conn.execute(
                                    '''INSERT INTO Added_To (track_id, new_playlist_name, new_playlist_description, new_playlist_username, date_added) VALUES 
                                (%s, %s, %s, %s, %s)''',
                                    r["id"], "Recommendations", "", session["username"], date.today().strftime("%Y-%m-%d"))
                            except Exception as e:
                                print(e)
                            
                            try:
                                # albums
                                if r["album"]["album_type"] == "album":
                                    g.conn.execute(
                                        '''INSERT INTO Albums (id, name, release_date) VALUES  
                                (%s, %s, %s)''',
                                        r["album"]["id"], r["album"]["name"], r["album"]["release_date"])
                            except Exception as e:
                                print(e)

                                # artists of track
                            for artist in r["artists"]:
                                artist_data = sp.artist(artist["id"])
                                try:
                                    # Artists
                                    g.conn.execute(
                                        '''INSERT INTO Artists (id, name, popularity) VALUES     
                            (%s, %s, %s)''', artist["id"], artist["name"], artist_data["popularity"])
                                except Exception as e:
                                    print(e)

                                try:
                                    collaboration = "FALSE"
                                    if len(r["artists"]) > 1:
                                        collaboration = "TRUE"

                                    g.conn.execute(
                                        '''INSERT INTO Is_On (artist_id, track_id, collaboration) VALUES  
                            (%s, %s, %s)''', artist["id"], r["id"], collaboration)
                                except Exception as e:
                                    print(e)

                                for genre in artist_data["genres"]:
                                    # Genres
                                    try:
                                        g.conn.execute(
                                            '''INSERT INTO Genres (genre) VALUES   
                                (%s)''', genre)
                                    except Exception as e:
                                        print(e)

                                    try:
                                        g.conn.execute(
                                            '''INSERT INTO Is_In (artist_id, genre) VALUES    
                                (%s, %s)''', artist["id"], genre)
                                    except Exception as e:
                                        print(e)

                                if r["album"]["album_type"] == "album":
                                    album_by_artist = "FALSE"

                                    for album_artist in r["album"]["artists"]:
                                        if album_artist["id"] == artist["id"]:
                                            album_by_artist = "TRUE"

                                    try:
                                        g.conn.execute(
                                            '''INSERT INTO released_on (artist_id, track_id, album_id, album_by_artist) VALUES  
                                (%s, %s, %s, %s)''', artist["id"], r["id"], r["album"]["id"], album_by_artist)
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
            else:
                return redirect("/logout")
        except Exception as e:
            print(e)
            return redirect("/")

    try:
        if "username" in session:
            # all moods from this user
            cursor = g.conn.execute(
                """
                    SELECT DISTINCT M.mood as name
                    FROM assigned_Mood_To M
                    WHERE M.username=%s
                    UNION
                    SELECT DISTINCT M.mood as name
                    FROM assigned_Mood_To2 M
                    WHERE M.username=%s
                    ORDER BY name
                    """, session['username'], session['username'])
            for result in cursor:
                moods.append(result["name"])
            context = dict(moods=moods, tracks=recommendations)
            return render_template('recommendations.html', **context)
        else:
            return redirect("/logout")
    except Exception as e:
        print(e)
        return redirect("/")


@app.route('/get-data')
def get_data():
    try:
        redirect_uri = "http://{}:8111/data-processing".format(external_ip)
        print(redirect_uri)
        auth = spotipy.oauth2.SpotifyOAuth(
            client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes, show_dialog=True)
    except Exception as e:
        print(e)
        return redirect("/logout")  
    return redirect(auth.get_authorize_url())


@app.route('/data-processing')
def data_processing():
    try:
        redirect_uri = "http://{}:8111/data-processing".format(external_ip)
        auth = spotipy.oauth2.SpotifyOAuth(cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(
            session), show_dialog=True, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)

        code = request.args.get("code")
        auth.get_access_token(code, as_dict=False)

        session["access_token"] = auth.get_cached_token()["access_token"]
        session["refresh_token"] = auth.get_cached_token()["refresh_token"]
    except Exception as e:
        print(e)
        return redirect("/logout")
    return redirect("/login")


@app.route('/fill-home')
def fill_home():  # put data from spotify into SQL
    try:
        redirect_uri = "http://{}:8111/data-processing".format(external_ip)
        auth = spotipy.oauth2.SpotifyOAuth(cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(
            session), client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)
        session["access_token"] = auth.get_cached_token()["access_token"] #internally checks if it's expired
        session["refresh_token"] = auth.get_cached_token()["refresh_token"]
        sp = spotipy.Spotify(auth=session["access_token"])
        
    except Exception:
        return redirect("/logout")

    try:
        playlist_info = sp.current_user_playlists(
            limit=2, offset=0)  # 2 to keep time manageable
    except Exception:
        return redirect("/get-data")

    try: 
        for item in playlist_info["items"]:

            playlist_data = sp.user_playlist(user=item["owner"]["id"],
                                            playlist_id=item["id"], fields="tracks,id,next,name,total")

            playlist = playlist_data["tracks"]

            try:
                g.conn.execute(
                    '''INSERT INTO Existing_User_Playlists (id, username, name, length) VALUES 
            (%s, %s, %s, %s)''',
                    playlist_data["id"], session["username"], playlist_data["name"], playlist['total'])
            except Exception as e:
                print(e)

            # added to limit download time. In the future, could be made more efficient by combining inserts.
            count = 0
            
            while playlist != None and count < 30:
                for track_info in playlist["items"]:
                    count = count + 1
                    track = track_info["track"]
                    
                    try:
                        try:
                            g.conn.execute(
                                '''INSERT INTO Tracks (id, name, popularity, duration, release_date) VALUES 
                    (%s, %s, %s, %s, %s)''',
                                track["id"], track["name"], track["popularity"], track["duration_ms"], track["album"]["release_date"])
                        except Exception as e:
                            print(e)

                        try:
                            g.conn.execute(
                                '''INSERT INTO Saved_To (track_id, existing_playlist_id, date_added) VALUES 
                    (%s, %s, %s)''',
                                track["id"], playlist_data["id"], track_info["added_at"][:10])
                        except Exception as e:
                            print(e)

                        try:
                            # albums
                            if track["album"]["album_type"] == "album":
                                g.conn.execute(
                                    '''INSERT INTO Albums (id, name, release_date) VALUES  
                            (%s, %s, %s)''',
                                    track["album"]["id"], track["album"]["name"], track["album"]["release_date"])
                        except Exception as e:
                            print(e)

                        try:
                            for artist in track["artists"]:

                                artist_data = sp.artist(artist["id"])
    
                                try:
                                    # Artists
                                    g.conn.execute(
                                        '''INSERT INTO Artists (id, name, popularity) VALUES     
                            (%s, %s, %s)''', artist["id"], artist["name"], artist_data["popularity"])
                                except Exception as e:
                                    print(e)

                                try:
                                    collaboration = "FALSE"
                                    if len(track["artists"]) > 1:
                                        collaboration = "TRUE"

                                    g.conn.execute(
                                        '''INSERT INTO Is_On (artist_id, track_id, collaboration) VALUES  
                            (%s, %s, %s)''', artist["id"], track["id"], collaboration)
                                except Exception as e:
                                    print(e)

                                for genre in artist_data["genres"]:
                                    # Genres
                                    try:
                                        g.conn.execute(
                                            '''INSERT INTO Genres (genre) VALUES   
                                (%s)''', genre)
                                    except Exception as e:
                                        print(e)

                                    try:
                                        g.conn.execute(
                                            '''INSERT INTO Is_In (artist_id, genre) VALUES    
                                (%s, %s)''', artist["id"], genre)
                                    except Exception as e:
                                        print(e)

                                if track["album"]["album_type"] == "album":
                                    album_by_artist = "FALSE"

                                    for album_artist in track["album"]["artists"]:
                                        if album_artist["id"] == artist["id"]:
                                            album_by_artist = "TRUE"

                                    try:
                                        g.conn.execute(
                                            '''INSERT INTO released_on (artist_id, track_id, album_id, album_by_artist) VALUES  
                                (%s, %s, %s, %s)''', artist["id"], track["id"], track["album"]["id"], album_by_artist)
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
                    except Exception as e:
                        print(e)

                    if count >= 30:
                        break
                if "next" in playlist:
                    playlist = sp.next(playlist)
                else:
                    playlist = None
    except Exception as e:
        print(e)
    return redirect("/")


@app.route('/add-friend', methods=["GET", "POST"])
def add_friend():
    try:
        if request.method == 'POST':

            if request.form["friend-id"] != "":
                try:
                    redirect_uri = "http://{}:8111/data-processing".format(external_ip)
                    auth = spotipy.oauth2.SpotifyOAuth(cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(
                        session), client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)
                    session["access_token"] = auth.get_cached_token()["access_token"] #internally checks if it's expired
                    session["refresh_token"] = auth.get_cached_token()["refresh_token"]
                    sp = spotipy.Spotify(auth=session["access_token"])
                    
                except Exception:
                    return redirect("/logout")
            
                user_info = sp.user(request.form["friend-id"])
                display_name = user_info["display_name"]
            
                #add friend to sql
                try:
                    g.conn.execute(
                    """INSERT INTO Friends (id, display_name) VALUES 
                    (%s, %s)""", request.form["friend-id"], display_name)
                except Exception as e:
                    print(e)

                #add is_friends_with to sql
                try:
                    g.conn.execute(
                    """INSERT INTO Is_Friends_With (friend_id, username) VALUES 
                    (%s, %s)""", request.form["friend-id"], session["username"])
                except Exception as e:
                    print(e)

                user_playlist_info = sp.user_playlists(request.form["friend-id"], limit=2)  # 5 max
                
                user_playlist_ids = []
                for item in user_playlist_info["items"]:
                    user_playlist_ids.append(item["uri"])
                
                # limit at 50 per playlist for speed
                # check if tracks in Tracks for user already, if so create Liked_By relationship
                user_tracks = set()
                
                for uri in user_playlist_ids:
                    friend_tracks = sp.user_playlist_tracks(
                        request.form["friend-id"], uri[17:], limit = 50)
                    
                    for item in friend_tracks["items"]:
                        user_tracks.add(item["track"]["id"])
                    
                
                #check if each track can be found in an existing_playlist or Recommendation related to the user
                #not checking every single song (no point in liking songs this user won't filter down to)
                #if they can be found, create LIKED_BY 
                liked_tracks=set()
                
                cursor = g.conn.execute(
                    """SELECT A.track_id AS id
                    FROM Added_To A 
                    WHERE A.new_playlist_username=%s AND A.new_playlist_name=%s AND A.new_playlist_description=%s
                    UNION 
                    SELECT S.track_id AS id
                    FROM Saved_To S, Existing_User_Playlists E
                    WHERE E.username=%s AND E.id=S.existing_playlist_id 
                    LIMIT 300
                    """, session['username'], "Recommendations", "", session['username'])

                #check if each track is also liked by the friend
                for result in cursor:
                    if result["id"] in user_tracks:
                        liked_tracks.add(result["id"])
                        print("match" + result["id"])

                for t in liked_tracks:
                    try:
                        g.conn.execute(
                            """INSERT INTO Liked_By (track_id, friend_id) VALUES 
                            (%s, %s)""",
                            t, request.form["friend-id"])
                    except Exception as e:
                        print(e)

                # do sql query on each track id to get track name and artists
                # 300 tracks max for reasonable response times
    except Exception as e:
        print(e)
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # make sql call to check if this username/password combo is in the database:
            try:
                
                cursor = g.conn.execute(
                    """SELECT DISTINCT U.username, U.password
        FROM Users U
        WHERE U.username=%s AND U.password=%s
        """, username, password)
                
                i = 0
                for result in cursor:
                    i = i + 1
                if i != 1:
                    # if it fails, go back to login page
                    return render_template("login.html")
            except Exception as e:
                print(e)
                return render_template("login.html")

            session['username'] = username
            return redirect('/')
    except Exception as e:
        print(e)
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # sql call to add this username/password combo to the database:
            try:
                cursor = g.conn.execute(
                    """INSERT INTO Users (username, password) VALUES (%s, %s)""", username, password)
            except:  # if it fails, show the register page again
                return render_template("register.html")
            return redirect('/')  # if it succeeds
    except Exception as e:
        print(e)
    return render_template("register.html")  # with "GET"


def filter():
    tracks = {}
    try:
        if "username" in session:
            requested = {"B": [], "L": [], "P": [], "R": [], "M": [], "G": []}
            results = []
            for option in request.form.keys():
                if option[0] in requested.keys():
                    requested[option[0]].append(request.form[option])
            # albums
            album_track_ids = set()
            for album in requested["B"]:
                cursor = g.conn.execute(
                    """
          SELECT R.track_id AS id
          FROM released_on R  
          WHERE R.album_id=%s
          """, album)
                update_set(album_track_ids, cursor)
            if len(requested["B"]) > 0:
                results.append(album_track_ids)

            # liked_by
            liked_by_track_ids = set()
            for friend in requested["L"]:
                cursor = g.conn.execute(
                    """
          SELECT L.track_id AS id
          FROM liked_by L  
          WHERE L.friend_id=%s
          """, friend)
                update_set(liked_by_track_ids, cursor)
            if len(requested["L"]) > 0:
                results.append(liked_by_track_ids)
            # playlists
            playlist_ids = set()
            for playlist in requested["P"]:
                cursor = g.conn.execute(
                    """
          SELECT S.track_id AS id
          FROM saved_to S, existing_user_playlists E  
          WHERE E.username=%s AND E.id = S.existing_playlist_id AND E.id=%s
          """, session['username'], playlist)
                update_set(playlist_ids, cursor)
            if len(requested["P"]) > 0:
                results.append(playlist_ids)
            # artists
            artist_track_ids = set()
            for artist in requested["R"]:
                cursor = g.conn.execute(
                    """
          SELECT I.track_id AS id
          FROM Is_On I  
          WHERE I.artist_id=%s
          """, artist)
                update_set(artist_track_ids, cursor)
            if len(requested["R"]) > 0:
                results.append(artist_track_ids)

            # moods
            mood_track_ids = set()
            
            for mood in requested["M"]:
                cursor = g.conn.execute(
                    """
          SELECT DISTINCT R.track_id AS id
          FROM Released_On R, Assigned_Mood_To2 M
          WHERE R.album_id=M.album_id AND M.username=%s AND M.mood=%s  
          UNION
          SELECT M.track_id
          FROM Assigned_mood_to M
          WHERE M.username=%s AND M.mood=%s
          """, session['username'], mood, session['username'], mood)
                update_set(mood_track_ids, cursor)
            if len(requested["M"]) > 0:
                results.append(mood_track_ids)
            
            # genres
            genre_track_ids = set()
            for genre in requested["G"]:
                cursor = g.conn.execute(
                    """
          SELECT O.track_id AS id
          FROM Is_In I, Is_On O
          WHERE I.genre=%s AND I.artist_id=O.artist_id
          """, genre)
                update_set(genre_track_ids, cursor)
            if len(requested["G"]) > 0:
                results.append(genre_track_ids)
         
            # find intersection of filters that had any selections
            track_ids = set()
           

            if len(results) > 0:
                track_ids = results.pop()
            for r in results:
                track_ids = track_ids.intersection(r)
            #popularity
           
            max_pop = 100
            min_pop = 0
            try:
                max_pop = int(request.form["max-popularity"])
            except Exception as e:
                print(e)
            try:
                min_pop = int(request.form["min-popularity"])
            except Exception as e:
                print(e)

            #duration
            max_dur = 2147483647 
            min_dur = 0
            try:
                max_dur = int(request.form["max-duration"])
            except Exception as e:
                print(e)
            try:
                min_dur = int(request.form["min-duration"])
            except Exception as e:
                print(e)

            # do sql query on each track id to get track name and artists
            # 200 tracks max for reasonable response times
            for id in track_ids:
                cursor = g.conn.execute(
                    """
        SELECT DISTINCT T.name, T.id, A.name AS artist, T.popularity, T.duration 
        FROM Is_On I, Artists A, tracks T
        WHERE T.id=%s AND I.artist_id=A.id AND T.id=I.track_id 
        AND T.popularity >= %s AND T.popularity <= %s
        AND T.duration >= %s AND T.duration <= %s
        LIMIT 200
        """, id, min_pop, max_pop, min_dur, max_dur)
                #update_tracks(cursor, tracks)
                cursor_copy = []
                result_count = 0
                for result in cursor:
                    result_count = result_count + 1
                    cursor_copy.append(result)
  
                if result_count == 0: #may have been missing an artist and was skipped
                    cursor = g.conn.execute(
                    """
                    SELECT DISTINCT T.name, T.id, T.popularity, T.duration 
                    FROM tracks T
                    WHERE T.id=%s
                    AND T.popularity >= %s AND T.popularity <= %s
                    AND T.duration >= %s AND T.duration <= %s
                    LIMIT 200
                    """, id, min_pop, max_pop, min_dur, max_dur)
                    update_tracks(cursor, tracks)
                else: 
                    update_tracks(cursor_copy, tracks)
        else:
            return redirect("/logout")
    except Exception as e:
        print(e)

    return tracks


def update_set(set, cursor):
    try:
        for result in cursor:
            set.add(result["id"])
    except Exception as e:
        print(e)


def update_tracks(cursor, tracks):
    try:
        for result in cursor:
            if "artist" in result:
                if result["id"] in tracks:
                    tracks[result["id"]]["artist"].append(result["artist"])
                else:
                    tracks[result["id"]] = {
                        'name': result['name'], 'artist': [result['artist']]}
            else:
                tracks[result["id"]] = {
                        'name': result['name'], 'artist': ["<Missing :(>"]}
            if "popularity" in result:
                tracks[result["id"]]["popularity"] = result["popularity"]
            if "duration" in result:
                tracks[result["id"]]["duration"] = result["duration"]
    except Exception as e:
        print(e)

@app.route('/create-new-playlist', methods=['POST'])
def new_playlist():
    try:
        name = request.form['playlist-name']
        description = request.form['playlist-description']
        g.conn.execute(
            """INSERT INTO New_User_Playlists (name, description, username, date_created) VALUES 
            (%s, %s, %s, %s)""", name, description, session["username"], date.today().strftime("%Y-%m-%d"))
    except Exception as e:
        print(e)
    return redirect('/')

# turn filtered tracks into new playlist
@app.route('/filtered-to-new-playlist', methods=['POST', 'GET'])
def filtered_to_playlist():

    if request.method == 'POST':
        try:
            if "username" in session:

                new_playlist = request.form['selected-new-playlist']

                if new_playlist != "":

                    pos_c = 1
                    len = 0
                    for c in new_playlist:

                        if c == ' ':
                            pos_c = new_playlist.index(' ')
                            len = int(new_playlist[:pos_c])
                            break


                    name = new_playlist[pos_c+1:pos_c+len+1]
                    description = new_playlist[pos_c+len+1:]


                    for key in request.form.keys():
                        if key[0] == 'T': #check if key is for a track
                            
                            track = request.form[key]
                                
                            # add each track to new_playlist
                            try:
                                g.conn.execute(
                                    '''INSERT INTO Added_To (track_id, new_playlist_name, new_playlist_description, new_playlist_username, date_added) VALUES 
                                    (%s, %s, %s, %s, %s)''', track, name, description, session["username"], date.today().strftime("%Y-%m-%d"))
                            except Exception as e:
                                print(e)
        except Exception as e:
            print(e)

    return redirect('/')

# add selected new playlist to spotify
@app.route('/new-playlist-to-spotify', methods=['POST', 'GET'])
def playlist_to_spotify():

    if request.method == 'POST':
        try:
            redirect_uri = "http://{}:8111/data-processing".format(external_ip)
            auth = spotipy.oauth2.SpotifyOAuth(cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(
                session), client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)
            session["access_token"] = auth.get_cached_token()["access_token"]
            session["refresh_token"] = auth.get_cached_token()["refresh_token"]
            sp = spotipy.Spotify(auth=session["access_token"])
            
        except Exception as e:
            print(e)
            return redirect("/logout")
    
        if "username" in session:
            try:
                new_playlist = request.form['new-spotify-playlist']

                pos_c = 1
                l = 0

                for c in new_playlist:
                    if c == ' ':
                        pos_c = new_playlist.index(' ')
                        l = int(new_playlist[:pos_c])
                        break

                name = new_playlist[pos_c+1:pos_c+l+1]
                desc = new_playlist[pos_c+l+1:]

                user_id = sp.me()["id"]

                new_playlist = sp.user_playlist_create(
                    user_id,
                    name, 
                    public = True,
                    description = desc)

                playlist_id = new_playlist["id"]

                tracks = set()

                cursor = g.conn.execute(
                    """SELECT A.track_id AS id
                    FROM Added_To A
                    WHERE A.new_playlist_username=%s AND A.new_playlist_name=%s AND A.new_playlist_description=%s
                    LIMIT 100""", 
                    session['username'], 
                    name, 
                    desc)
                update_set(tracks, cursor)

                #spotipy only takes max 100 songs, take first 100
                while len(tracks) > 100:
                    tracks.pop()
                    
                t = sp.user_playlist_add_tracks(
                    session['username'], 
                    playlist_id, 
                    tracks, 
                    position=None)
           
            except Exception as e:
                print(e)
                return redirect("/logout")
    return redirect('/')

# assign mood to filtered tracks
@app.route('/mood-to-filtered', methods=["POST", "GET"])
def add_mood_to_filtered():
    if request.method == 'POST':
        try:
            if "username" in session:
                sel_mood = ""
                if "selected-mood" in request.form:
                    sel_mood = request.form["selected-mood"]
                add_mood = request.form["added-mood"]
                if add_mood != "":
                    sel_mood = add_mood
                # get album mood
                for key in request.form.keys():
                    if key[0] == 'T': #check if key is for a track

                        track = request.form[key]
                        try:              
                            g.conn.execute(
                            '''INSERT INTO Assigned_Mood_To (track_id, username, mood) VALUES 
                            (%s, %s, %s)''', track, session["username"], sel_mood)
                        except Exception as e:  # may already exist
                            try:
                                g.conn.execute(
                                '''UPDATE Assigned_Mood_To SET mood=%s WHERE track_id=%s AND username=%s''', sel_mood, track, session["username"])
                            except Exception as e:
                                print(e)
        except Exception as e:
            print(e)
    return redirect('/')
            
# assign mood to albums
@app.route('/albumoods', methods=["POST", "GET"])
def add_album_moods():

    moods = []
    albums = []
    if request.method == 'POST':
        try:
            if "username" in session:
                sel_mood = ""
                if "select-album-mood" in request.form:
                    sel_mood = request.form["select-album-mood"]
                add_mood = request.form["add-album-mood"]
                if add_mood != "":
                    sel_mood = add_mood

                # get album mood
                for key in request.form.keys():
                    if key[0] == 'Q': #check if key is for a track
                        album = request.form[key]
                        try:               
                            g.conn.execute(
                            '''INSERT INTO Assigned_Mood_To2 (album_id, username, mood) VALUES 
                            (%s, %s, %s)''', album, session["username"], sel_mood)
                        except Exception as e:  # may already exist
                            try:
                                g.conn.execute(
                                '''UPDATE Assigned_Mood_To2 SET mood=%s WHERE album_id=%s AND username=%s''', 
                                sel_mood, album, session["username"])
                            except Exception as e:
                                print(e)
                                return redirect("/")
            else:
                return redirect("/logout")
        except Exception as e:
            print(e)
            return redirect("/")
    try:
        if "username" in session:
            # all albums associated with tracks on one of the user's existing playlists or Recommendations
            cursor = g.conn.execute(
                """
                    SELECT DISTINCT A.name, A.id
                    FROM Released_On R, Tracks T, Albums A, Saved_To S, existing_user_playlists E
                    WHERE A.id=R.album_id AND R.track_id=S.track_id AND S.existing_playlist_id=E.id AND E.username=%s
                    UNION
                    SELECT DISTINCT A.name, A.id
                    FROM Released_On R, Tracks T, Albums A, Added_To AD
                    WHERE A.id=R.album_id AND
                    AD.track_id=R.track_id AND AD.new_playlist_username=%s AND AD.new_playlist_name=%s AND AD.new_playlist_description=%s
                    ORDER BY name
                    LIMIT 100
                    """, session['username'], session['username'], "Recommendations", "")
            for result in cursor:
                # can also be accessed using result[0]
                albums.append(
                    {'name': result['name'], 'id': result['id']})  

            # all moods from this user
            cursor = g.conn.execute(
                """
                    SELECT DISTINCT M.mood as name
                    FROM assigned_Mood_To M
                    WHERE M.username=%s
                    UNION
                    SELECT DISTINCT M.mood as name
                    FROM assigned_Mood_To2 M
                    WHERE M.username=%s
                    ORDER BY name
                    """, session['username'], session['username'])
            for result in cursor:
                moods.append(result["name"])

            context = dict(albums=albums, moods=moods)
            return render_template('albumoods.html', **context)

        else:
            return redirect("/logout")
    except Exception as e:
        print(e)
        return redirect("/")

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python3 server.py

        Show the help text using:

            python3 server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
