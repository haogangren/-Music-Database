#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://hr2461:4111@34.73.21.127/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#Create table Genres
engine.execute("""CREATE TABLE IF NOT EXISTS Genres (
  Genre_ID CHAR(20),
  Genre_Name text,
  Description text,
  PRIMARY KEY (Genre_ID)
);""")
#Insert Values into table Genres
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

#Create table Band
engine.execute("""CREATE TABLE IF NOT EXISTS Band (
Band_ID CHAR(20),
Band_Name text,
Description text,
PRIMARY KEY (Band_ID)
);""")
#Insert Values into table Band
#engine.execute("""INSERT INTO Band VALUES ;""")

#Create table Artist
engine.execute("""CREATE TABLE IF NOT EXISTS Artist (
Artist_ID CHAR(20),
Artist_Name text,
Years Date,
Band_ID CHAR(20) NOT NULL,
PRIMARY KEY (Artist_ID),
FOREIGN KEY (Band_ID) 
REFERENCES Band
);""")
#Insert values into table Artist
#engine.execute("""INSERT INTO Artist VALUES ;""")

#Create table Composer
engine.execute("""CREATE TABLE IF NOT EXISTS Composer (
Composer_ID CHAR(20),
Artist_ID CHAR(20),
PRIMARY KEY (Composer_ID),
FOREIGN KEY (Artist_ID)
REFERENCES Artist
);""")
#Insert values into table Composer
#engine.execute("""INSERT INTO Composer VALUES ;""")

#Create table Singer
engine.execute("""CREATE TABLE IF NOT EXISTS Singer (
Singer_ID CHAR(20),
Artist_ID CHAR(20),
PRIMARY KEY (Singer_ID),
FOREIGN KEY (Artist_ID)
REFERENCES Artist
);""")
#Insert values into table Composer
#engine.execute("""INSERT INTO Singer VALUES ;""")

#Create table Albums
engine.execute("""CREATE TABLE IF NOT EXISTS Albums (
Album_ID CHAR(20),
Artist_ID CHAR(20) NOT NULL,
Album_Name CHAR(20),
Release_Date DATE,
PRIMARY KEY (Album_ID),
FOREIGN KEY (Artist_ID)
REFERENCES Artist
);""")
#Insert values into table Albums
#engine.execute("""INSERT INTO Composer VALUES ;""")

#Create table Tracks
engine.execute("""CREATE TABLE IF NOT EXISTS Tracks (
Track_ID CHAR(20),
Track_Name CHAR(20),
Lyric text,
Frequency_heard INT,
Play_time_in_seconds INT,
Album_ID CHAR(20) NOT NULL,
Genre_ID CHAR(20) NOT NULL,
Composer_ID CHAR(20),
Singer_ID CHAR(20),
PRIMARY KEY (Track_ID),
FOREIGN KEY (Album_ID)
REFERENCES Albums,
FOREIGN KEY (Genre_ID)
REFERENCES Genres,
FOREIGN KEY (Composer_ID)
REFERENCES Composer,
FOREIGN KEY (Singer_ID)
REFERENCES Singer
);""")
#Insert values into table Tracks
#engine.execute("""INSERT INTO Tracks VALUES ;""")



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
    print "uh oh, problem connecting to database"
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
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


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
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
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
  context = dict(data = names)


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
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
