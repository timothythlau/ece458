import db, bcrypt, sys

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
db.verifyuser(user, sys.argv[1])
