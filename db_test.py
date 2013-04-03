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
db.createPoll('testPoll', datetime.now(), datetime.now())
db.createOption(1, 'option1')
db.createOption(1, 'option2')
db.createOption(1, 'option3')
db.createPoll('testPoll2', datetime.now(), datetime.now())
db.createOption(2, 'option1')
db.createOption(2, 'option2')
db.createOption(2, 'option3')
db.createVote(1, 1, 1)
db.createVote(1, 2, 2)
db.createVote(1, 1, 3)
db.createVote(1, 3, 4)
print db.verifyVote(1, 2)
