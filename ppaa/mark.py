import functools
from flask import Blueprint, flash, g, redirect, render_template, session, url_for,abort
from flask import request as req
from ppaa.db import get_db
from ppaa.utils import objFromDict, complete_link,add_funcname_to_print
from ppaa.auth import login_required
import traceback as tb

from collections import Counter


ERR = dict(
	UNVALID=dict(
		LINK="unvalid link",
		VERIFY="Verify your account first to bookmark"
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
@add_funcname_to_print
def index(print,link=None):
	db = get_db()
	if link is not None and '/' in link:
		index = link.index('/')
		username = link[:index]
		index = req.url.index("{}/".format(username))
		link = req.url[index+len(username)+1:]
		#complete link url to redirect
		link = complete_link(link)
			
		#return "{} {}".format(username,link)
		user = db.execute('SELECT id,email,verified FROM user WHERE username = ?',(username,)).fetchone()
		
		if not user:
			print("Not user / username:{}, link:{}".format(username,link))
			return render_template('mark/no_user.html',username=username,link=link)
		
		if user['verified']!=1:
			flash(ERR.UNVALID.VERIFY)
			print("Unverified / user_id:{}".format(user['id']))
			return redirect(url_for('auth.login'))
		
		already_inserted = db.execute('SELECT link FROM mark WHERE user_id=? AND link=?',
									 (user['id'],link)).fetchone()
		
		if already_inserted:
			print("Already_inserted / user_id:{}, link:{}".format(user['id'],link))
			return render_template('mark/already_inserted.html',username=username,link=link)
		else:
			db.execute('INSERT INTO mark (user_id,link) VALUES (?,?)',(user['id'],link))
			db.commit()
			#TODO : send email 
			print("Add link / user_id:{}, link:{}".format(user['id'],link))
			return redirect(link)
	
	if link:abort(404)
	if not g.user:
		#render introduction 
		print("Unknown user visits ppaa.me /")
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
		print("Access marks / user_id:{}".format(g.user['id']))
		return render_template('mark/marks.html',data=data)
	
@bp.route('/mark')
@login_required
@add_funcname_to_print
def tag_index(print):
	db=get_db()
	tag = req.args.get('tag')
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
	print("Tag selected / tag:{}, user_id:{}".format(tag,g.user['id']))
	return render_template('mark/marks.html',data=data)
	
	
	
	
	
	
	
	