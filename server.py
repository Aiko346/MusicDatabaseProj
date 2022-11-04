from flask import Flask, redirect, url_for, request
from typing import ItemsView
import requests
# import json
import urllib
import base64
import spotipy
import spotipy.util as util
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
#redirect_uri = "http://127.0.0.1:8111/data-processing"
#redirect_uri = "http://localhost:8111/data-processing"
client_id = "67bdc4b1d4d74f5d88cdab031fee6a41"
client_secret = "1a88af0b600d4ce3bf81c5191ae3aac0"
scopes = "playlist-read-private,user-read-private,user-read-email,user-library-read"

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.debug = True
app.secret_key = '648e2097fec28316b68b70c56305fdb6d2c07c82e4f00fce04e26ff0230eb3e4'
# app.config['SECRET_KEY'] = '648e2097fec28316b68b70c56305fdb6d2c07c82e4f00fce04e26ff0230eb3e4'
# toolbar = DebugToolbarExtension(app)

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
DATABASEURI = "postgresql://alg2252:5368@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

# track current filter params in session
# format session.filter_yes={playlist: [], song: [], mood: [], artist:[], album[], liked_by[]}
# format session.filter_no={playlist: [], song: [], mood: [], artist:[], album[], liked_by[]}

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
    import traceback; traceback.print_exc()
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



#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """
  if 'username' in session:
    print(session['username'])
  else:
    print('no username')
  # DEBUG: this is debugging code to see what request looks like
  # print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  testlist = ["a", "b", "c"]
  context = dict(data = names, testlist=testlist)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
# @app.route('/another')
# def another():
#   return render_template("another.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')

@app.route('/get-data')
def get_data():
    redirect_uri = "http://localhost:8111/data-processing"
    return redirect("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": client_id, "response_type": "code", "redirect_uri": redirect_uri, "scope": scopes
    }))

@app.route('/data-processing')
def data_processing():
  
  code = request.args.get("code")
  redirect_uri="http://localhost:8111/data-processing"
  
  result = requests.post(url="https://accounts.spotify.com/api/token", data={
          "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
          "client_id": client_id, "client_secret": client_secret
  })

  #r = result.json()
  print()
  r = result.json()

  session["access_token"] = r["access_token"]
  session["refresh_token"] = r["refresh_token"]

  
  return redirect("/login")

@app.route('/fill-home')
def fill_home():
  #get multiple playlists

  #get songs from playlists

  #add to tracks 
  # print(session["access_token"])
  # print(session["username"])
  # print(session["return_to"])
  return redirect("/")

@app.route('/add-friend', methods=["GET", "POST"])
def add_friend():
    print("adding_friend")
    if request.method == 'POST':
      # refresh access token (only valid for about an hour)
      result = requests.post(url="https://accounts.spotify.com/api/token", data={
            "grant_type": "refresh_token", "refresh_token": session["refresh_token"], "client_id": client_id, "client_secret": client_secret
      })
      if result.status_code != 200:
          return redirect("/get-data")
      sp = spotipy.Spotify(auth=session["access_token"])
      user_info = sp.user(request.form["friend-id"])
      display_name = user_info["display_name"] 
      user_playlist_info = sp.user_playlists(request.form["friend-id"], limit = 2) #5 max
      print(user_playlist_info)
      user_playlist_ids = []
      for item in user_playlist_info["items"]:
        user_playlist_ids.append(item["uri"])
      #add display_name to sql
      for uri in user_playlist_ids:
        tracks = sp.user_playlist_tracks(request.form["friend-id"], uri[17:])
        print(tracks)
        #limit at 100 per playlist due to speed
        #check if tracks in Tracks for user already, if so create Liked_By relationship
      print()
      
    #    # c = sp.current_user_playlists(limit = 10)
    # # for item in c["items"]:
    # #     print(item['description'])
    # #     print(item["name"])
    # #     print(item[])
    # playlist_data = sp.user_playlist(user="zsp0yz1vi3brxtpz39a8zefqk",
    #                                  playlist_id="5RuV6Qo9qJMrJ49NwTIYRW", fields="tracks,id,next,name,description")
      
   
    return redirect("/fill-home")


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password'] 
    
    #make sql call to check if this username/password combo is in the database:

    #if it fails:
     
    #if it succeeds:

    #session.clear()
    session['username'] = username
    
    #return redirect('/')
    # redirect_uri = "http://localhost:8111/data-processing"
   
   
    
    #get_data("http://localhost:8111/data-processing")
    return redirect('/fill-home')
  return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password'] 
   
    #make sql call to add this username/password combo is in the database:

    #if it fails:
     
    #if it succeeds:
    return redirect('/')
  return render_template("register.html")


@app.route('/filter', methods=['POST'])
def filter():
  filter_option = request.form['filter-option']
  #g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)

  
  return redirect('/')




@app.route('/new-playlist', methods=['POST'])
def new_playlist():
  name = request.form['playlist-name']
  description = request.form['playlist-description']
  g.conn.execute('INSERT INTO new_playlists(name, description) VALUES (%s, %s)', name, description)
  print("testing new_playlist()")
  # if 'playlist' in session:
  #   print("%s test", name)
  #   for key in session.keys():  
  #       print(session[key])
  #   session[name].append(name)
  #   for playlist_name in session['playlist']:  
  #       print(len(session['playlist']))
  #       print(playlist_name)
  #   print()
  # else:
  #   session['playlist'] = []
  #   print(type(session['playlist']))
  #   session['playlist'].append(name)
  return redirect('/')

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
