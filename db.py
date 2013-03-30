import MySQLdb
import onetimepass as otp
import sys, string, random, base64

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

#create user and assign random secret for two-factor authentication
def createuser(email,pw):
	db = DB()
	
	cur, status = db.query("select email from Users where email=%s",(email,))
	
	if status == False:
		print "MySQL error"
		return False
	
	#check for duplicate users
	if cur.fetchone() != None:
		print "User exists already"
		return False
	
	#assign secret to user
	secret = base64.b32encode(''.join(random.choice(string.replace(string.ascii_uppercase + string.digits, '8', '')) for x in range(10)))
	cur, status = db.query("insert into Users(email,password,secret) values (%s,%s,%s)",(email,pw,secret))
	
	if status == False:
		print "MySQL error"
		return False
	else:
		print "User successfully added"
		return True

#get bcrypted password from DB to compare
def getpwhash(email):
	db = DB()
	cur, status = db.query("select password from Users where email=%s",(email,))
	
	if status == True:
		return cur.fetchone()['password']
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
		print otp.valid_totp(token, row['secret'])
		return True
	
