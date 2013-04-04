import db, bcrypt, sys
from datetime import datetime

user = 'testuser10'
pw = 'testpw10'

hashpass = bcrypt.hashpw(pw, bcrypt.gensalt())
#print hashpass
print user, pw
db.createuser(user,hashpass)

'''
returnpw = db.getpwhash(user)

if returnpw == bcrypt.hashpw(pw,returnpw):
	print "Correct password entered"
else:
	print "Incorrect password entered"
'''
db.createPoll('What is the best ECE course?')
db.createOption(1, 'ECE 406')
db.createOption(1, 'ECE 458')
db.createOption(1, 'ECE 459')
db.createOption(1, 'Not ECE')
db.createPoll('100 duck sized horses or 1 horse sized duck?')
db.createOption(2, '100 ducked sized horses')
db.createOption(2, '1 horse sized duck')
