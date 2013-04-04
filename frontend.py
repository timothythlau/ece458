import db, bcrypt, sys, os, qrcode

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory
app = Flask(__name__)

debug = True

def checksession(step):
	try:
		if step == 1:
			if session['steponelogin']:
				return True
		
		elif step == 2:
			if session['steptwologin']:
				return True
	
	except KeyError:
		pass
	
	return False

@app.route('/')
def hello_world():
	if checksession(2):
		return redirect(url_for('getPollListing'))
	else:
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

	if checksession(1):
		session.pop('steponelogin', None)
		session.pop('user', None)
	if checksession(2):
		session.pop('steptwologin', None)

	return render_template('login.html', error=error)

@app.route('/login_verify', methods=['GET', 'POST'])
def login_verify():
	error = None
	
	if not checksession(1):
		return redirect(url_for('login'))
	
	if request.method == 'POST':
		verifystatus = db.verifyuser(session['user'],request.form['token'])
		
		if verifystatus:
			session['steptwologin'] = True
			flash('Logged in as ' + session['user'])
			return redirect(url_for('hello_world'))
		else:
			error = ('Incorrect two-factor token')
			return render_template('login.html', error=error)
	
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
					if debug:
						path = 'http://localhost:5000/qr/'
					else:
						path = 'http://ec2-54-242-83-73.compute-1.amazonaws.com/qr/'
					
					imgpath = path + usersec + '.png'
					return render_template('new_user_created.html', user=request.form['username'], secret=usersec, imgpath=imgpath)
				
				else:
					error = createstatus
					prevname = request.form['username']
			
			else:
				error = 'Password missing or incorrect'
				prevname = request.form['username']
	
	return render_template('new_user.html', error=error, prevname=prevname)
	
@app.route('/qr/<secret>')
def get_img(secret):
	return send_from_directory('qrcodes', secret)

@app.route('/show_polls', methods=['GET'])
def getPollListing():
	if checksession(2):
	    return render_template('show_polls.html', entries=db.getPolls())
	
	flash('Please login to access polls functionality')
	return redirect(url_for('login'))

@app.route('/poll/<int:poll_id>', methods=['GET', 'POST'])
def showPoll(poll_id):
	if checksession(2):
		error = None
		checkstatus = None
		if request.method == 'POST':
		    option = request.form['option']   
		    checkstatus = db.createVote(poll_id, option, 104)

		    if checkstatus == False:
		        error = 'Vote has already been cast'
		    
		return render_template('poll.html', error=error, success=checkstatus, poll_id=poll_id, poll=db.getPoll(poll_id), options=db.getOptions(poll_id))

	flash('Please login to access polls functionality')   
   	return redirect(url_for('login'))
    
@app.route('/result/<int:poll_id>', methods=['GET'])
def showResult(poll_id):
	if checksession(2):
	    return render_template('result.html', results=db.getPollResults(poll_id), votes=db.getPollHistory(poll_id))

	flash('Please login to access polls functionality')	    
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.debug = debug
	app.secret_key = os.urandom(24)
	app.run()
