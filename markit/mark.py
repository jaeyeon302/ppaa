import functools
from flask import Blueprint, flash, g, redirect, render_template, session, url_for
from flask import request as req
from markit.db import get_db
from markit.utils import objFromDict
from markit.auth import login_required
import traceback as tb

ERR = dict()
ERR = objFromDict(ERR)

bp = Blueprint('mark',__name__)

@bp.route('/')
@bp.route('/<path:link>')
def index(link=None):
	db = get_db()
	if link is not None and '/' in link:
		index = link.index('/')
		username = link[:index]
		link = link[index+1:]
		
		#complete link url to redirect
		if link.startswith('http:/'):
			link = 'http://'+link[len('http:/'):]
		elif link.startswith('https:/'):
			link = 'https://'+link[len('https:/'):]
		else:
			link = 'http://'+link
		#return "{} {}".format(username,link)
		user = db.execute('SELECT id,email FROM user WHERE username = ?',(username,)).fetchone()
		if not user:
			return render_template('mark/no_user.html',username=username,link=link)
		
		db.execute('INSERT INTO mark (user_id,link) VALUES (?,?)',(user['id'],link))
		db.commit()
		#TODO : send email 
		return redirect(link)
	
	if not g.user:
		#render introduction 
		return render_template('mark/index.html')
	else:
		marks = db.execute('SELECT * FROM mark WHERE user_id = ?',(g.user['id'],)).fetchall()
		return render_template('mark/marks.html', marks = marks, user = g.user)
	
	
	
	
	
	
	
	
	
	