from flask import Flask
from markit.config import set_config

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
	db .init_app(app)
	
	#register blueprints
	from . import auth
	app.register_blueprint(auth.bp)
	
	
	return app