import functools
from flask import Blueprint,flash,g,redirect,render_template,session,url_for
from flask import request as req
from werkzeug.security import check_password_hash, generate_password_hash
from markit.db import get_db
from markit.utils import objFromDict
import traceback as tb

ERR = dict(	
	REGISTER = dict(
		REQUIRED = dict(
			USERNAME = "username is required",
			PW = 'password is required',
			EMAIL = 'email is required'
		),
		WRONG = dict(
			PW = 'password not confirmed',
			EMAIL = 'unsuitable email format'
		),
		ENROLLED = 'already registered'
	),
	LOGIN = dict(
		INCORRECT = dict(
			EMAIL = "incorrect email",
			PW = 'incorrect password'
		)
	),
	VERIFY = dict(
		COMPLETE = "verified",
		UNCOMPLETE = "wrong page"
	),
	CONFIGURE = dict(
		SUCCESS = "CONFIGURATION SUCCESS",
		FAIL = dict(
			PW = "PW WRONG",
			GENERAL = "CONFIGURATION FAIL"
		)
	)
)
ERR = objFromDict(ERR)


bp = Blueprint('auth',__name__,url_prefix='/auth')

		
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if not g.user:
			return redirect(url_for('auth.login'))
		return view(**kwargs)
	return wrapped_view


@bp.route('/register',methods=('GET','POST'))
def register():
	if req.method == 'POST':
		username = req.form['username'].lstrip().rstrip()
		pw = req.form['pw'].lstrip().rstrip()
		pw_confirm = req.form['pw-confirm'].lstrip().rstrip()
		email = req.form['email'].lstrip().rstrip()
		db = get_db()
		err = None
		if not username: err = ERR.REGISTER.REQUIRED.USERNAME
		elif not pw: err = ERR.REGISTER.REQUIRED.PW
		elif pw!=pw_confirm: err = ERR.REGISTER.WRONG.PW
		elif not email: err = ERR.REGISTER.REQUIRED.EMAIL
		elif db.execute('SELECT id FROM user WHERE email = ?',(email,)).fetchone():
			err = "{} {}".format(email,ERR.REGISTER.ENROLLED)
		elif db.execute('SELECT id FROM user WHERE username = ?',(username,)).fetchone():
			err = "{} {}".formaT(username, ERR.REGISTER.ENROLLED)
		else:
			pass
		
		if not err:
			email_hash = hash(email)
			try:
				db.execute(
					'INSERT INTO user (username,email,email_hash,password) VALUES (?,?,?,?)',
					(username,email,email_hash,generate_password_hash(pw))
				)
				db.commit()
				#TODO : send email to verify email address
				return redirect(url_for('auth.login'))
			except:
				tb.print_exc()
				err = ERR.REGISTER.WRONG.EMAIL
				
		flash(err)
	return render_template('auth/register.html')

@bp.route('/')
def index():
	return redirect(url_for('auth.login'))

@bp.route('/login',methods=('GET','POST'))
def login():
	if req.method == 'POST':
		pw = req.form['pw'].lstrip().rstrip()
		email = req.form['email'].lstrip().rstrip()
		db = get_db()
		err = None
		
		user = db.execute(
			'SELECT * FROM user WHERE email = ?',(email,)
		).fetchone()
		
		if not user: 
			err = ERR.LOGIN.INCORRECT.EMAIL
		elif not check_password_hash(user['password'],pw):
			err = ERR.LOGIN.INCORRECT.PW
		else:
			pass
		if not err:
			session.clear()
			session['user_id'] = user['id']
			print(url_for('mark.index'))
			return redirect(url_for('mark.index'))
		flash(err)
	return render_template('auth/login.html')

@bp.route('/verify')
def verify():
	email_hash = req.args.get('h')
	if not email_hash: return render_template('404.html')
	
	user = db.execute('SELECT id,email FROM user WHERE email_hash = ?',
					  (email_hash,)).fetchone()
	if user:
		db.execute(
			'UPDATE user SET verified=? WHERE id=?',(1,user['id'])
		)
		db.commit()
		flash(ERR.VERIFY.COMPLETE)
		return render_template('auth/verified.html', email=user['email'])
	else:
		return render_template('404.html')

@bp.route('/configure',methods=('GET','POST'))
@login_required
def configure():
	if req.method == 'POST':
		old_pw = req.form['old-pw'].lstrip().rstrip()
		new_pw = req.form['new-pw'].lstrip().rstrip()
		new_pw_confirm = req.form['new-pw-confirm'].lstrip().rstrip()
		username = req.form['username'].lstrip().rstrip()

		err = None
		if not check_password_hash(g.user['password'],old_pw):
			err = ERR.CONFIGURE.FAIL.PW
		if new_pw is not None and new_pw!=new_pw_confirm:
			err = ERR.REGISTER.WRONG.PW
		
		
		if not err:
			db = get_db()
			err = ERR.CONFIGURE.SUCCESS
			if new_pw is not None:
				db.execute(
					"UPDATE user SET username = ?, password = ?WHERE email = ?",
					(username,generate_password_hash(new_pw),g.user['email']))
				db.commit()
			else:
				db.execute(
					"UPDATE user SET username = ? WHERE email = ?",(username,))
				db.commit()

		flash(err)
		return redirect(url_for('auth.configure'))
	
	return render_template('auth/configure.html',
						  username = g.user['username'],
						  email = g.user['email']
						  )
		
@bp.route('/logout')
@login_required
def logout():
	session.clear()
	return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')
	if not user_id:
		g.user = None
	else:
		g.user = get_db().execute(
			'SELECT * FROM user WHERE id = ?',(user_id,)
		).fetchone()



