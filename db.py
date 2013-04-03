import MySQLdb
import onetimepass as otp
import sys, string, random, base64, bcrypt, qrcode, crypt
from datetime import datetime

#DB connection settings
conhost = 'localhost'
conuser = 'ece458'
condb = 'ece458'

#use seperate class to manage MySQL queries
class DB:
	conn = None
	
	#create connection
	def connect(self):
		self.conn = MySQLdb.connect(host=conhost,user=conuser,db=condb)
	
	#query DB and return cursor for control
	def query(self, sql, param):
		try:
			self.connect()
			cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute(sql,param)
			
			# if query is not a select statement, commit to DB
			if string.find(sql,'select',0,6) == -1:
				print 'sql commit'
				self.conn.commit()
			status = True
		
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
			status = False
		return cursor, status

#check if user already exists
def checkuser(email):
	db = DB()
	
	cur, status = db.query("select email from Users where email=%s",(email,))
	
	if status == False:
		print "MySQL error"
		return "MySQL error"
	
	#check for duplicate users
	if cur.fetchone() != None:
		print "User exists already"
		return "Username exists already, please choose different username"
	else:
		return True

#create user and assign random secret for two-factor authentication
def createuser(email,pw):
	db = DB()
	
	#assign secret to user, hash pw, insert into db
	secret = base64.b32encode(''.join(random.choice(string.replace(string.ascii_uppercase + string.digits, '8', '')) for x in range(10)))
	hashpw = bcrypt.hashpw(pw, bcrypt.gensalt())
	cur, status = db.query("insert into Users(email,password,secret) values (%s,%s,%s)",(email,hashpw,secret))
	
	if status == False:
		print "MySQL error"
		return "MySQL error", -1
	else:
		qrimg = qrcode.make('otpauth://totp/' + email + '?secret=' + secret)
		qrimg.save('qrcodes/' + secret +'.png')
		
		print "User successfully added"
		return True, secret

#check for valid username and password, returns True if valid, False if not valid, None for SQL error
def login(email,pw):

	if pw == '' or email == '':
		return False;
	
	db = DB()
	cur, status = db.query("select password from Users where email=%s",(email,))
	
	if status == True:
		row = cur.fetchone()
		
		if row != None:
			dbpw = row['password']
			if dbpw == bcrypt.hashpw(pw,dbpw):
				return True
		
		return False
	else:
		return None

#verify two-factor token
def verifyuser(email,token):
	db = DB()
	cur, status = db.query("select secret from Users where email=%s",(email,))
	row = cur.fetchone()

	if row == None:
		#should never happen
		print "Invalid user entered"
		return False
	else:
		#print otp.valid_totp(token, row['secret'])
		return otp.valid_totp(token, row['secret'])

#create poll
def createPoll(title, startDate, endDate):
    db = DB()
    cur, status = db.query("INSERT INTO polls(title, startDate, endDate, salt) VALUES (%s, %s, %s, SUBSTRING(MD5(RAND()), -16))", (title, startDate.strftime('%Y-%m-%d %H:%M:%S'), endDate.strftime('%Y-%m-%d %H:%M:%S')))

    if status == False:
        print "MySQL error"
        return "MySQL error"
    else:
        print "Poll successfully added"
        return True

#read poll salt
def readPollSalt(pollId):
    db = DB()
    cur, status = db.query("SELECT salt FROM polls WHERE Id='%s'", (pollId))
    row = cur.fetchone()

    if row == None:
        return False
    else:
        return row['salt']

#create option
def createOption(pollId, text):
    db = DB()
    cur, status = db.query("INSERT INTO options(pollId, num, text) VALUES (%s, %s, %s)", (pollId, numOptions(pollId), text))
	
    if status == False:
        print "MySQL error"
        return "MySQL error"
    else:
        print "Option successfully added"
        return True

#get options in poll
def numOptions(pollId):
    db = DB()
    cur, status = db.query("SELECT count(*) AS count FROM options WHERE pollId=%s", (pollId))
    return cur.fetchone()['count']+1

#create vote
def createVote(pollId, optionId, userId):
    db = DB()
    currentTime = datetime.now()
    if verifyVote(pollId, userId) == False:
        cur, status = db.query("INSERT INTO votes(pollId, optionId, userId, timestamp) VALUES (%s, %s, ENCRYPT(%s, %s), %s)", (pollId, optionId, userId, readPollSalt(pollId), currentTime.strftime('%Y-%m-%d %H:%M:%S')))
        if status == False:
            print "MySQL error"
            return "MySQL error"
        else:
            print "Vote successfully added"
            return True
    else:
        return False

#verify vote
def verifyVote(pollId, userId):
    db = DB()
    cryptUserId = crypt.crypt(str(userId), readPollSalt(pollId))
    cur, status = db.query("SELECT count(*) AS votecount FROM votes WHERE pollId=%s and userId=%s", (pollId, str(cryptUserId)))
    res = cur.fetchone()
    
    if res['votecount'] > 0:
        return True;
    else:
        return False;

#get polls
def getPolls():
    db = DB()
    cur, status = db.query("SELECT title, Id FROM polls", None)
    entries = cur.fetchall()
    return entries

#get poll
def getPoll(pollId):
    db = DB()
    cur, status = db.query("SELECT title FROM polls WHERE Id=%s", (pollId))
    poll = cur.fetchone()
    return poll

#get options
def getOptions(pollId):
    db = DB()
    cur, status = db.query("SELECT text, Id FROM options WHERE pollId=%s", (pollId))
    options = cur.fetchall()
    return options

#get poll results
def getPollResults(pollId):
    db = DB()
    cur, status = db.query("SELECT votesCount.count, o.num, o.text FROM (SELECT v.optionId, COUNT(v.optionId) AS count FROM votes v WHERE v.pollId=%s GROUP BY v.optionId) AS votesCount LEFT JOIN options o ON votesCount.optionId = o.Id", (pollId))
    entries = cur.fetchall()
    return entries

#get poll votes
def getPollHistory(pollId):
    db = DB()
    cur, status = db.query("SELECT o.num, v.userId, v.timestamp FROM votes v LEFT JOIN options o ON v.optionId = o.Id WHERE v.pollId=%s ORDER BY timestamp DESC", (pollId))
    entries = cur.fetchall()
    return entries
