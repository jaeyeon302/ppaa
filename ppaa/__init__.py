from flask import Flask, g,render_template
from ppaa.config import set_config
import os

def create_app(test_config=None):
	app = Flask(__name__,instance_relative_config=True)
	
	#update config
	config = set_config(database = os.path.join(app.instance_path,'markit.db'),
					   debug = True)
	app.config.update(config)
	
	#initialize database
	from . import db
	if not os.path.isdir(app.instance_path):
		os.mkdir(app.instance_path)
		db.init_db(app)
	db.init_app(app)
	
	#register 404
	@app.errorhandler(404)
	def page_not_found(error):
		return render_template('404.html')
	
	#register blueprints
	from . import auth
	app.register_blueprint(auth.bp)
	
	from . import api
	app.register_blueprint(api.bp)
	
	from . import mark
	app.register_blueprint(mark.bp)
	
	
	return app