import json
import os
import markdown
import logging
import sys
import socket
from datetime import datetime
from flask import Flask, abort, flash, Markup, redirect, render_template, request, Response, session, url_for
from flask_sqlalchemy import SQLAlchemy

# config setup
with open('config.json') as f:
    config = json.load(f)

#Flask app setup
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

#logging setup
app.logger.setLevel(config['LOGGING']['LEVEL']['ALL'])
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(style='{', fmt='{asctime} [{levelname}] {message}', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
handler.setLevel(config['LOGGING']['LEVEL']['CONSOLE'])
app.logger.addHandler(handler)
handler = logging.FileHandler(config['LOGGING']['FILE'])
handler.setFormatter(formatter)
handler.setLevel(config['LOGGING']['LEVEL']['FILE'])
app.logger.addHandler(handler)

#Create sqlalchemy object
db = SQLAlchemy(app)

from models import *

@app.route('/')
def index():
	"""Shows the user the main blog page with a list of blogposts in chronological order
	Args:
		None
	Returns;
	str: rendered template 'login.html'
	"""
	query = Entry.query.order_by(Entry.timestamp.desc()).limit(5).all()
	if('logged_in' not in session or session['logged_in'] == False):
		query = Entry.query.order_by(Entry.timestamp.desc()).filter(Entry.published == True).all()

	return render_template('index.html',blogposts=query)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		password = request.form['password']
		if password == config['ADMIN_PASSWORD']:
			session['logged_in'] = True
			session.permanent = True
			flash('Logged in as an admin!','success')
			app.logger.info("Login detected")
			return redirect(url_for('index'))
		else:
			app.logger.info("Login attempted")
			flash('Incorrect password.','danger')

	return render_template('login.html')

@app.route('/logout/')
def logout():
	if('logged_in' in session and session['logged_in']):
		flash('Logged out successfully!','success')
		app.logger.info("Logout detected")
	session.clear()
	return redirect(url_for('index'))

@app.route('/new_post/', methods=['GET','POST'])
def new_post():
	if('logged_in' not in session or session['logged_in'] == False):
		return redirect(url_for('index'))

	if request.method == 'POST':
		title = request.form.get('title')
		shortDesc = request.form.get('shortDesc')
		content = request.form.get('content')
		published = True
		if request.form.get('published') is None:
			published = False

		post = Entry(title,shortDesc,content,published)
		db.session.add(post)
		db.session.commit()
		if published:
			app.logger.info("Post published with title {}".format(post.title))
		else:
			app.logger.info("Post drafted with title {}".format(post.title))

		return redirect(url_for('index'))

	return render_template('new_post.html')

@app.route('/view_post/<int:id>')
def view_post(id):
	post = Entry.query.filter(Entry.id == id).first()
	if post == None:
		return redirect(url_for('index'))

	if 'logged_in' not in session or session['logged_in'] == False:
		if post.published == False:
			return redirect(url_for('index'))

	md = Markup(markdown.markdown(post.content))
	return render_template('view_post.html',blogpost=post,content_markdown=md)


@app.route('/edit_post/<int:id>', methods=['GET','POST'])
def edit_post(id):
	if('logged_in' not in session or session['logged_in'] == False):
		return redirect(url_for('index'))

	post = Entry.query.filter(Entry.id == id).first()
	if post == None:
		return redirect(url_for('index'))

	if request.method == 'POST':
		title = request.form.get('title')
		shortDesc = request.form.get('shortDesc')
		content = request.form.get('content')
		published = True
		if request.form.get('published') is None:
			published = False

		post.title = title
		post.shortDesc = shortDesc
		post.content = content
		post.published = published
		db.session.commit()
		app.logger.info("Edited post {} with id {}".format(title,id))
		return redirect(url_for('view_post', id=id))

	return render_template('edit_post.html',blogpost=post)

@app.route('/remove_post/<int:id>')
def remove_post(id):
	if('logged_in' in session and session['logged_in'] == True):
		#Remove post
		post = Entry.query.filter(Entry.id == id).first()
		if post == None:
			app.logger.info("No post to remove with id {}".format(id))
		else:
			db.session.delete(post)
			db.session.commit()
			app.logger.info("Post {} removed with id {}".format(post.title,id))

	return redirect(url_for('index'))

#Run app
if __name__ == '__main__':
	app.run()