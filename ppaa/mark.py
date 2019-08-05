import functools
from flask import Blueprint, flash, g, redirect, render_template, session, url_for,abort
from flask import request as req
from markit.db import get_db
from markit.utils import objFromDict, complete_link, validate_link
from markit.auth import login_required
import traceback as tb

from collections import Counter

ERR = dict(
	UNVALID=dict(
		LINK="unvalid link"
	)
)
ERR = objFromDict(ERR)


bp = Blueprint('mark',__name__)

def generate_tag_table(marks):
	tags = { mark:[tag for tag in mark['tag'].split('#') if tag !=''] for mark in marks if mark['tag']}
	return tags

def count_tag_table(tag_table):
	tagCounter = []
	for taglist in tag_table.values():
		tagCounter.extend(taglist)
	return Counter(tagCounter)

	
@bp.route('/')
@bp.route('/<path:link>')
def index(link=None):
	db = get_db()
	if link is not None and '/' in link:
		index = link.index('/')
		username = link[:index]
		link = link[index+1:]
		#complete link url to redirect
		link = complete_link(link,req.query_string)
			
		#return "{} {}".format(username,link)
		user = db.execute('SELECT id,email FROM user WHERE username = ?',(username,)).fetchone()
		if not user:
			return render_template('mark/no_user.html',username=username,link=link)
		
		if validate_link(link):
			already_inserted = db.execute('SELECT link FROM mark WHERE user_id=? AND link=?',
										 (user['id'],link)).fetchone()
			if already_inserted:
				return render_template('mark/already_inserted.html',username=username,link=link)
			else:
				db.execute('INSERT INTO mark (user_id,link) VALUES (?,?)',(user['id'],link))
				db.commit()
				#TODO : send email 
				return redirect(link)
		else:
			flash(ERR.UNVALID.LINK)
			abort(404)
	
	if link:abort(404)
	if not g.user:
		#render introduction 
		return render_template('mark/index.html')
	else:
		marks = db.execute('SELECT * FROM mark WHERE user_id = ? ORDER BY id DESC',(g.user['id'],)).fetchall()
		tags = generate_tag_table(marks)
		tag_counter = count_tag_table(tags)
		data = dict(
			marks=marks,
			counts=len(marks),
			tags=tags,
			tag_counter = tag_counter
		)
		return render_template('mark/marks.html',data=data)
	
@bp.route('/mark')
@login_required
def tag_index():
	db=get_db()
	tag = req.args.get('tag')
	print(tag)
	user_id = g.user['id']
	marks = db.execute(
		"SELECT * FROM mark WHERE user_id={} AND tag LIKE '%{}%' ORDER BY id DESC".format(user_id,tag)
		).fetchall()
	tags = generate_tag_table(marks)
	all_tags = db.execute(
				'SELECT tag FROM mark WHERE user_id = ?',(g.user['id'],)
				).fetchall()
	all_tags = generate_tag_table(all_tags)
	tag_counter = count_tag_table(all_tags)

	data = dict(
		marks=marks,
		counts=len(marks),
		tags=tags,
		target_tag = tag,
		tag_counter = tag_counter
	)

	return render_template('mark/marks.html',data=data)
	
	
	
	
	
	
	
	