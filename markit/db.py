import sqlite3
from flask import current_app, g

def get_db():
	if 'db' not in g:
		db = sqlite3.connect(
			current_app.config['DATABASE'],
		)
		db.row_factory = sqlite3.Row
		g.db = db
		
	return g.db

def close_db(err=None):
	db = g.pop('db',None)
	if db is not None:
		db.close()

def init_db(app):
	with app.open_resource('schema.sql') as f:
		with app.app_context():
			db = get_db()
			db.cursor().executescript(f.read().decode('utf-8'))
			print('Initialized Database')

def init_app(app):
	app.teardown_appcontext(close_db)