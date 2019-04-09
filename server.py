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
from flask import Flask, request, render_template, g, redirect, Response, jsonify

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
def musicDB():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
#  print request.args
#  
#  search = MusicSearchForm(request.form)
#  if request.method == 'POST':
#     return search_results(search
  tables = ["Artist", "Album", "Band", "Composer", "Singer", "Tracks","Genres"]
  return render_template("musicDB.html", tables = tables)
  
tableColumns = {
    "Artist": ["Artist_ID", "Artist_Name","Years","Band_ID"],
    "Album" : ["Album_ID", "Artist_ID", "Album_Name", "Release_Date"],
    "Band" : ["Band_ID", "Band_Name", "Description"],
    "Composer" : ["Composer_ID", "Instrument"],
    "Singer" : ["Singer_ID", "Voicelevel"],
    "Tracks" : ["Track_ID", "Track_Name", "Lyric", "Frequency_heard", "Play_time_in_seconds","Album_ID", "Genre_ID", "Composer_ID", "Singer_ID"],
    "Genres" : ["Genre_ID", "Genre_Name", "Description"]
}

@app.route('/getForm', methods = ["GET"])
def getForm():
    table = request.args.get('table')
    fields = tableColumns[table]
    deleteFields = [fields[0]]
    return render_template("actions.html", table = table, fields = fields, deleteFields = deleteFields)

@app.route('/search',methods = ['POST'])
def search():
    table = request.form['table']
    field = tableColumns[table][0]
    value = request.form[field]
    query = "Select " + "*" + " from " + table + " where " + field + " = %s"
    resultProxy = g.conn.execute(query,value)
    results = []
    for rowProxy in resultProxy:
        data = {}
        for column, value in rowProxy.items():
            data[column] = value
        results.append(data)
    print results
    return render_template("results.html", results = results)
        
    


@app.route('/create', methods=["POST"])
def create():
    table = request.form['table']
    fields = tableColumns[table]
    values = []
    for field in fields:
        values.append(request.form[field])
    query = "INSERT INTO " + table + " VALUES (" + ','.join(['%s']*len(fields)) + ")"
    g.conn.execute(query, values)
    
    return redirect('/')
            

@app.route('/update',methods=['POST'])
def update():
    table = request.form['table']
    fields = tableColumns[table]
    fieldsRequiringSet = []
    values = []
    for field in fields:
        if field != fields[0]:
            fieldsRequiringSet.append(field)
            values.append(request.form[field])
    query = "UPDATE " + table + " SET" + " (" + ", ".join(fieldsRequiringSet) + ")" + " = (" + ','.join(['%s']*(len(fieldsRequiringSet))) + ")" + " WHERE " + fields[0] + " = %s"
    values.append(request.form[fields[0]])
    print query
    print values
    g.conn.execute(query, values)
    return redirect('/')
    

@app.route('/delete',methods = ['POST'])
def delete():
    table = request.form['table']
    field = tableColumns[table][0]
    value = request.form[field]
    query = "DELETE FROM " + table + " WHERE " + field + " = %s"
    print query
    g.conn.execute(query, value)
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
