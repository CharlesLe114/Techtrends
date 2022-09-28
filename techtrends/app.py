import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

conn_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define the health check
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info("Status request successfull")
    return response

# Define the metrics check
@app.route('/metrics')
def metrics():
    global conn_count
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)

    # print(connections)
    connection.close()
    dictionary = {'post_cound':post_count}
    response = app.response_class(
        # response=json.dumps(dictionary),
        response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": conn_count, "post_count": post_count}}),
        status=200,
        mimetype='application/json'
    )

    app.logger.info("Metrics request successfull")
    return response


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("A non-existing article is accessed")
        return render_template('404.html'), 404
    else:
        app.logger.info("Article {0} retrieve".format(post["title"]))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("The 'About Us' page is retrieved.")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("Article {0} created".format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    format_output = '%(levelname)s: %(name)-2s - [%(asctime)s] - %(message)s'
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)  # TODO: stderr handler
    handlers = [stderr_handler, stdout_handler]

    logging.basicConfig(format = format_output,handlers=handlers,level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')
