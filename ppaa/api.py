import functools
from flask import Blueprint, flash, g, redirect, session, url_for
from flask import request as req
from flask_babel import lazy_gettext
from ppaa.db import get_db
from ppaa.utils import objFromDict, complete_link, add_funcname_to_print
from ppaa.auth import login_required
import traceback as tb


ERR = dict(
	DEL=dict(
		LINK=lazy_gettext('apy-del-link'),
		TAG=lazy_gettext('apy-del-tag'),
		USER=lazy_gettext('apy-del-account')
	),
	VERIFY=dict(
		RESEND=lazy_gettext('apy-verify-resend')
	)
)
ERR = objFromDict(ERR)

bp = Blueprint('api',__name__,url_prefix="/api")

@bp.route('/')
@login_required
def index():
	return redirect(url_for('mark.index'))


@bp.route("/del/<path:link>")
@login_required
@add_funcname_to_print
def del_link(print,link):
	db = get_db()
	index = req.url.index('/del/')
	link = req.url[index+len('/del/'):]
	link = complete_link(link)
	db.execute('DELETE FROM mark WHERE user_id=? AND link=?',(g.user['id'],link))
	db.commit()
	print("Delete / link:{}, user_id:{}".format(link,g.user['id']))
	flash(ERR.DEL.LINK)
	return redirect(url_for('mark.index'))

@bp.route('/link/<path:link>')
@login_required
@add_funcname_to_print
def visit_link(print,link):
	db = get_db()
	index = req.url.index('/link/')
	link = req.url[index+len('/link/'):]
	link = complete_link(link)
	user_id = g.user['id']
	db.execute('UPDATE mark SET view_count=view_count+1 WHERE user_id=? AND link=?',(user_id,link))
	db.commit()
	print("link:{}, user_id:{}".format(link,user_id))
	return redirect(link)

@bp.route('/add_tag',methods=('POST',))
@login_required
@add_funcname_to_print
def add_tag(print):
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

		db.execute('UPDATE mark SET tag = tag||? WHERE user_id=? AND link=?',
				   (tag,user_id,link))
		db.commit()
		print("tag:{}, user_id:{}, link:{}".format(tag,user_id,link))

		return redirect(url_for('mark.index'))
	
@bp.route('/del_tag', methods=('POST',))
@login_required
@add_funcname_to_print
def del_tag(print):
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
			print("tag:{}, user_id:{}, link:{}".format(tag,user_id,link))
	return redirect(url_for('mark.index'))

@bp.route('/del_user')
@login_required
@add_funcname_to_print
def del_user(print):
	user_id = g.user['id']
	email = g.user['email']
	db = get_db()
	db.execute('DELETE FROM user WHERE id=?',(user_id,))
	db.execute('DELETE FROM mark WHERE user_id=?',(user_id,))
	db.commit()
	flash("{} {}".format(email,ERR.DEL.USER))
	print("user_id:{}, email:{} removed".format(user_id, email))
	return redirect(url_for('auth.logout'))
	

@bp.route('/verify')
@login_required
@add_funcname_to_print
def verify(print):
	from ppaa.auth import authenticate_user
	authenticate_user(g.user['username'],g.user['email'],g.user['email_hash'],req.host)
	flash(ERR.VERIFY.RESEND)
	print("Resend email to Verify / user_id:{}, email:{}".format(g.user['id'],g.user['email']))
	return redirect(url_for('mark.index'))
	