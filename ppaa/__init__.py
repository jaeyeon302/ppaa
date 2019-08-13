from flask import Flask, g,render_template, request
from flask_babel import Babel, lazy_gettext, gettext
import os

def create_app(DEBUG=True):
	app = Flask(__name__,instance_relative_config=True)
	babel = Babel(app)
	
	#setting for locale
	@babel.localeselector
	def get_locale():
		korean = ['ko', 'ko-kr', 'ko-KR']
		supported_lang = ['en']
		supported_lang.extend(korean)
		lang = request.accept_languages.best_match(supported_lang)
		if lang in korean : return 'ko'
		else: return lang
		
	
	#update config
	from . import config
	config = config.set_config(database = os.path.join(app.instance_path,'markit.db'),
					   debug = DEBUG)
	app.config.update(config)
	
	#initialize database
	from . import db
	if not os.path.isdir(app.instance_path):
		os.mkdir(app.instance_path)
		db.init_db(app)
	db.init_app(app)
	
	#initialize print_format
	from . import utils
	utils.set_print_format()

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
