import functools
from flask import Blueprint, flash, g, redirect, session, url_for
from flask import request as req
from markit.db import get_db
from markit.utils import objFromDict, complete_link
from markit.auth import login_required
import traceback as tb


ERR = dict()
ERR = objFromDict(ERR)

bp = Blueprint('api',__name__,url_prefix="/api")

@bp.route('/')
@login_required
def index():
	return redirect(url_for('mark.index'))


@bp.route("/del/<path:link>")
@login_required
def del_link(link):
	db = get_db()
	link = complete_link(link,req.query_string)
	user_id = g.user['id']
	db.execute('DELETE FROM mark WHERE user_id=? AND link=?',(g.user['id'],link))
	db.commit()
	flash("link is deleted")
	return redirect(url_for('mark.index'))

@bp.route('/link/<path:link>')
@login_required
def visit_link(link):
	db = get_db()
	link = complete_link(link,req.query_string)
	user_id = g.user['id']
	db.execute('UPDATE mark SET view_count=view_count+1 WHERE user_id=? AND link=?',(user_id,link))
	db.commit()
	return redirect(link)

@bp.route('/add_tag',methods=('POST',))
@login_required
def add_tag():
	db = get_db()
	if req.method =='POST':
		tag = req.form['tag'].lstrip().rstrip()
		link = complete_link(req.form['link'].lstrip().rstrip())
		user_id=g.user['id']
		if not tag:
			return redirect(url_for('mark.index'))
		tag = tag.replace(' ','')
		if not tag.startswith('#'):
			tag="#{}".format(tag)
		print(tag)
		db.execute('UPDATE mark SET tag = tag||? WHERE user_id=? AND link=?',
				   (tag,user_id,link))
		db.commit()

		return redirect(url_for('mark.index'))
	
@bp.route('/del_tag', methods=('POST',))
@login_required
def del_tag():
	if req.method != 'POST':
		return redirect(url_for('mark.index'))
	
	link = req.form['link'].lstrip().rstrip()
	tag = req.form['tag'].lstrip().rstrip()
	db = get_db()
	if link is not None and tag is not None:
		user_id = g.user['id']
		tags = db.execute('SELECT tag FROM mark WHERE user_id=? AND link=?',
						 (user_id,link)).fetchone()['tag']
		if tags:
			tags = tags.split('#')
			tags = [t for t in tags if t != tag]
			update_tag = ""
			for t in tags:
				update_tag += "#{}".format(t)
			db.execute('UPDATE mark SET tag=? WHERE user_id=? AND link=?',
					  (update_tag,user_id,link))
			db.commit()
			
		
	return redirect(url_for('mark.index'))
