import MySQLdb
import onetimepass as otp
import sys, string, random, base64, bcrypt, qrcode

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
	
