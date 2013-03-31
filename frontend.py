import db, bcrypt, sys, os, qrcode

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
app = Flask(__name__)

@app.route('/')
def hello_world():
	return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        loginstatus = db.login(request.form['username'],request.form['password'])
        if loginstatus == True:
			session['steponelogin'] = True
			session['user'] = request.form['username']
			return redirect(url_for('login_verify'))
        elif loginstatus == False:
        	error = 'Invalid e-mail or password'
        else:
        	error = 'Login mechanism failed'
    
    session.pop('steponelogin', None)
    session.pop('steptwologin', None)
    session.pop('user', None)
        	
    return render_template('login.html', error=error)

@app.route('/login_verify', methods=['GET', 'POST'])
def login_verify():
	error = None
	
	if not session['steponelogin']:
		return redirect(url_for('login'))
	
	if request.method == 'POST':
		verifystatus = db.verifyuser(session['user'],request.form['token'])
		
		if verifystatus:
			session['steptwologin'] = True
			flash('Logged in as ' + session['user'])
			return redirect(url_for('hello_world'))
		else:
			flash('Incorrect two-factor token')
			return redirect(url_for('login'))
	
	return render_template('login_verify.html', error=error)

@app.route('/logout')
def logout():
    session.pop('steponelogin', None)
    session.pop('steptwologin', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('hello_world'))
    
@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
	error = None
	prevname = None
	if request.method == 'POST':
		checkstatus = db.checkuser(request.form['username'])
		
		if checkstatus != True:
			error = checkstatus
			prevname = request.form['username']
			
		else:
			if len(request.form['password'])<6:
				error = 'Password too short, must be 6 or more characters'
			
			elif request.form['password'] == request.form['passwordconfirm']:
				createstatus, usersec = db.createuser(request.form['username'], request.form['password'])
			
				if createstatus == True:
					#userqrkey = 'otpauth://totp/' + request.form['username'] + '?secret=' + usersec
					#qrimg = qrcode.make(userqrkey)
					return render_template('new_user_created.html', user=request.form['username'], secret=usersec)
					
					#return redirect(url_for('login'))
				
				else:
					error = createstatus
					prevname = request.form['username']
			
			else:
				error = 'Password missing or incorrect'
				prevname = request.form['username']
	
	return render_template('new_user.html', error=error, prevname=prevname)
    
if __name__ == '__main__':
	app.debug = True
	app.secret_key = os.urandom(24)
	app.run()
